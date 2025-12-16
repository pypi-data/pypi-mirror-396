from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import pluggy

from MemoryFrames import APP_NAME

if TYPE_CHECKING:
    from collections.abc import Callable
    from threading import Event
    from pathlib import Path

    from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
    from MemoryFrames.PluginInfra.UserExperienceInfo import UserExperienceInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ThreadInfo:
    """Information about a thread that is defined by a Plugin but created and managed by the application."""

    description: str
    thread_func: Callable[
        [
            Event  # Event set when the application is quitting
        ],
        None,
    ]


# ----------------------------------------------------------------------
class Plugin(ABC):
    """Base class for all MemoryFrames plugins."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        root_data_dir: Path,
    ) -> None:
        scrubbed_unique_name = self.unique_name

        for invalid_char in ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."]:
            scrubbed_unique_name = scrubbed_unique_name.replace(invalid_char, "_")

        self.working_dir = root_data_dir / scrubbed_unique_name

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the plugin."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abstractmethod
    def author(self) -> str:
        """The author of the plugin. This value will be used in the plugin's unique name."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of the plugin."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abstractmethod
    def plugin_priority(self) -> int:
        """The priority of the plugin. Higher values indicate higher priority, which will cause the plugin to appear before other lower priority plugins."""
        raise NotImplementedError()  # pragma: no cover

    @cached_property
    def unique_name(self) -> str:
        """The unique name of the plugin."""
        return f"{self.author}_{self.name}"

    # ----------------------------------------------------------------------
    def GetNoteSource(
        self,
        observer: NoteSourceObserver,  # noqa: ARG002
        enqueue_thread_info_func: Callable[[ThreadInfo], None],  # noqa: ARG002
    ) -> NoteSource | None:
        """Return a NoteSource implemented by this plugin."""
        return None


# ----------------------------------------------------------------------
@pluggy.HookspecMarker(APP_NAME)
def GetPlugin(
    root_data_dir: Path,
    all_plugins_settings: dict[str, object],
    user_experience_info: UserExperienceInfo,
) -> Plugin:
    """Return a Plugin instance."""
    raise NotImplementedError()  # pragma: no cover
