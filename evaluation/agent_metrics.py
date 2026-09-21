from langchain_core.messages import ToolMessage


def tool_execution_success(
    result: dict,
) -> bool:
    """
    Determine whether the agent actually executed
    its selected tools successfully.

    Uses LangGraph ToolMessage objects from the
    execution trace instead of relying on the
    custom tool_results state.
    """

    messages = result.get(
        "messages",
        [],
    )

    tool_messages = [
        message
        for message in messages
        if isinstance(
            message,
            ToolMessage,
        )
    ]

    # No ToolMessage means no tool was actually executed.
    if not tool_messages:
        return False

    for message in tool_messages:

        content = message.content

        # Tool content can be a dictionary-like string
        # or a normal string depending on the tool.
        if content is None:
            return False

        if isinstance(
            content,
            str,
        ):
            normalized = content.lower()

            failure_markers = [
                '"found": false',
                "no ipo found",
                "could not find sufficient evidence",
                "insufficient evidence",
            ]

            if any(
                marker in normalized
                for marker in failure_markers
            ):
                return False

            if not content.strip():
                return False

    return True