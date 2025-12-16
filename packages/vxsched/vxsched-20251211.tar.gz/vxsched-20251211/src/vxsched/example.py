from datetime import datetime, timedelta
from typing import Any
import time

from .scheduler import Scheduler
from .trigger import OnceTrigger, IntervalTrigger, CronTrigger
from .handler import Context


def example_handler(context: Context) -> None:
    """Example handler"""
    print(f"Event {context.event_id} fired at {context.fire_time}")
    print(f"Context params: {context.params}")
    time.sleep(1)  # Simulate time-consuming operation


def main():
    # Create scheduler instance
    scheduler = Scheduler(min_workers=1, max_workers=5, thread_ttl=30)

    # Create a one-off trigger event
    once_trigger = OnceTrigger(datetime.now() + timedelta(seconds=2))
    once_event_id = scheduler.add_event(once_trigger)
    scheduler.handler.add_handler(once_event_id, example_handler)

    # Create an interval trigger event
    interval_trigger = IntervalTrigger(
        interval=timedelta(seconds=3),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(seconds=10),
    )
    interval_event_id = scheduler.add_event(interval_trigger)
    scheduler.handler.add_handler(interval_event_id, example_handler)

    # Create a cron trigger (executes every minute)
    cron_trigger = CronTrigger(
        cron_expression="* * * * *",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=5),
    )
    cron_event_id = scheduler.add_event(cron_trigger)
    scheduler.handler.add_handler(cron_event_id, example_handler)

    # Start scheduler
    try:
        scheduler.start()
        print("Scheduler started...")
        time.sleep(15)  # Run for 15 seconds then shutdown
    finally:
        scheduler.shutdown()
        print("Scheduler stopped")


if __name__ == "__main__":
    main()
