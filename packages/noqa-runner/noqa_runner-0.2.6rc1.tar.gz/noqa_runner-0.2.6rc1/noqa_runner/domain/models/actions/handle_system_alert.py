from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from noqa_runner.domain.models.actions.base import BaseAction


class HandleSystemAlert(BaseAction):
    """Accept or dismiss system alerts"""

    name: Literal["handle_system_alert"] = "handle_system_alert"
    accept: bool = Field(
        description="Whether to accept (true) or dismiss (false) the system alert"
    )
    alert_text: SkipJsonSchema[str | None] = None

    def get_action_description(self) -> str:
        """Get description of alert handling action"""
        action_word = "Accepted" if self.accept else "Dismissed"
        return f"{action_word} system alert: {self.alert_text}"
