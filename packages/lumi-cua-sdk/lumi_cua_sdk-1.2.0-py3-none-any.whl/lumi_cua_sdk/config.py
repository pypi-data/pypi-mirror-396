import os
import threading
from typing import Any, Type, TypeVar, Optional, cast

T = TypeVar("T", bound="Config")


class Config(object):
    _instance: Optional["Config"] = None
    _lock = threading.Lock()

    web_ui_url: str
    vnc_proxy_url: str
    sandbox_manager_url: str
    agent_planner_url: str
    auth_token: str

    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cast(T, cls._instance)

    def __init__(
        self,
            agent_planner_url: str = "",
            sandbox_manager_url: str = "",
            auth_token: str = "",
            web_ui_url: str = "",
            vnc_proxy_url: str = ""
    ) -> None:
        if hasattr(self, "initialized") and self.initialized:
            return

        self.agent_planner_url = agent_planner_url or os.environ.get("AGENT_PLANNER_URL")
        self.sandbox_manager_url = sandbox_manager_url or os.environ.get("SANDBOX_MANAGER_URL")
        self.auth_token = auth_token or os.environ.get("AUTH_TOKEN")
        self.web_ui_url = web_ui_url or os.environ.get("WEB_UI_URL")
        self.vnc_proxy_url = vnc_proxy_url or os.environ.get("VNC_PROXY")
        self.initialized = True

    def __repr__(self) -> str:
        return (
            f"sandbox_manager_url={self.sandbox_manager_url!r} "
            f"agent_planner_url={self.auth_token!r} "
            f"auth_token={self.auth_token!r}"
            f"web_ui_url={self.web_ui_url!r}"
            f"vnc_proxy_url={self.vnc_proxy_url!r}"
        )


config = Config()


def get_config() -> Config:
    return config


def set_config(
    agent_planner_url: Optional[str] = "",
    sandbox_manager_url: Optional[str] = "",
    auth_token: Optional[str] = "",
    web_ui_url: Optional[str] = "",
    vnc_proxy_url: Optional[str] = "",
) -> None:
    config.agent_planner_url = agent_planner_url or config.agent_planner_url
    config.sandbox_manager_url = sandbox_manager_url or config.sandbox_manager_url
    config.auth_token = auth_token or config.auth_token
    config.web_ui_url = web_ui_url or config.web_ui_url
    config.vnc_proxy_url = vnc_proxy_url or config.vnc_proxy_url
