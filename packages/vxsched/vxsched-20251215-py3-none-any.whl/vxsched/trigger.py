"""Trigger module providing multiple types of schedulable triggers.

This module implements:
- VXTrigger: base trigger interface
- OnceTrigger: fires once at a specific time
- IntervalTrigger: fires repeatedly at fixed intervals
- CronTrigger: fires based on cron expressions

Examples:
    # Create an interval trigger every 5 minutes
    trigger = IntervalTrigger(timedelta(minutes=5))

    # Create a cron trigger that fires at 02:00 daily
    cron_trigger = CronTrigger("0 0 2 * * *")
"""

import threading
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Generator, Literal, List, Any, Tuple
from heapq import heappush, heappop
from contextlib import suppress
from queue import Empty

from vxutils import to_datetime, VXDataModel
from pydantic import Field

__all__ = [
    "VXTrigger",
    "OnceTrigger",
    "IntervalTrigger",
    "Cron",
    "CronField",
    "CronTrigger",
    "once",
    "every",
    "crontab",
]


class CronField:
    """Cron expression field parser.

    Parses a single cron field (second, minute, hour, day, month, weekday).
    Supported formats:
    - exact value: "5"
    - range: "1-5"
    - step: "*/5" or "1/5"
    - list: "1,3,5"
    - any: "*"
    """

    def __init__(self, value: str, min_val: int, max_val: int):
        """Initialize CronField.

        Args:
            value: cron field value
            min_val: minimum allowed value
            max_val: maximum allowed value
        """
        self.min = min_val
        self.max = max_val
        self.values = self._parse_field(value)
        self.iter_index = 0

    def _parse_field(self, value: str) -> List[int]:
        """Parse cron field value.

        Args:
            value: field value to parse

        Returns:
            list of valid values
        """
        if value == "*":
            return list(range(self.min, self.max + 1))

        values = set()
        for part in value.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                values.update(range(start, end + 1))
            elif "/" in part:
                start_val, step = part.split("/")
                start = self.min if start_val == "*" else int(start_val)
                step = int(step)
                values.update(range(start, self.max + 1, step))
            else:
                values.add(int(part))
        return sorted(list(values))

    def __contains__(self, value: int) -> bool:
        """Check if value is allowed in this field."""
        return value in self.values

    def __iter__(self) -> Generator[int, None, None]:
        """Iterate over field values."""
        for idx in range(self.iter_index, len(self.values)):
            yield self.values[idx]
        self.iter_index = 0  # Reset the index to 0 after the loop

    def reset(self, value: Optional[int] = None) -> None:
        """Reset iteration starting index to first >= value."""

        self.iter_index = 0
        for idx, val in enumerate(self.values):
            if val >= value:
                self.iter_index = idx
                break


class Cron:
    """Cron expression parser.

    Supports: seconds, minutes, hours, days, months, weekdays.
    """

    def __init__(self, cron_expression: str, start_dt: Any = None, end_dt: Any = None):
        """Initialize Cron.

        Args:
            cron_expression: cron expression string
            start_dt: start datetime
            end_dt: end datetime
        """
        self.cron_expression = cron_expression
        if start_dt is None:
            start_dt = datetime.now()
        if end_dt is None:
            end_dt = datetime.max
        self.start_dt = to_datetime(start_dt).replace(microsecond=0)
        self.end_dt = to_datetime(end_dt).replace(microsecond=0)

        fields = self.cron_expression.split()
        if len(fields) != 6:
            raise ValueError("Invalid cron expression format")

        second, minute, hour, day, month, weekday = fields

        self.seconds = CronField(second, 0, 59)
        self.minutes = CronField(minute, 0, 59)
        self.hours = CronField(hour, 0, 23)
        self.days = CronField(day, 1, 31)
        self.months = CronField(month, 1, 12)
        self.weekdays = CronField(weekday, 0, 6)

    def _initialize_fields(self, current_dt: datetime) -> datetime:
        """Initialize iteration indices based on current time."""

        current_dt = (
            current_dt.replace(microsecond=0)
            if current_dt
            else datetime.now().replace(microsecond=0)
        )

        self.seconds.reset(current_dt.second)
        self.minutes.reset(current_dt.minute)
        self.hours.reset(current_dt.hour)
        self.days.reset(current_dt.day)
        self.months.reset(current_dt.month)

        if current_dt.month <= self.months.values[-1]:
            self.months.reset(current_dt.month)
            if current_dt.day <= self.days.values[-1]:
                self.days.reset(current_dt.day)
                if current_dt.hour <= self.hours.values[-1]:
                    self.hours.reset(current_dt.hour)
                    if current_dt.minute <= self.minutes.values[-1]:
                        self.minutes.reset(current_dt.minute)
                        if current_dt.second <= self.seconds.values[-1]:
                            self.seconds.reset(current_dt.second)
        else:
            current_dt = current_dt.replace(
                year=current_dt.year + 1,
                month=current_dt.month.values[0],
                day=self.days.values[0],
                hour=self.hours.values[0],
                minute=self.minutes.values[0],
                second=self.seconds.values[0],
                microsecond=0,
            )
        return current_dt

    def __call__(
        self, current_dt: Optional[datetime] = None
    ) -> Generator[datetime, None, None]:
        """Yield matching datetimes within range."""
        if current_dt is None:
            current_dt = datetime.now()

        current_dt = self._initialize_fields(current_dt)

        while current_dt <= self.end_dt:
            for month in self.months:
                for day in self.days:
                    try:
                        current_dt = current_dt.replace(
                            year=current_dt.year,
                            month=month,
                            day=day,
                        )
                        if current_dt.weekday() not in self.weekdays:
                            continue

                        for hour in self.hours:
                            for minute in self.minutes:
                                for second in self.seconds:
                                    current_dt = current_dt.replace(
                                        hour=hour, minute=minute, second=second
                                    )
                                    if current_dt >= self.start_dt:
                                        yield current_dt
                    except ValueError:
                        pass
            current_dt = current_dt.replace(
                year=current_dt.year + 1,
            )


class VXTrigger(VXDataModel):
    """Base trigger interface.

    Subclasses must implement get_next_fire_time.
    """

    start_dt: datetime = Field(
        default_factory=datetime.now, description="Trigger start time"
    )
    end_dt: datetime = Field(
        default_factory=datetime.max, description="Trigger end time"
    )
    trigger_dt: datetime = Field(
        default_factory=datetime.now, description="Current fire time"
    )
    interval: float = Field(default=0.0, description="Trigger interval seconds")
    cron_expression: str = Field(default="* * * * * *", description="Cron expression")
    skip_past: bool = Field(default=False, description="Skip past times")
    status: Literal["Ready", "Running", "Completed"] = Field(
        default="Ready", description="Trigger status"
    )

    def model_post_init(self, __context: Any, /) -> None:
        if self.start_dt > self.end_dt:
            raise ValueError(
                f"{self.start_dt=} must not be greater than {self.end_dt=}"
            )

        if not (self.start_dt <= self.trigger_dt <= self.end_dt):
            raise ValueError(
                f"{self.trigger_dt=} must be between {self.start_dt=} and {self.end_dt=}"
            )

    @abstractmethod
    def get_next_fire_time(
        self,
    ) -> Optional[Tuple[datetime, Literal["Ready", "Running", "Completed"]]]:
        """Get next fire time."""
        raise NotImplementedError

    @abstractmethod
    def get_first_fire_time(
        self,
    ) -> Optional[Tuple[datetime, Literal["Ready", "Running", "Completed"]]]:
        """Get first fire time."""
        raise NotImplementedError

    def __iter__(self) -> Generator[datetime, None, None]:
        self.status = "Ready"
        return self

    def __next__(self) -> datetime:
        if self.status == "Completed":
            raise StopIteration

        if self.status == "Ready":
            self.trigger_dt, self.status = self.get_first_fire_time()
        else:
            self.trigger_dt, self.status = self.get_next_fire_time()

        if self.status == "Completed":
            raise StopIteration

        return self

    def __lt__(self, other: "VXTrigger") -> bool:
        if isinstance(other, VXTrigger):
            return self.trigger_dt < other.trigger_dt
        return NotImplemented

    def __le__(self, other: "VXTrigger") -> bool:
        if isinstance(other, VXTrigger):
            return self.trigger_dt <= other.trigger_dt
        return NotImplemented

    def __gt__(self, other: "VXTrigger") -> bool:
        if isinstance(other, VXTrigger):
            return self.trigger_dt > other.trigger_dt
        return NotImplemented

    def __ge__(self, other: "VXTrigger") -> bool:
        if isinstance(other, VXTrigger):
            return self.trigger_dt >= other.trigger_dt
        return NotImplemented


class OnceTrigger(VXTrigger):
    """One-off trigger that fires once at a specific time."""

    def __init__(self, trigger_dt: datetime, skip_past: bool = False):
        """Initialize OnceTrigger.

        Args:
            trigger_dt: fire time
        """
        super().__init__(
            start_dt=trigger_dt,
            end_dt=trigger_dt,
            trigger_dt=trigger_dt,
            skip_past=skip_past,
            interval=0,
        )

    def get_next_fire_time(
        self,
    ) -> Optional[Tuple[datetime, Literal["Ready", "Running", "Completed"]]]:
        """Get next fire time for one-off trigger (always Completed)."""
        return datetime.max, "Completed"

    def get_first_fire_time(self) -> Optional[Tuple[datetime, Literal["Ready"]]]:
        """Get first fire time."""
        if self.skip_past and self.trigger_dt < datetime.now():
            return datetime.max, "Completed"
        else:
            return self.trigger_dt, "Running"


class IntervalTrigger(VXTrigger):
    """Interval trigger that repeats on a fixed interval within a time range."""

    def __init__(
        self,
        interval: float,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        skip_past: bool = False,
    ):
        """Initialize IntervalTrigger.

        Args:
            interval: interval seconds
            start_dt: start time
            end_dt: end time
            skip_past: skip past times
        """

        super().__init__(
            interval=interval,
            start_dt=start_dt,
            trigger_dt=start_dt,
            end_dt=end_dt,
            skip_past=skip_past,
        )

    def get_first_fire_time(self) -> Optional[datetime]:
        """Get first fire time."""
        if self.status in ["Running", "Completed"]:
            return self.trigger_dt, self.status

        if self.skip_past and self.trigger_dt < datetime.now():
            delta = timedelta(
                seconds=(datetime.now().timestamp() - self.start_dt.timestamp())
                // self.interval
                * self.interval
                + self.interval
            )
            self.trigger_dt = self.start_dt + delta
            if self.trigger_dt > self.end_dt:
                return datetime.max, "Completed"
            return self.trigger_dt, "Running"
        else:
            return self.trigger_dt, "Running"

    def get_next_fire_time(
        self,
    ) -> Optional[Tuple[datetime, Literal["Ready", "Running", "Completed"]]]:
        """Get next fire time or Completed when exceeding end time."""
        if (
            self.status == "Completed"
            or self.trigger_dt + timedelta(seconds=self.interval) > self.end_dt
        ):
            return datetime.max, "Completed"

        self.trigger_dt += timedelta(seconds=self.interval)
        return self.trigger_dt, "Running"


class CronTrigger(VXTrigger):
    """Cron-based trigger supporting second-level precision and time range."""

    def __init__(
        self,
        cron_expression: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        skip_past: bool = False,
    ):
        """Initialize CronTrigger.

        Args:
            cron_expression: cron expression
            start_dt: start time
            end_dt: end time
            skip_past: skip past times
        """
        super().__init__(
            cron_expression=cron_expression,
            start_dt=start_dt,
            trigger_dt=start_dt,
            end_dt=end_dt,
            skip_past=skip_past,
        )

    def get_first_fire_time(self) -> Optional[Tuple[datetime, Literal["Ready"]]]:
        """Get first fire time."""
        if self.status in ["Running", "Completed"]:
            return self.trigger_dt, self.status

        self._cron = Cron(
            cron_expression=self.cron_expression,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
        )()
        for trigger_dt in self._cron:
            if self.skip_past and trigger_dt < datetime.now():
                continue
            elif trigger_dt > self.end_dt:
                return datetime.max, "Completed"
            else:
                return trigger_dt, "Running"
        return datetime.max, "Completed"

    def get_next_fire_time(
        self,
    ) -> Optional[Tuple[datetime, Literal["Ready", "Running", "Completed"]]]:
        """Get next fire time or Completed when exhausted."""
        if self.status == "Completed":
            return datetime.max, "Completed"

        try:
            trigger_dt = next(self._cron)
            if self.trigger_dt > self.end_dt:
                return datetime.max, "Completed"
        except StopIteration:
            return datetime.max, "Completed"

        return trigger_dt, "Running"


def once(fire_time: datetime) -> VXTrigger:
    """Decorator for a one-off trigger."""

    return OnceTrigger(fire_time)


def daily(
    time_str: str,
    start_dt: Optional[datetime] = None,
    end_dt: Optional[datetime] = None,
    skip_past: bool = False,
) -> VXTrigger:
    """Decorator for a daily trigger at HH:MM:SS."""
    if start_dt is None:
        start_dt = datetime.now()
    if end_dt is None:
        end_dt = datetime.max
    hour, minute, second = map(int, time_str.split(":"))
    return CronTrigger(
        f"{second} {minute} {hour} * * *",
        start_dt=start_dt,
        end_dt=end_dt,
        skip_past=skip_past,
    )


def weekly(
    time_str: str,
    day_of_week: int,
    start_dt: Optional[datetime] = None,
    end_dt: Optional[datetime] = None,
    skip_past: bool = False,
) -> VXTrigger:
    """Decorator for a weekly trigger at HH:MM:SS on specified weekday."""
    if start_dt is None:
        start_dt = datetime.now()
    if end_dt is None:
        end_dt = datetime.max
    hour, minute, second = map(int, time_str.split(":"))

    return CronTrigger(
        f"{second} {minute} {hour} * * {day_of_week}",
        start_dt=start_dt,
        end_dt=end_dt,
        skip_past=skip_past,
    )


def every(
    interval: float,
    start_dt: Optional[datetime] = None,
    end_dt: Optional[datetime] = None,
    skip_past: bool = False,
) -> VXTrigger:
    """Decorator for an interval trigger."""
    start_dt = datetime.now() if start_dt is None else start_dt
    end_dt = datetime.max if end_dt is None else end_dt

    return IntervalTrigger(
        interval=interval, start_dt=start_dt, end_dt=end_dt, skip_past=skip_past
    )


def crontab(
    cron_expression: str,
    start_dt: Optional[datetime] = None,
    end_dt: Optional[datetime] = None,
    skip_past: bool = False,
) -> VXTrigger:
    """Decorator for a cron-based trigger."""
    start_dt = datetime.now() if start_dt is None else start_dt
    end_dt = datetime.max if end_dt is None else end_dt
    return CronTrigger(
        cron_expression=cron_expression,
        start_dt=start_dt,
        end_dt=end_dt,
        skip_past=skip_past,
    )


if __name__ == "__main__":
    cron = Cron("01 30 9 * * 0-4", datetime.now(), datetime.now() + timedelta(days=30))
    current_dt = datetime.now()
    cnt = 0
    for dt in cron():
        print(dt)
        cnt += 1
        if cnt > 10:
            break

    once_trigger = OnceTrigger(datetime.now() - timedelta(seconds=10), skip_past=True)
    print(once_trigger)
    print("-" * 50)
    for t in once_trigger:
        print(t)
    else:
        print("Completed")
    print("+" * 50)
    once_trigger = OnceTrigger(datetime.now() - timedelta(seconds=10), skip_past=False)
    for t in once_trigger:
        print(t)
    else:
        print("Completed")
    print("=" * 50)
    print(once_trigger)

    now = datetime.now()
    print(f"{now=}")
    interval_trigger = IntervalTrigger(
        2,
        now - timedelta(seconds=10),
        now + timedelta(seconds=10),
        skip_past=True,
    )
    for t in interval_trigger:
        print(t.trigger_dt)
    else:
        print("Completed")
    print("-" * 50)

    cron_trigger = CronTrigger(
        "*/3 */5 */2 * * 0-4",
        now - timedelta(days=1),
        now + timedelta(days=1),
        skip_past=True,
    )
    for t in cron_trigger:
        print(t.trigger_dt)
    else:
        print("Completed")
    print(cron_trigger)

    # q = VXSchedQueue()
    # q.put("once_trigger", trigger=once(datetime.now() + timedelta(seconds=1)))
    # q.put("interval_trigger 2s", trigger=every(interval=2))
    # q.put("crontab_trigger ", trigger=crontab("*/2 * * * * *"))
    # from vxutils import loggerConfig
#
# loggerConfig()
# import logging
#
# while True:
#    logging.info(q.get())
