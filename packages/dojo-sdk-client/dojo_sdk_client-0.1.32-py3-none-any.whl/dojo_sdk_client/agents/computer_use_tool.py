from dojo_sdk_core.types import (
    Action,
    ClickAction,
    DoneAction,
    DoubleClickAction,
    DragAction,
    HotkeyAction,
    KeyAction,
    MiddleClickAction,
    RightClickAction,
    ScrollAction,
    TypeAction,
)


# Should work with agents that support tool calling. For ones that don't we probalby need a parser
def computer_tool(
    action: str,
    coordinate: list[int] = None,
    text: str = None,
    scroll_direction: str = "up",
    scroll_amount: int = None,
    start_coordinate: list[int] = None,
    duration: float = 1.0,
) -> Action:
    """
    This function handles the conversion of actions from openai's tool call
    format to Dojo's internal Action types. It supports various mouse and keyboard actions.
    When you are done with the task, use the "done" action.

    Args:
        action: The action type to perform. Supported actions:
            - "click", "left_click": Single left mouse click
            - "right_click": Right mouse click
            - "double_click": Double left mouse click
            - "middle_click": Middle mouse click
            - "left_click_drag": Click and drag operation
            - "key": Single key press or hotkey combination (use + to separate keys)
            - "type": Type text string
            - "scroll": Scroll the page
            - "done": Mark the task as done
        coordinate: [x, y] coordinates for mouse actions (required for click actions and drag end)
        text: Text to type or key(s) to press (required for "type" and "key" actions)
        scroll_direction: Direction to scroll, either "up" or "down" (default: "up")
        scroll_amount: Positive number of pixels to scroll (required for scroll action)
        start_coordinate: [x, y] starting coordinates for drag action
        duration: Duration in seconds for drag action (default: 1.0)

    Returns:
        Action: A Dojo Action object ready to be executed

    Raises:
        ValueError: If required parameters are missing or action is unsupported

    Examples:
        >>> computer_tool(action="click", coordinate=[100, 200])
        ClickAction(type=ActionType.CLICK, x=100, y=200)

        >>> computer_tool(action="type", text="hello world")
        TypeAction(type=ActionType.TYPE, text="hello world")

        >>> computer_tool(action="key", text="ctrl+c")
        HotkeyAction(type=ActionType.HOTKEY, keys=["ctrl", "c"])
    """
    if action in ["click", "left_click"]:
        if not coordinate:
            raise ValueError("No coordinate provided for click action")
        return ClickAction(x=coordinate[0], y=coordinate[1])

    elif action == "right_click":
        if not coordinate:
            raise ValueError("No coordinate provided for right_click action")
        return RightClickAction(x=coordinate[0], y=coordinate[1])

    elif action == "double_click":
        if not coordinate:
            raise ValueError("No coordinate provided for double_click action")
        return DoubleClickAction(x=coordinate[0], y=coordinate[1])

    elif action == "middle_click":
        if not coordinate:
            raise ValueError("No coordinate provided for middle_click action")
        return MiddleClickAction(x=coordinate[0], y=coordinate[1])

    elif action == "key":
        if not text:
            raise ValueError("No text provided for key action")
        # Handle both "+" and space as separators for hotkey combinations
        # Try splitting by "+" first, then by space if no "+" found
        if "+" in text:
            hotkeys = text.split("+")
        elif " " in text:
            hotkeys = text.split(" ")
        else:
            hotkeys = [text]

        # Strip whitespace from each key
        hotkeys = [key.strip() for key in hotkeys if key.strip()]

        if len(hotkeys) == 1:
            return KeyAction(key=hotkeys[0])
        return HotkeyAction(keys=hotkeys)

    elif action == "type":
        if not text:
            raise ValueError("No text provided for type action")
        return TypeAction(text=text)

    elif action == "scroll":
        if scroll_amount is None:
            raise ValueError("No scroll amount provided for scroll action")
        return ScrollAction(direction=scroll_direction, amount=scroll_amount)

    elif action == "done":
        return DoneAction()

    elif action == "left_click_drag":
        if not start_coordinate or not coordinate:
            raise ValueError("No start or end coordinate provided for drag action")
        return DragAction(
            from_x=start_coordinate[0],
            from_y=start_coordinate[1],
            to_x=coordinate[0],
            to_y=coordinate[1],
            duration=duration,
        )

    elif action == "screenshot":
        raise ValueError("Screenshot action is not supported - screenshots are automatically provided")

    # Default fallback
    raise ValueError(f"Unsupported action type: {action}")
