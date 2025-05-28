from datetime import datetime
from typing import List, Optional

import structlog
from pydantic import BaseModel, ConfigDict, Field, computed_field

from lkr.load_test.utils import ms_diff, now


class EventLog(BaseModel):
    event: str
    user_id: str
    dashboard: str
    task_id: str
    task_start_time: datetime
    timestamp: datetime = Field(default_factory=now)
    last_event_time: Optional[datetime] = Field(default=None)
    last_event_name: Optional[str] = Field(default=None)
    model_config = ConfigDict(extra="allow")
    error: Optional[str] = Field(default=None)

    @computed_field(return_type=int)
    @property
    def time_since_start_ms(self):
        return ms_diff(self.task_start_time, self.timestamp)

    @computed_field(return_type=int)
    @property
    def time_since_last_event_ms(self):
        if not self.last_event_time:
            return None
        return ms_diff(self.last_event_time, self.timestamp)


class EventLogger(BaseModel):
    log_event_prefix: str
    user_id: str
    dashboard: str
    task_id: str
    task_start_time: datetime = Field(default_factory=now)
    events: List[EventLog] = []

    @classmethod
    def initialize(
        cls,
        user_id: str,
        dashboard: str,
        task_id: str,
        log_event_prefix: str,
        task_start_time: datetime | None = None,
    ):
        n = cls(
            user_id=user_id,
            dashboard=dashboard,
            task_id=task_id,
            log_event_prefix=log_event_prefix,
        )
        if task_start_time:
            n.task_start_time = task_start_time
        return n

    def log_event(self, event: str, **kwargs):
        logger = structlog.get_logger("looker-embed-observability")
        e = EventLog(
            event=f"{self.log_event_prefix}:{event}",
            user_id=self.user_id,
            dashboard=self.dashboard,
            task_id=self.task_id,
            task_start_time=self.task_start_time,
        )
        for k, v in kwargs.items():
            if k == "dashboard":
                setattr(e, "dashboard_metadata", v)
            else:
                setattr(e, k, v)

        last_event = self.events[-1] if self.events else None
        if last_event:
            e.last_event_time = last_event.timestamp
            e.last_event_name = last_event.event
        self.events.append(e)
        if e.error:
            logger.error(
                e.event,
                **e.model_dump(
                    mode="json",
                    exclude={"event"},
                    exclude_unset=True,
                    exclude_none=True,
                ),
            )
        else:
            logger.info(
                e.event,
                **e.model_dump(
                    mode="json",
                    exclude={"event"},
                    exclude_unset=True,
                    exclude_none=True,
                ),
            )
