import asyncio

from ...common import create_logger
from ..chat_model_client import UsageMetadata
from ..config import AgentConfig
from ..state import AgentState  
from .prebuilt_workflow import PrebuiltWorkflow
from a2a.client import ClientConfig, ClientEvent, ClientFactory
from a2a.client.client import UpdateEvent
from a2a.types import AgentCard, Message, Task, TaskArtifactUpdateEvent, TaskStatusUpdateEvent, TaskState, Part
from a2a.utils.parts import get_text_parts, get_data_parts, get_file_parts
from httpx import AsyncClient
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from typing import Any, AsyncIterable, Callable, Dict, Literal, Optional, Sequence, Type
from typing_extensions import override



logger = create_logger(__name__, level="debug")
USAGE_METADATA_KEY = "usage"

class CallAgentNode(PrebuiltWorkflow):
    """Abstracts streaming communication between agents (e.g., Athena ↔ Hermes) as an internal mini-graph.
    
    Internal mini-graph flow:
        START → call → consume → router → (consume | cleanup) → END
    """
    
    def __init__(
        self,
        config: AgentConfig,
        StateType: Type[AgentState],
        loop_name: str,
        agent_name: str,
        build_message: Callable[[RunnableConfig, str], Message],
        *,
        input: str = "question",
        output: str = "answer",
        global_status: str = "status",
        agent_input_required: str = "agent_input",
        agent_status: str = "agent_status",
        agent_content: str = "agent_content",
        input_required: str = "input_required",
        recursion_limit: int = 50,
    ) -> None:
        """Initialize the CallAgentNode workflow.
        
        Args:
            config: Agent configuration.
            StateType: The state class type.
            loop_name: Name of this workflow loop.
            agent_card: Card of the target agent to call.
            build_message: Callback to build the request message.
            input: State field name for input text.
            output: State field name for output text.
            global_status: State field name for global status.
            agent_input_required: State field name indicating if agent needs input.
            agent_status: State field name for agent-specific status.
            agent_content: State field name for agent-specific content.
            input_required: State field name indicating if user input is required.
            recursion_limit: Max recursion depth for nested calls.
        """
        # Initialize PrebuiltWorkflow 
        super().__init__(
            config=config,
            StateType=StateType,
            loop_name=loop_name,
            agent_name=agent_name,
            build_message=build_message,
            input=input,
            output=output,
            global_status=global_status,
            agent_input_required=agent_input_required,
            agent_status=agent_status,
            agent_content=agent_content,
            input_required=input_required,
            recursion_limit=recursion_limit,
        )
        
        
    def _router(self, state: Type[AgentState]) -> Literal["consume_stream", "cleanup"]:
        """Route between consuming more stream data or cleaning up."""
        stream_done_val = self.stream_done 
        needs_input_val = bool(getattr(state, self.agent_input_required))

        return "cleanup" if stream_done_val or needs_input_val else "consume_stream"
    
    @override
    def _setup(
        self,
        loop_name: str,
        agent_name: str,
        build_message: Callable[[RunnableConfig, str], Message],
        *,
        input: str = "question",
        output: str = "answer",
        global_status: str = "status",
        agent_input_required: str = "agent_input",
        agent_status: str = "agent_status",
        agent_content: str = "agent_content",
        input_required: str = "input_required",
        recursion_limit: int = 50,
    ) -> None:
        """Set up the internal mini-graph with nodes and edges."""
        self._agent_name = agent_name
        self.input = input
        self.output = output
        self.global_status = global_status
        self.agent_input_required = agent_input_required
        self.agent_status = agent_status
        self.agent_content = agent_content
        self.input_required = input_required
        self._build_message = build_message
        self.recursion_limit = recursion_limit
        self.loop_name = loop_name
        
        self._agent_card = None  
        self.stream_done: bool = False
        self._queue: Optional[asyncio.Queue[Optional[tuple[str, str]]]] = None
        self._stream_task: Optional[asyncio.Task[None]] = None
        self._usage_buffer = UsageMetadata()

        self.graph_builder.add_node("call_agent", self._call_agent)
        self.graph_builder.add_node("consume_stream", self._consume_stream)
        self.graph_builder.add_node("cleanup", self._cleanup)

        self.graph_builder.add_edge(START, "call_agent")
        self.graph_builder.add_edge("call_agent", "consume_stream")
        self.graph_builder.add_conditional_edges("consume_stream", self._router)
        self.graph_builder.add_edge("cleanup", END)

    @override
    async def _astream(
        self,
        state: Type[AgentState],
        config: RunnableConfig,
    ) -> AsyncIterable[Type[AgentState]]:
        """Stream execution of the internal graph."""
        cfg: Dict[str, Any] = dict(config or {})

        if "recursion_limit" not in cfg or (isinstance(cfg["recursion_limit"], int) and cfg["recursion_limit"] < 200):
            cfg["recursion_limit"] = self.recursion_limit
            
        stream = self.graph.astream(state, cfg)

        async for item in stream:
            state_item = self.StateType.model_validate(item)
            yield state_item

    
    async def _call_agent(
        self,
        state: Type[AgentState],
        config: RunnableConfig,
    ) -> AsyncIterable[Type[AgentState]]:
        """Initial node: prepare and start the agent stream."""
        
        if self._agent_card is None:
            cards = await self.agent_config.list_agent_cards([self._agent_name])
            self._agent_card = cards[self._agent_name]
            
        # Reset dynamic fields
        self.stream_done = False
        setattr(state, self.agent_status, None)
        setattr(state, self.agent_content, None)
        setattr(state, self.agent_input_required, False)

        # Get input text
        text = getattr(state, self.input, "") or getattr(state, self.output, None) 
        if not isinstance(text, str):
            text = str(text)

        request = self._build_message(config, text)

        # Update global state
        setattr(state, self.global_status, "working")
        setattr(state, self.output, f"Forwarding request to {self.loop_name}…")
        setattr(state, self.input_required, False)

        # Start streaming worker
        await self._start_stream(request)

        yield state

    async def _consume_stream(
        self,
        state: Type[AgentState],
        config: RunnableConfig,
    ) -> AsyncIterable[Type[AgentState]]:
        """Consume one item from the stream queue and update state."""
        q = self._queue
        if q is None:
            # Nothing to consume: consider stream finished
            self.stream_done = True
            yield state
            return

        item = await q.get()

        # Sentinel: end of stream
        if item is None:
            self.stream_done = True
            await self._stop_stream()
            yield state
            return

        status, content = item

        # Update agent-specific fields
        setattr(state, self.agent_status, status)
        setattr(state, self.agent_content, content)

        # Update global fields
        setattr(state, self.global_status, status)
        if content:
            setattr(state, self.output, content)

        needs_input = (status == "input-required")
        setattr(state, self.agent_input_required, needs_input)
        setattr(state, self.input_required, needs_input)

        if needs_input:
            # If user input is required, stop the stream
            self.stream_done = True
            await self._stop_stream()

        yield state

    def _cleanup(self, state: Type[AgentState]) -> AgentState:
        """Final cleanup node (only an endpoint)."""
        return state

    # -------------------------------------------------------------------------
    # STREAM HELPERS
    # -------------------------------------------------------------------------
    async def _stop_stream(self) -> None:
        """Stop the streaming worker task and clear the queue."""
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        self._stream_task = None
        self._queue = None

    async def _start_stream(self, request: Message) -> None:
        """Start a background worker to consume the agent stream and populate the queue."""
        await self._stop_stream()

        q: asyncio.Queue[Optional[tuple[str, str]]] = asyncio.Queue()
        self._queue = q

        async def _worker():
            """Background worker that consumes agent stream and pushes items to queue."""
            try:
                async for item in self.consume_agent_stream(
                    agent_card=self._agent_card,
                    message=request,
                ):
                    status, content = self._map_stream_item(item)
                    status = status.value
                    await q.put((status, content))
                    logger.debug(f"Worker: put {(status, content)}")
                    if status in ("completed", "error", "input-required"):
                        break

            except Exception as e:
                await q.put(("error", f"AgentLoop stream error: {e}"))

            finally:
                # Sentinel: end of stream
                await q.put(None)

        self._stream_task = asyncio.create_task(_worker())



    @staticmethod
    def _parts_to_text(parts: Sequence[Part] | None) -> str:
        if not parts:
            return ""
        texts = get_text_parts(list(parts))
        if texts:
            return "\n\n".join(texts)
        datas = get_data_parts(list(parts))
        if datas:
            return str(datas)
        files = get_file_parts(list(parts))
        if files:
            return f"Length: {len(files)} files"
        return ""


    def _map_stream_item(self, item: ClientEvent | Message) -> tuple[TaskState, str]:
        """Map a stream item to (status, content) tuple.
        
        Args:
            item: Stream item from the agent (task update or message).
            
        Returns:
            Tuple of (status, content_text).
        """
        if (isinstance(item, Message)):
            return TaskState.completed, CallAgentNode._parts_to_text(item.parts)
        
        task: Task
        update: UpdateEvent | None
        task, update = item

        if isinstance(update, TaskArtifactUpdateEvent):
            artifact = update.artifact
            msg = CallAgentNode._parts_to_text(artifact.parts)
            return TaskState.completed, msg

        if isinstance(update, TaskStatusUpdateEvent):
            status_obj = update.status
            message = status_obj.message
            msg = CallAgentNode._parts_to_text(message.parts)
            st = status_obj.state

            return st, msg if st else (TaskState.working, msg)

        return TaskState.working, ""


    async def consume_agent_stream(
        self,
        agent_card: AgentCard,
        message: Message,
    ) -> AsyncIterable[ClientEvent | Message]:
        """Consume the agent stream from another A2A agent.
        
        Args:
            agent_card: The agent card of the target agent.
            message: The message to send to the agent.
        
        Yields:
            Stream items (events or messages) from the agent.
        """
        TIMEOUT = 120.0  # seconds
        client_factory = ClientFactory(
            ClientConfig(
                httpx_client=AsyncClient(timeout=TIMEOUT),
                streaming=True,
            )
        )
        client = client_factory.create(card=agent_card)
        stream = client.send_message(request=message)
        try:
            async for item in stream:
                # Track usage metadata
                if isinstance(item, Message):
                    metadata = item.metadata
                else:
                    event = item[1]
                    metadata = event.metadata if event else None

                if metadata and USAGE_METADATA_KEY in metadata:
                    usage = metadata[USAGE_METADATA_KEY]
                    self._usage_buffer += UsageMetadata.model_validate(usage)
                yield item

        except Exception as e:
            logger.error(f"consume_agent_stream: Streaming failed: {e}")
            raise
