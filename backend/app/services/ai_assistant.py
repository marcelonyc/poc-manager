"""AI Assistant service using LlamaIndex with Ollama and MCP tools.

The assistant ONLY operates when MCP tools are available. All responses
must be grounded in data retrieved through MCP tool calls — direct LLM
generation without tools is never allowed.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from app.config import settings

logger = logging.getLogger(__name__)

# Error returned when the MCP tool pipeline is unavailable
_MCP_UNAVAILABLE_MSG = (
    "The AI Assistant requires MCP tools to operate but they are not available. "
    "Please verify that MCP_TOOLS is configured and that the required packages "
    "(llama-index-tools-mcp, mcp) are installed."
)

# Returned when the agent answered without calling any tool (hallucination guard)
_NO_TOOL_CALL_MSG = (
    "I was unable to retrieve the information you requested because I could "
    "not fetch data from the system. I can only provide answers based on "
    "actual data retrieved through the platform. "
    "Please try rephrasing your question."
)


def _patch_tool_tracking(tool: Any, tracker: dict) -> None:
    """Monkey-patch a tool's call/acall to record that it was invoked."""
    original_acall = tool.acall
    original_call = tool.call

    async def _tracked_acall(*args: Any, **kwargs: Any) -> Any:
        tracker["called"] = True
        return await original_acall(*args, **kwargs)

    def _tracked_call(*args: Any, **kwargs: Any) -> Any:
        tracker["called"] = True
        return original_call(*args, **kwargs)

    tool.acall = _tracked_acall
    tool.call = _tracked_call


# In-memory chat session store (keyed by session_id)
_chat_sessions: Dict[str, dict] = {}

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 10


def _get_mcp_tool_names() -> List[str]:
    """Get the list of allowed MCP tool names from environment variable."""
    tools_str = settings.MCP_TOOLS.strip()
    if not tools_str:
        return []
    return [t.strip() for t in tools_str.split(",") if t.strip()]


def _cleanup_expired_sessions():
    """Remove sessions that have timed out."""
    now = datetime.utcnow()
    expired = [
        sid
        for sid, session in _chat_sessions.items()
        if now - session["last_activity"]
        > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ]
    for sid in expired:
        del _chat_sessions[sid]


def get_or_create_session(
    session_id: Optional[str],
    user_id: int,
    tenant_id: int,
) -> dict:
    """Get an existing session or create a new one."""
    _cleanup_expired_sessions()

    if session_id and session_id in _chat_sessions:
        session = _chat_sessions[session_id]
        # Verify session belongs to same user and tenant
        if session["user_id"] == user_id and session["tenant_id"] == tenant_id:
            session["last_activity"] = datetime.utcnow()
            return session

    # Create new session
    new_id = str(uuid.uuid4())
    session = {
        "session_id": new_id,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "messages": [],
    }
    _chat_sessions[new_id] = session
    return session


def close_session(session_id: str) -> bool:
    """Close and remove a chat session."""
    if session_id in _chat_sessions:
        del _chat_sessions[session_id]
        return True
    return False


def reset_session(
    session_id: Optional[str], user_id: int, tenant_id: int
) -> dict:
    """Reset a chat session by closing the existing one and creating a new one."""
    if session_id:
        close_session(session_id)
    return get_or_create_session(
        session_id=None, user_id=user_id, tenant_id=tenant_id
    )


def is_mcp_configured() -> bool:
    """Return True when MCP tools are configured and ready to use."""
    return bool(_get_mcp_tool_names())


async def chat_with_assistant(
    session: dict,
    user_message: str,
    ollama_api_key: str,
    user_token: str,
) -> str:
    """Send a message to the AI assistant and get a response.

    Uses LlamaIndex with Ollama as the LLM and MCP tools from the local
    server.  The user's auth token is forwarded to MCP tools so that every
    data request respects the caller's RBAC permissions.

    Raises immediately when MCP tools are not configured — the assistant
    never falls back to a plain LLM without tools.
    """
    # ── Gate: MCP tools are mandatory ──────────────────────────────────
    mcp_tool_names = _get_mcp_tool_names()
    if not mcp_tool_names:
        logger.error("MCP_TOOLS is empty — chat request rejected")
        return _MCP_UNAVAILABLE_MSG

    try:
        from llama_index.llms.ollama import Ollama
        from llama_index.core.llms import ChatMessage, MessageRole
    except ImportError:
        logger.error("llama-index-llms-ollama not installed")
        return _MCP_UNAVAILABLE_MSG

    # Record user message
    session["messages"].append(
        {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow(),
        }
    )

    # ── System prompt ──────────────────────────────────────────────────
    # The tool catalog is appended dynamically inside _run_with_mcp_tools.
    system_prompt = (
        "You are an AI assistant for POC (Proof of Concept) Manager. "
        "You help users retrieve and understand information about their POCs.\n\n"
        "CRITICAL INSTRUCTIONS — follow every one without exception:\n"
        "1. LANGUAGE: Detect the language the user writes in and ALWAYS "
        "reply in that SAME language. If the user writes in Spanish, reply "
        "in Spanish; if in French, reply in French; and so on.\n"
        "2. TOOL-ONLY DATA: You MUST call the available tools to obtain "
        "data before answering. NEVER generate, guess, or fabricate data "
        "on your own. Every factual claim in your response must come from "
        "a tool result.\n"
        "3. NO TOOL LEAKS: NEVER mention tool names, function signatures, "
        "parameter JSON, or internal environment details in your response.\n"
        "4. SUMMARISE RESULTS: After a tool returns data, present it in "
        "clear, user-friendly language. Do NOT dump raw JSON.\n"
        "5. MULTIPLE CALLS: A question may require several tool calls. "
        "Always call as many tools as needed — do not stop early.\n"
        "6. NO IDENTITY QUESTIONS: Never ask the user for identity, "
        "tenant, or login information — that context is part of the session.\n"
        "7. TOOL LIST: You may ONLY use tools from the AVAILABLE TOOLS "
        "list below. Do NOT invent or guess tool names.\n"
        "8. LIMITS: If no tool can answer the question, clearly tell the "
        "user you cannot help with that request and explain what kind of "
        "questions you CAN answer.\n"
        "9. MANDATORY TOOL USE: You MUST call at least one tool before "
        "producing any answer that contains names, lists, numbers, dates, "
        "statuses, or any other factual content. If you do not have a tool "
        "result, respond ONLY with: 'I don't have the information to answer "
        "that question.'\n"
        "10. ZERO FABRICATION: Do NOT invent names, email addresses, "
        "counts, percentages, or any data point. Even a single made-up "
        "value is a critical violation.\n"
    )

    chat_history = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
    ]

    # Add conversation history (last 20 messages to keep context manageable)
    for msg in session["messages"][-20:]:
        role = (
            MessageRole.USER
            if msg["role"] == "user"
            else MessageRole.ASSISTANT
        )
        chat_history.append(ChatMessage(role=role, content=msg["content"]))

    # ── Initialise Ollama LLM ──────────────────────────────────────────
    from ollama import Client as OllamaClient, AsyncClient as OllamaAsyncClient

    client_kwargs: dict = {
        "host": settings.OLLAMA_BASE_URL,
        "timeout": 120.0,
    }
    if ollama_api_key:
        client_kwargs["headers"] = {
            "Authorization": f"Bearer {ollama_api_key}"
        }

    llm = Ollama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        request_timeout=120.0,
        client=OllamaClient(**client_kwargs),
        thinking=True,
        async_client=OllamaAsyncClient(**client_kwargs),
    )

    # ── Run with MCP tools (the only allowed path) ─────────────────────
    try:
        response_text = await _run_with_mcp_tools(
            llm, chat_history, user_token, mcp_tool_names
        )
    except BaseException as e:
        # Log sub-exceptions from ExceptionGroups for diagnostics
        sub_excs = getattr(e, "exceptions", None)
        if sub_excs:
            logger.error(
                "LLM/MCP chat error (%s) with %d sub-exception(s):",
                type(e).__name__,
                len(sub_excs),
            )
            for i, sub in enumerate(sub_excs):
                logger.error("  [%d] %s: %s", i + 1, type(sub).__name__, sub)
        else:
            logger.error("LLM/MCP chat error: %s", e)
        response_text = (
            "I'm sorry, I encountered an error processing your request. "
            f"Please check that the Ollama service is running and the "
            f"model '{settings.OLLAMA_MODEL}' is available."
        )

    # Record assistant message
    session["messages"].append(
        {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow(),
        }
    )
    session["last_activity"] = datetime.utcnow()

    return response_text


async def _run_with_mcp_tools(
    llm: Any,
    chat_history: list,
    user_token: str,
    tool_names: List[str],
) -> str:
    """Open an MCP session, load tools, and run the agent.

    The MCP session must stay open for the entire agent interaction so
    that tools can be called.  If tools cannot be loaded for any reason
    this function raises instead of silently falling back to a plain LLM.

    NOTE: The ``streamable_http_client`` context manager uses an internal
    ``anyio.TaskGroup`` whose background tasks may fail during cleanup
    after the agent has already finished.  We therefore capture the agent
    result *before* the context managers exit and tolerate
    ``ExceptionGroup`` / ``BaseExceptionGroup`` errors that occur only
    during teardown.
    """
    try:
        from llama_index.tools.mcp import McpToolSpec
        from mcp.client.streamable_http import streamable_http_client
        from mcp import ClientSession
        import httpx
    except ImportError as exc:
        raise RuntimeError(
            "Required MCP packages are not installed "
            "(llama-index-tools-mcp, mcp)"
        ) from exc

    mcp_url = "http://localhost:8000/mcp"

    # Capture the agent result so it survives context-manager teardown
    # errors from the MCP streaming transport's internal TaskGroup.
    agent_result: Optional[str] = None

    try:
        # Use generous timeouts — the default httpx 5-second read
        # timeout is far too aggressive for SSE streams and causes
        # the background reader task to disconnect/reconnect in a
        # loop, eventually failing and crashing the TaskGroup.
        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=httpx.Timeout(
                connect=30.0, read=300.0, write=30.0, pool=30.0
            ),
        ) as http_client, streamable_http_client(
            url=mcp_url,
            http_client=http_client,
        ) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as mcp_session:
                await mcp_session.initialize()

                mcp_tool_spec = McpToolSpec(
                    client=mcp_session,
                    allowed_tools=tool_names if tool_names else None,
                )

                tools = list(await mcp_tool_spec.to_tool_list_async())
                if not tools:
                    raise RuntimeError(
                        "MCP session opened but no tools were loaded. "
                        "Verify that MCP_TOOLS names match the server."
                    )

                # Build an explicit tool catalog for the system prompt
                tool_catalog_lines = []
                for t in tools:
                    meta = t.metadata
                    desc = (meta.description or "").split("\n")[0]
                    tool_catalog_lines.append(f"  - {meta.name}: {desc}")
                tool_catalog = "\n".join(tool_catalog_lines)

                # Inject tool catalog into the system message
                from llama_index.core.llms import ChatMessage, MessageRole

                for i, msg in enumerate(chat_history):
                    if msg.role == MessageRole.SYSTEM:
                        chat_history[i] = ChatMessage(
                            role=MessageRole.SYSTEM,
                            content=(
                                msg.content
                                + f"\nAVAILABLE TOOLS (use ONLY these):\n"
                                f"{tool_catalog}\n"
                            ),
                        )
                        break

                # Store result BEFORE exiting context managers.
                # Wrap in its own try/except so that ExceptionGroups
                # raised by the agent workflow's internal TaskGroup
                # (e.g. from the SSE reader being cancelled) do not
                # prevent us from capturing a successfully-produced
                # response.
                try:
                    agent_result = await _agent_chat(llm, tools, chat_history)
                except BaseException as agent_exc:
                    _agent_sub = getattr(agent_exc, "exceptions", None)
                    if _agent_sub is not None:
                        logger.warning(
                            "Agent raised %s with %d sub-exception(s):",
                            type(agent_exc).__name__,
                            len(_agent_sub),
                        )
                        for idx, sub in enumerate(_agent_sub):
                            logger.warning(
                                "  [%d] %s: %s",
                                idx + 1,
                                type(sub).__name__,
                                sub,
                            )
                    # Re-raise; the outer handler will deal with it.
                    raise
    except BaseException as exc:
        # The streamable_http_client's internal TaskGroup can raise an
        # ExceptionGroup during teardown even when the agent completed
        # successfully.  If we already have a response, log and return it.
        _is_eg = getattr(exc, "exceptions", None) is not None
        _is_taskgroup_cleanup = (
            _is_eg
            or "TaskGroup" in str(exc)
            or type(exc).__name__ in ("ExceptionGroup", "BaseExceptionGroup")
        )
        if agent_result is not None and _is_taskgroup_cleanup:
            logger.warning(
                "MCP session cleanup raised %s (agent response was "
                "already obtained — ignoring): %s",
                type(exc).__name__,
                exc,
            )
            return agent_result
        # Genuine error — propagate
        raise

    return agent_result


async def _agent_chat(llm: Any, tools: list, chat_history: list) -> str:
    """Run an agent chat with MCP tools.  Never falls back to plain LLM.

    Tracks whether any tool was actually invoked during the interaction.
    If the agent produces a response without a single tool call it is
    treated as hallucinated and replaced with a safe refusal message.
    """
    from llama_index.core.agent import ReActAgent

    # ── Track real tool invocations ────────────────────────────────────
    call_tracker: dict = {"called": False}
    for tool in tools:
        _patch_tool_tracking(tool, call_tracker)

    # Extract system prompt from chat history
    agent_system_prompt = None
    for msg in chat_history:
        if msg.role.value == "system":
            agent_system_prompt = msg.content
            break

    agent = ReActAgent(
        tools=tools,
        llm=llm,
        verbose=False,
        system_prompt=agent_system_prompt,
        timeout=120.0,
    )

    # Build prompt from chat history (last user message)
    user_messages = [m for m in chat_history if m.role.value == "user"]
    if not user_messages:
        return "I didn't receive a message to respond to."

    last_user_msg = user_messages[-1].content

    # Provide conversation context
    context_parts = []
    for msg in chat_history[1:-1]:  # Skip system prompt and last user message
        prefix = "User" if msg.role.value == "user" else "Assistant"
        context_parts.append(f"{prefix}: {msg.content}")

    if context_parts:
        full_prompt = (
            "Previous conversation:\n"
            + "\n".join(context_parts[-10:])
            + f"\n\nCurrent question: {last_user_msg}"
        )
    else:
        full_prompt = last_user_msg

    handler = agent.run(user_msg=full_prompt)

    try:
        result = await handler
    except BaseException as exc:
        # The ReActAgent's workflow can raise an ExceptionGroup when
        # its internal TaskGroup is cancelled (e.g. by the MCP
        # transport's SSE reader failing).  Log the sub-exceptions
        # for diagnostics and re-raise.
        _sub = getattr(exc, "exceptions", None)
        if _sub is not None:
            logger.warning(
                "await handler raised %s with %d sub-exception(s):",
                type(exc).__name__,
                len(_sub),
            )
            for idx, sub in enumerate(_sub):
                logger.warning(
                    "  [%d] %s: %s", idx + 1, type(sub).__name__, sub
                )
        raise

    response_text = str(result.response.content)

    # ── GUARDRAIL: block responses not backed by a tool call ───────────
    if not call_tracker["called"]:
        logger.warning(
            "Agent responded without calling any tool — "
            "blocking potentially hallucinated response: %s",
            response_text[:200],
        )
        return _NO_TOOL_CALL_MSG

    return response_text
