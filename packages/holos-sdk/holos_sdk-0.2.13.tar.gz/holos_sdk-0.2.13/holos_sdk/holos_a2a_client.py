"""
HolosTracingA2AClient - A client wrapper that adds response tracing to A2A clients.
"""

import logging
from collections.abc import AsyncIterator
from typing import Optional
from a2a.client.base_client import BaseClient
from a2a.client.client import Client, ClientCallContext, ClientEvent
from a2a.types import Message, Task, TaskQueryParams, TaskIdParams, TaskPushNotificationConfig, GetTaskPushNotificationConfigParams, AgentCard, TaskArtifactUpdateEvent, TaskStatusUpdateEvent
from .plant_tracer import PlantTracer
from .types import Plan, TaskArtifact, Assignment
from .utils import plan_to_message

logger = logging.getLogger(__name__)


class HolosTracingA2AClient(Client):
    """
    A client wrapper that adds request and response tracing to A2A clients.
    
    This client handles both request and response tracing for:
    1. send_message - submits produced object before sending, consumed object after receiving response
    2. resubscribe - submits consumed object for message/task objects, ignores A2A events
    3. send_plan_streaming - submits plan as produced, converts to message and calls send_message
    """

    def __init__(self, base_client: BaseClient, tracer: PlantTracer):
        """
        Initialize the tracing client.
        
        Args:
            base_client: The underlying BaseClient instance
            tracer: PlantTracer instance for submitting tracing data, may be the no_op_tracer
        """
        super().__init__(base_client._consumers, base_client._middleware)
        self._base_client = base_client
        self._tracer = tracer
        self._card = base_client._card
        self._config = base_client._config
        self._transport = base_client._transport


    @staticmethod
    def _extract_event_id(response: ClientEvent | Message | tuple) -> str | None:
        """
        Extract event_id from a response object.
        
        Handles different response types:
        - Tuple (response_task, response_event): checks response_event first, then response_task
        - Direct response object: checks response.metadata['event_id']
        
        Args:
            response: The response object to extract event_id from
            
        Returns:
            The event_id string if found, None otherwise
        """
        if isinstance(response, tuple):
            response_task, response_event = response
            if response_event is not None:
                if hasattr(response_event, 'metadata') and response_event.metadata is not None and 'event_id' in response_event.metadata:
                    return response_event.metadata['event_id']
            if hasattr(response_task, 'metadata') and response_task.metadata is not None and 'event_id' in response_task.metadata:
                return response_task.metadata['event_id']
        elif hasattr(response, 'metadata') and response.metadata is not None and 'event_id' in response.metadata:
            return response.metadata['event_id']
        return None

    async def _read_response_from_event_stream(self, event_stream: AsyncIterator[ClientEvent | Message], local_tracer: PlantTracer, from_objects = None) -> AsyncIterator[ClientEvent | Message]:
        async for response in event_stream:
            if isinstance(response, Message):
                await local_tracer.submit_object_consumed(response, from_objects=from_objects)
            elif isinstance(response, tuple):
                response_task, response_event = response
                if response_event is None:
                    await local_tracer.submit_object_consumed(response_task, from_objects=from_objects)
                elif isinstance(response_event, TaskArtifactUpdateEvent):
                    #Only submit a full artifact instead of a chunked artifact
                    if response_event.last_chunk is None or response_event.last_chunk == True:
                        for artifact in response_task.artifacts:
                            if artifact.artifact_id == response_event.artifact.artifact_id:
                                task_artifact = TaskArtifact(
                                    artifact=artifact,
                                    context_id=response_event.context_id,
                                    task_id=response_event.task_id,
                                )
                                await local_tracer.submit_object_consumed(task_artifact, from_objects=from_objects)
                                break
                else:
                    #currently only TaskStatusUpdateEvent will come to here
                    await local_tracer.submit_object_consumed(response_event, from_objects=from_objects)
            yield response

    async def send_message(self, request: Message, *, context: ClientCallContext | None = None, from_objects = None) -> AsyncIterator[ClientEvent | Message]:
        await self._tracer.submit_object_produced(request, from_objects)
        assignment = Assignment(context_id=request.context_id, object_id=request.message_id, object_kind=request.kind, assignee_id=self._card.url, assignee_name=self._card.name)
        await self._tracer.submit_object_produced_consumed(assignment)

        event_stream = self._base_client.send_message(request, context=context)

        local_from_objects = (from_objects or []) + [request.message_id]
        local_tracer = self._tracer.create_request_scoped_copy()
        async for response in self._read_response_from_event_stream(event_stream, local_tracer, local_from_objects):
            yield response


    async def resubscribe(self, request: TaskIdParams, *, context: ClientCallContext | None = None,) -> AsyncIterator[ClientEvent]:
        #To fix the design bug of a2a-sdk tracer(when artifacts return with append mode), we have to manually handle the response
        #Currently the resubscribe may have a small chance to lose tracing relations since we don't know the original message
        should_yield = True
        last_event_id = None
        if hasattr(request, 'metadata') and request.metadata is not None and 'last_event_id' in request.metadata:
            last_event_id = request.metadata['last_event_id']
            request.metadata['last_event_id'] = "HEAD"
            if last_event_id != "HEAD":
                should_yield = False

        local_tracer = self._tracer.create_request_scoped_copy()
        event_stream = self._base_client.resubscribe(request, context=context)
        async for response in self._read_response_from_event_stream(event_stream, local_tracer):
            event_id = self._extract_event_id(response)
            if event_id is None:
                should_yield = True

            if should_yield:
                yield response

            if event_id == last_event_id:
                should_yield = True
    

    async def send_plan_streaming( self, plan: Plan, context: Optional[ClientCallContext] = None, from_objects = None) -> AsyncIterator[ClientEvent | Message]:
        """
        Send a plan using streaming and submit tracing data.
        
        This function is specifically for planning agents:
        1. Submits the plan as produced
        2. Converts plan to message and calls send_message
        3. send_message will handle its own tracing for the converted message
        
        Args:
            plan: The Plan object to send
            context: Optional client call context
            
        Returns:
            The result from send_message (which will be streaming)
        """
        try:
            plans_to_submit = [plan]
            submitted_plans = set()
            while plans_to_submit:
                cur_plan = plans_to_submit.pop(0)
                if cur_plan.id in submitted_plans:
                    continue
                await self._tracer.submit_object_produced(cur_plan, from_objects)
                submitted_plans.add(cur_plan.id)
                plans_to_submit.extend(cur_plan.depend_plans)

            message = plan_to_message(plan)
            message_from_objects = [plan.id]
            async for response in self.send_message(message, context=context, from_objects=message_from_objects):
                yield response
        except Exception as e:
            logger.error(f"Error in send_plan_streaming: {e}")
            raise
    

    #--- just call base client

    async def get_task( self, request: TaskQueryParams, *, context: ClientCallContext | None = None,) -> Task:
        return await self._base_client.get_task(request, context=context)
    
    async def cancel_task( self, request: TaskIdParams, *, context: ClientCallContext | None = None,) -> Task:
        return await self._base_client.cancel_task(request, context=context)
    
    async def set_task_callback( self, request: TaskPushNotificationConfig, *, context: ClientCallContext | None = None,) -> TaskPushNotificationConfig:
        return await self._base_client.set_task_callback(request, context=context)
    
    async def get_task_callback( self, request: GetTaskPushNotificationConfigParams, *, context: ClientCallContext | None = None,) -> TaskPushNotificationConfig:
        return await self._base_client.get_task_callback(request, context=context)
    
    async def get_card( self, *, context: ClientCallContext | None = None) -> AgentCard:
        return await self._base_client.get_card(context=context)
    
    async def close(self) -> None:
        await self._base_client.close()
