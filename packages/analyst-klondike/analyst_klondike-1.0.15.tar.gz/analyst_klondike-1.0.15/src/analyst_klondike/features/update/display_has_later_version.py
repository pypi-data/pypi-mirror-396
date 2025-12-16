from dataclasses import dataclass
import httpx
import analyst_klondike
from analyst_klondike.features.events.event_hook import send_event
from analyst_klondike.features.message_box.mb_hook import show_message
from analyst_klondike.state.app_state import AppState


def _get_latest_app_version() -> str | None:
    try:
        with httpx.Client() as client:
            response = client.get(
                'https://pypi.org/pypi/analyst-klondike/json', timeout=5000)
            response.raise_for_status()
            data = response.json()
            latest_version = data['info']['version']
            return latest_version
    except:
        return None


@dataclass
class IsOutdatedResult:
    current_version: str
    latest_version: str
    is_outdated: bool


def _is_outdated() -> IsOutdatedResult | None:
    current_version = analyst_klondike.__version__
    latest_version = _get_latest_app_version()
    if latest_version is None:
        return None
    is_outdated = _more(latest_version, current_version)
    return IsOutdatedResult(
        current_version=current_version,
        latest_version=latest_version,
        is_outdated=is_outdated
    )


def _more(first_v: str, next_v: str) -> bool:
    def _parse(ver_str: str) -> list[int]:
        return [int(v) for v in ver_str.split(".")]

    return _parse(first_v) > _parse(next_v)


def close_app(_: AppState) -> None:
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app
    app = get_app()
    send_event("app_closed_after_outdated", "/")
    app.exit(0)


def display_message_if_outdated():
    res = _is_outdated()
    if res is None:
        send_event("fail_to_get_latest_version", "/")
        show_message(message="Ошибка при загрузке последней версии приложения")
        return
    if res.is_outdated:
        send_event("app_is_outdated", "/")
        show_message(f"Доступна новая версия {res.latest_version} " +
                     f"(сейчас установлена {res.current_version}). \n"
                     "Обновите приложение. \n" +
                     "Для этого закройте приложение и запустите команду: \n" +
                     "[@click=app.copy_update_str_to_clipboard]uv tool upgrade analyst-klondike[/]",
                     close_app)
