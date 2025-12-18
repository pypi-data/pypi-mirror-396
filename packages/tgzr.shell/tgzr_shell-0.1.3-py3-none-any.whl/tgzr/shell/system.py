from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session


class System:
    """
    Utility class to manage the "System" folder in a tgzr session home.
    """

    def __init__(self, session: Session):
        self.session = session
