from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MemoryFrames.Settings import Settings


# ----------------------------------------------------------------------
def Execute(settings: Settings) -> None:
    """Execute the Textual user experience."""

    print("TextualUserExperience", settings)  # noqa: T201
