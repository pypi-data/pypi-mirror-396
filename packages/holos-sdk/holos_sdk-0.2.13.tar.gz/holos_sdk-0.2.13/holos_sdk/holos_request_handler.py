import copy
import logging
import uuid
from collections.abc import AsyncGenerator
import asyncio
from a2a.utils import artifact
from a2a.utils.artifact import new_artifact
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContextBuilder
from a2a.server.context import ServerCallContext
from a2a.server.events import Event, QueueManager, EventQueue
from a2a.server.tasks import (
    PushNotificationConfigStore,
    PushNotificationSender,
    TaskStore,
)
from a2a.types import (
    Message,
    MessageSendParams,
    Task,
    TaskIdParams,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
)
from a2a.utils.errors import ServerError, TaskNotFoundError
from holos_sdk.utils import plan_to_message, try_convert_to_plan
from .plant_tracer import PlantTracer, no_op_tracer
from .types import Plan, Assignment, TaskArtifact

logger = logging.getLogger(__name__)


class HolosRequestHandler(DefaultRequestHandler):
    """
    Holos request handler that extends DefaultRequestHandler with tracing functionality.
    
    This handler adds tracing to:
    1. on_message_send - consumes incoming objects and traces results
    2. on_message_send_stream - consumes incoming objects, tries to convert to Plan, and traces all events
    """
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        task_store: TaskStore,
        queue_manager: QueueManager | None = None,
        push_config_store: PushNotificationConfigStore | None = None,
        push_sender: PushNotificationSender | None = None,
        request_context_builder: RequestContextBuilder | None = None,
        tracer: PlantTracer = no_op_tracer,
    ) -> None:
        """
        Initialize the Holos request handler.
        
        Args:
            agent_executor: The AgentExecutor instance to run agent logic
            task_store: The TaskStore instance to manage task persistence
            queue_manager: The QueueManager instance to manage event queues
            push_config_store: The PushNotificationConfigStore instance for managing push notification configurations
            push_sender: The PushNotificationSender instance for sending push notifications
            request_context_builder: The RequestContextBuilder instance used to build request contexts
            tracer: PlantTracer instance for submitting tracing data
        """
        super().__init__(
            agent_executor=agent_executor,
            task_store=task_store,
            queue_manager=queue_manager,
            push_config_store=push_config_store,
            push_sender=push_sender,
            request_context_builder=request_context_builder,
        )
        self._tracer = tracer
        self._task_event_history = {}
        self._message_event_history = {}

    def _ensure_tracer_in_context(self, context: ServerCallContext | None = None) -> ServerCallContext:
        """
        Ensure the tracer is available in the context.
        
        Creates a request-scoped copy of the tracer to prevent race conditions
        when handling multiple concurrent requests. Each request gets its own
        tracer instance with isolated state (consumed_objects, produced_objects).
        
        If context is provided, add the request-scoped tracer to its state.
        If context is None, create a new ServerCallContext with the request-scoped tracer.
        
        Args:
            context: The server call context (can be None)
            
        Returns:
            ServerCallContext with request-scoped tracer in state
        """
        # Create a request-scoped copy to prevent race conditions
        request_tracer = self._tracer.create_request_scoped_copy()
        
        if context is not None:
            context.state['tracer'] = request_tracer
            return context
        else:
            return ServerCallContext(state={'tracer': request_tracer})

    @staticmethod
    def _create_event_copy(event: Event) -> Event:
        try:
            return copy.deepcopy(event)
        except (TypeError, AttributeError) as e:
            logger.warning(f"Could not create copy of event {type(event)}: {e}, storing reference (may be mutable)")
            return event

    async def _trace_event(self, event: Event, tracer: PlantTracer) -> None:
        """
        Trace an event using the provided tracer.
        
        Args:
            event: The event to trace
            tracer: The request-scoped tracer to use for tracing
        """
        try:
            if isinstance(event, (Message, Task, TaskArtifact, TaskStatusUpdateEvent)):
                await tracer.submit_object_produced(event)
            elif isinstance(event, Assignment):
                await tracer.submit_object_produced_consumed(event)
            elif isinstance(event, TaskArtifactUpdateEvent):
                #Only submit a full artifact instead of a chunked artifact
                task = await self.task_store.get(event.task_id)
                if (event.last_chunk is None or event.last_chunk == True) and task.artifacts:
                    for artifact in task.artifacts:
                        if artifact.artifact_id == event.artifact.artifact_id:
                            task_artifact = TaskArtifact(
                                artifact=artifact,
                                context_id=event.context_id,
                                task_id=event.task_id,
                            )
                            await tracer.submit_object_produced(task_artifact)
                            break
            #No need to submit plan, the client will submit it
            # elif isinstance(event, Plan):
            #     tracer.submit_object_produced(event)
        
        except Exception as e:
            logger.error(f"Error in _trace_event: {e}", exc_info=True)

    async def _process_stream_event(
        self,
        event: Event,
        request_tracer: PlantTracer,
        responsed_context_id: str | None,
        responsed_task_id: str | None,
    ) -> tuple[Event, str | None, str | None]:
        """
        Process an event from the stream: convert Plan to TaskArtifact, add metadata, trace, and update history.
        
        Args:
            event: The event to process
            request_tracer: The request-scoped tracer to use for tracing
            responsed_context_id: Current context ID (may be updated if event is a Task)
            responsed_task_id: Current task ID (may be updated if event is a Task)
            
        Returns:
            Tuple of (processed_event, updated_responsed_context_id, updated_responsed_task_id)
        """
        if isinstance(event, Plan):
            plan_message = plan_to_message(event)
            task_artifact = TaskArtifact(
                artifact=new_artifact(plan_message.parts, name="plan_message"),
                context_id=responsed_context_id,
                task_id=responsed_task_id,
                metadata=event.metadata,
            )
            event = task_artifact
        
        logger.debug(f"Got event: {event} of type {type(event)}")

        if hasattr(event, 'metadata'):
            if event.metadata is None:
                event.metadata = {}
            event.metadata['event_id'] = str(uuid.uuid4())
        await self._trace_event(event, request_tracer)

        if isinstance(event, Task):
            responsed_task_id = event.id
            responsed_context_id = event.context_id
        
        return event, responsed_context_id, responsed_task_id

    async def _consume_event_stream_in_background(self, event_stream: AsyncGenerator[Event, None], output_event_queue: EventQueue, request_tracer: PlantTracer,) -> None:
        responsed_context_id, responsed_task_id = None, None
        try:
            async for event in event_stream:
                event, responsed_context_id, responsed_task_id = await self._process_stream_event(
                    event, request_tracer, responsed_context_id, responsed_task_id
                )

                if responsed_task_id:
                    event_copy = self._create_event_copy(event)
                    if responsed_task_id not in self._task_event_history:
                        self._task_event_history[responsed_task_id] = { "events": [], "process_status": "running", }
                        logger.debug(f"Created new event history for task {responsed_task_id}")
                    self._task_event_history[responsed_task_id]["events"].append(event_copy)
                
                await output_event_queue.enqueue_event(event)
        except Exception as e:
            logger.error(f"Error in _consume_event_stream_in_background: {e}", exc_info=True)
        finally:
            await output_event_queue.enqueue_event(None)
            if responsed_task_id and responsed_task_id in self._task_event_history:
                self._task_event_history[responsed_task_id]["process_status"] = "stopped"

    
    async def on_message_send(self, params: MessageSendParams, context: ServerCallContext | None = None,) -> Message | Task:
        """
        Handle message send with tracing.
        
        This follows the server-side pattern where we consume the incoming request
        object before processing (opposite of client-side which produces before sending).
        """
        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        
        result = await super().on_message_send(params, context)
        await self._trace_event(result, request_tracer)
        
        return result
    
    async def on_message_send_stream(self, params: MessageSendParams, context: ServerCallContext | None = None) -> AsyncGenerator[Event]:
        """
        Handle message send stream with tracing.
        
        This follows the server-side pattern:
        1. Consume the incoming request object (server-side receives)
        2. Try to convert to Plan and resubmit if successful (following client-side pattern)
        
        Uses a queue-based approach where:
        - A background task consumes the event_stream, processes events, and puts them into a queue
        - Events are also added to _task_event_history by the background task for resubscription
        - This generator reads from the event queue and yields events
        """

        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        plan = try_convert_to_plan(params.message)
        if plan:
            plans_to_submit = [plan]
            submitted_plans = set()
            while plans_to_submit:
                cur_plan = plans_to_submit.pop(0)
                if cur_plan.id in submitted_plans:
                    continue
                await request_tracer.submit_object_consumed(cur_plan)
                submitted_plans.add(cur_plan.id)
                plans_to_submit.extend(cur_plan.depend_plans)

        event_queue = EventQueue()
        
        background_task = asyncio.create_task(
            self._consume_event_stream_in_background(
                super().on_message_send_stream(params, context),
                event_queue,
                request_tracer,
            )
        )
        logger.debug(f"Started background task {background_task.get_name()} to consume event stream and add to history")

        try:
            while True:
                event = await event_queue.dequeue_event()
                if event is None:
                    break
                
                if isinstance(event, Event):
                    yield event
                event_queue.task_done()
                
        except Exception as e:
            logger.error(f"Error in on_message_send_stream: {e}", exc_info=True)
            raise


    async def on_resubscribe_to_task(self, params: TaskIdParams, context: ServerCallContext | None = None) -> AsyncGenerator[Event]:
        """Default handler for 'tasks/resubscribe'.

        Allows a client to re-attach to a running streaming task's event stream.
        Requires the task and its queue to still be active.
        """
        task_id = params.id
        last_event_id = params.metadata.get('last_event_id', None) if params.metadata else None
        
        logger.info(f"Resubscribe request received for task_id: {task_id}, last_event_id: {last_event_id}")
        
        if task_id in self._task_event_history:
            task_history = self._task_event_history[task_id]
            total_events = len(task_history["events"])
            process_status = task_history["process_status"]
            
            logger.info(f"Task {task_id} found in event history. Total events: {total_events}, process_status: {process_status}")
            
            last_index = total_events
            if last_event_id == "HEAD":
                last_index = -1
                logger.debug(f"Resubscribing from HEAD (all events) for task {task_id}")
            elif last_event_id:
                logger.debug(f"Searching for event with event_id: {last_event_id} in task {task_id}")
                found = False
                for i, event in enumerate(task_history["events"]):
                    if hasattr(event, 'metadata') and event.metadata is not None and event.metadata.get('event_id') == last_event_id:
                        last_index = i
                        found = True
                        logger.debug(f"Found event with event_id {last_event_id} at index {i} for task {task_id}")
                        break
                if not found:
                    logger.warning(f"Event with event_id {last_event_id} not found for task {task_id}, starting from last")
            else:
                logger.debug(f"No last_event_id provided for task {task_id}, starting from beginning")
            
            events_yielded = 0
            while True:
                events_in_iteration = 0
                for i in range(last_index + 1, len(task_history["events"])):
                    logger.debug(f"Yielding event {i}: {task_history['events'][i].model_dump(mode='json', exclude_none=True)}")
                    if isinstance(task_history["events"][i], Event):
                        yield task_history["events"][i]
                    last_index = i
                    events_in_iteration += 1
                    events_yielded += 1
                
                if events_in_iteration > 0:
                    logger.debug(f"Yielded {events_in_iteration} events for task {task_id} (total yielded: {events_yielded})")
                
                if task_history["process_status"] == "stopped":
                    logger.info(f"Task {task_id} process status is stopped. Total events yielded: {events_yielded}")
                    break
                
                await asyncio.sleep(0.1)
        else:
            logger.error(f"Task {task_id} not found in event history. Available tasks: {list(self._task_event_history.keys())}")
            raise ServerError(error=TaskNotFoundError())
