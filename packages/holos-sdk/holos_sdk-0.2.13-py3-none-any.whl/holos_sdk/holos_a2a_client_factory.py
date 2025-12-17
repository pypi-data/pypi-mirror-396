from a2a.client.client_factory import ClientFactory
from a2a.types import AgentCard
from typing import Optional, List

from holos_sdk.utils import logger
from .plant_tracer import PlantTracer, no_op_tracer
from .holos_a2a_client import HolosTracingA2AClient


class HolosA2AClientFactory(ClientFactory):
    """
    A ClientFactory that automatically adds tracing functionality to A2A clients.
    
    This factory wraps the client with HolosTracingA2AClient for both request and response tracing:
    1. send_message - submits produced before sending, consumed after receiving
    2. resubscribe - submits consumed for message/task objects, ignores A2A events
    3. send_plan_streaming - submits plan as produced, converts to message and calls send_message
    """
    
    def __init__(self, config, consumers=None, tracer: Optional[PlantTracer] = None):
        """
        Initialize the HolosA2AClientFactory.
        
        Args:
            config: ClientConfig for the factory
            consumers: List of consumers for the clients
            tracer: PlantTracer instance for submitting tracing data
        """
        super().__init__(config, consumers)
        self.tracer = tracer or no_op_tracer
    
    def create(
        self,
        card: AgentCard,
        consumers: Optional[List] = None,
        interceptors: Optional[List] = None,
    ) -> HolosTracingA2AClient:
        """
        Create a new A2A client with automatic tracing.
        
        Args:
            card: An AgentCard defining the characteristics of the agent.
            consumers: A list of Consumer methods to pass responses to.
            interceptors: A list of interceptors to use for each request.
            
        Returns:
            A HolosTracingA2AClient with request and response tracing.
        """

        logger.info(f"create client config: {self._config}")
        base_client = super().create(card, consumers, interceptors)
        
        # Wrap with HolosTracingA2AClient for both request and response tracing
        return HolosTracingA2AClient(base_client, self.tracer)

