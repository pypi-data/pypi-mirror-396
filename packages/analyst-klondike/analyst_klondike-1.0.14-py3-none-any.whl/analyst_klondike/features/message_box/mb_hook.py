from typing import Callable
from analyst_klondike.features.message_box.ui.mb_screen import MessageBoxScreen
from analyst_klondike.state.app_state import AppState


def show_message(message: str, on_close: Callable[[AppState | None], None] | None = None) -> None:
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app

    app = get_app()
    app.push_screen(MessageBoxScreen(message=message), on_close)


def hide_message_box():
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app

    app = get_app()

    last_screen = app.screen_stack[-1]
    if isinstance(last_screen, MessageBoxScreen):
        app.pop_screen()
