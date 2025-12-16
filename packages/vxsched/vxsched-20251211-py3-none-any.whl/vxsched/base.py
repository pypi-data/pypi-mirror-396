"""
Base classes for the VXSched library.
"""

import time
import logging
import importlib.util
from pathlib import Path
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Callable, DefaultDict, Set
import threading
from threading import Event, Thread, current_thread
from contextlib import suppress
from collections import defaultdict
from concurrent.futures import Future
from queue import Empty
from heapq import heappush, heappop
from pydantic import Field
from vxutils import VXDataModel, VXThreadPoolExecutor
from vxsched.trigger import VXTrigger, once
from types import MappingProxyType
from copy import deepcopy


INIT_EVENT = "__INIT__"
SHUTDOWN_EVENT = "__SHUTDOWN__"
RESERVED_EVENTS = {INIT_EVENT, SHUTDOWN_EVENT}


class VXEvent(VXDataModel):
    """Event"""

    id: str = Field(
        default_factory=lambda: uuid.uuid4().hex[:8], description="Event ID"
    )
    type: str = Field(description="Event type")
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Event payload"
    )
    priority: int = Field(default=10, description="Event priority")
    channel: str = Field(default="default", description="Event channel")
    reply_to: str = Field(default="", description="Reply channel")


class VXEventQueue:
    """Event queue"""

    def __init__(self):
        self._queue: List[Tuple[VXTrigger, Any]] = []
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)

    def _qsize(self):
        now = datetime.now()
        return len([1 for _, t, _ in self._queue if t.trigger_dt <= now])

    @property
    def queue(self) -> List[Tuple[VXTrigger, Any]]:
        """Return a list of all tasks for debugging."""
        return self._queue

    def qsize(self) -> int:
        """Return queue size"""
        with self.mutex:
            return self._qsize()

    def empty(self):
        """Return True if the queue is empty, False otherwise (not reliable!)."""
        with self.mutex:
            return self._qsize() == 0

    def put(self, event: "VXEvent", trigger: Optional[VXTrigger] = None) -> None:
        """Put an item into the queue."""
        if trigger is None:
            trigger = once(fire_time=datetime.now())

        with self.mutex:
            self._put(event, trigger=trigger)
            self.not_empty.notify()

    # Put a new item in the queue
    def _put(self, event: "VXEvent", trigger: VXTrigger) -> None:
        with suppress(StopIteration):
            next(trigger)
            heappush(self._queue, (event.priority, trigger, event))

    def get(self, block=True, timeout=None) -> Optional["VXEvent"]:
        """Remove and return an item from the queue."""
        with self.not_empty:
            if not block and (not self._qsize()):
                raise Empty

            if timeout is not None and timeout <= 0:
                raise ValueError("'timeout' must be a non-negative number")

            if timeout is not None:
                endtime = datetime.now().timestamp() + timeout
            else:
                endtime = float("inf")

            while not self._qsize():
                now = datetime.now().timestamp()
                if now >= endtime:
                    raise Empty

                lastest_trigger_dt = (
                    endtime
                    if len(self._queue) == 0
                    else self._queue[0][1].trigger_dt.timestamp()
                )
                min_endtime = min(endtime, lastest_trigger_dt, now + 1)
                remaining = min_endtime - now
                self.not_empty.wait(remaining)
            event = self._get()
            return event

    def get_nowait(self) -> VXEvent:
        """Equivalent to get(block=False)."""
        return self.get(block=False)

    def _get(self) -> VXEvent:
        _, trigger, event = heappop(self._queue)
        if trigger.status != "Completed":
            self._put(event, trigger)
            self.not_empty.notify()
        return event


class VXEventHandlers:
    """Event handlers"""

    executor: VXThreadPoolExecutor = VXThreadPoolExecutor()

    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[Callable[...]]] = defaultdict(list)

    def __call__(
        self,
        event_type: str,
    ) -> None:
        """Register handler via decorator"""

        def wrapper(handler: Callable[[VXEvent, Dict[str, Any]], Any]) -> None:
            self.register(event_type, handler)
            return handler

        return wrapper

    def register(
        self, event_type: str, handler: Callable[[VXEvent, Dict[str, Any]], Any]
    ) -> None:
        """Register event handler"""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logging.warning(
                f"Register handler {handler.__name__} to event type {event_type}"
            )

    def unregister(
        self,
        event_type: str,
        handler: Optional[Callable[[VXEvent, Dict[str, Any]], Any]] = None,
    ) -> None:
        """Unregister event handler"""
        if handler is None:
            for hdlr in self._handlers[event_type]:
                self._handlers[event_type].remove(hdlr)
                logging.warning(
                    f"Unregister handler {hdlr.__name__} from event type {event_type}"
                )
        elif handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logging.warning(
                f"Unregister handler {handler.__name__} from event type {event_type}"
            )
        else:
            logging.error(
                f"Handler {handler.__name__} not registered to event type {event_type}"
            )

    def handle(
        self, app: "VXSched", event: VXEvent, *, wait: bool = False
    ) -> Optional[List[Any]]:
        """Handle event"""
        results: List[Future] = [
            self.executor.submit(handler, app, event)
            for handler in self._handlers[event.type]
        ]
        return [r.result() for r in results] if wait else results

    def merge(self, handlers: "VXEventHandlers") -> None:
        """Merge handlers"""
        for event_type, hdls in handlers._handlers.items():
            for handler in hdls:
                if handler not in self._handlers[event_type]:
                    self._handlers[event_type].append(handler)
                    logging.debug(
                        f"Merge handler {handler.__name__} to event type {event_type}"
                    )
                else:
                    logging.debug(
                        f"Handler {handler.__name__} already registered to event type {event_type}"
                    )


def _freeze(obj):
    if isinstance(obj, dict):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_freeze(v) for v in obj)
    if isinstance(obj, set):
        return frozenset(_freeze(v) for v in obj)
    if isinstance(obj, tuple):
        return tuple(_freeze(v) for v in obj)
    return obj


class _Parameters:
    """
    Parameters for the VXSched.
    """

    def __getitem__(self, name: str, /) -> Any:
        return getattr(self, name)

    def __setitem__(self, name: str, value: Any, /) -> None:
        setattr(self, name, value)


class VXSched:
    """
    Base class for the VXSched.
    """

    def __init__(
        self, event_queue: VXEventQueue = None, config: Optional[Dict[str, Any]] = None
    ):
        self._event_queue = event_queue or VXEventQueue()
        self._event_handlers = VXEventHandlers()
        self._stop_mutex = Event()
        self._stop_mutex.set()

        raw_config = deepcopy(config) if config is not None else {}
        self._config = _freeze(raw_config)
        self._params: _Parameters = _Parameters()

        self._workers: Set[Thread] = set()

    @property
    def config(self) -> Dict[str, Any]:
        """Get the config."""
        return self._config

    @property
    def params(self) -> _Parameters:
        """Get the params."""
        return self._params

    @property
    def event_handlers(self) -> VXEventHandlers:
        """Get the event handlers."""
        return self._event_handlers

    def load_config(self, **kwargs: Any) -> None:
        """Load the config."""
        self._config = _freeze({**kwargs})

    def run(self, *, wait: bool = True) -> None:
        """Run the scheduler."""
        logging.debug(
            f"{self.__class__.__name__} worker({current_thread().name}) started."
        )
        while not self._stop_mutex.is_set():
            try:
                event = self._event_queue.get(timeout=1)
                self._event_handlers.handle(app=self, event=event, wait=wait)
            except Empty:
                continue
            except Exception as e:
                logging.error(
                    f"Error handling event {event}: {e}",
                    exc_info=True,
                    stack_info=True,
                )
        logging.debug(
            f"{self.__class__.__name__} worker({current_thread().name}) stopped."
        )

    def _initialize(self) -> bool:
        """Start the scheduler."""
        if not self._stop_mutex.is_set():
            logging.warning(f"{self.__class__.__name__} scheduler is already started.")
            return False

        try:
            self._stop_mutex.clear()
            self._event_handlers.handle(
                app=self, event=VXEvent(type=INIT_EVENT), wait=True
            )
            logging.info(
                f"{self.__class__.__name__} {INIT_EVENT} event handled successfully."
            )
        except Exception as e:
            logging.error(
                f"Error handling {INIT_EVENT} event: {e}",
                exc_info=True,
                stack_info=True,
            )
            self._stop_mutex.set()
            return False
        return True

    def stop(self) -> None:
        """Stop the scheduler."""
        if self._stop_mutex.is_set():
            logging.warning(f"{self.__class__.__name__} scheduler is already stopped.")
            return

        try:
            self._stop_mutex.set()
            for worker in self._workers:
                worker.join()
            self._workers.clear()

            self._event_handlers.handle(
                app=self, event=VXEvent(type=SHUTDOWN_EVENT), wait=True
            )
            logging.info(
                f"{self.__class__.__name__} {SHUTDOWN_EVENT} event handled successfully."
            )
        except Exception as e:
            logging.error(
                f"Error handling {SHUTDOWN_EVENT} event: {e}",
                exc_info=True,
                stack_info=True,
            )
        return

    def start(self, *, wait: bool = False) -> None:
        """Start the scheduler."""
        if not self._initialize():
            return False

        for i in range(3):
            worker = Thread(
                target=self.run,
                daemon=True,
                name=f"{self.__class__.__name__}Worker-{i}",
            )
            worker.start()
            self._workers.add(worker)

        return True

    def wait(self) -> None:
        """Wait for all workers to finish."""
        logging.warning(f"Press Ctrl+C to stop the {self.__class__.__name__}.")
        while not self._stop_mutex.is_set():
            time.sleep(1)

    def submit(self, event: VXEvent, *, trigger: VXTrigger = None) -> None:
        """Submit an event to the scheduler."""
        if self._stop_mutex.is_set():
            logging.warning(f"{self.__class__.__name__} scheduler is already stopped.")
            return

        if event.type in RESERVED_EVENTS:
            logging.warning(f"Event type {event.type} is reserved.")
            return

        self._event_queue.put(event, trigger=trigger)

    def add_handlers(self, handlers: VXEventHandlers) -> None:
        """Add event handlers to the scheduler."""
        self._event_handlers.merge(handlers)

    def load_modules(self, path: str) -> None:
        """Load modules from the given path."""
        for module in Path(path).glob("*.py"):
            if module.name.startswith("_"):
                continue
            logging.info(f"Loading module {module.name}")
            spec = importlib.util.spec_from_file_location(module.stem, module)
            if spec is None:
                logging.error(f"Error loading module {module.name}")
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
