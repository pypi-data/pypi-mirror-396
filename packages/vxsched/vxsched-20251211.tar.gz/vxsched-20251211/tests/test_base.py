from pathlib import Path
import sys
import types
import importlib.util
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pydantic import BaseModel
from queue import Empty


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


# 提供最小 vxutils
vxutils_stub = types.ModuleType("vxutils")
vxutils_stub.VXDataModel = BaseModel


def _to_datetime(val):
    from datetime import datetime

    if isinstance(val, datetime):
        return val.replace(microsecond=0)
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val).replace(microsecond=0)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val).replace(microsecond=0)
        except Exception:
            return datetime.now().replace(microsecond=0)
    return datetime.now().replace(microsecond=0)


class _DummyExecutor:
    def submit(self, fn, *args, **kwargs):
        from concurrent.futures import Future

        f = Future()
        try:
            res = fn(*args, **kwargs)
            f.set_result(res)
        except Exception as e:
            f.set_exception(e)
        return f


vxutils_stub.to_datetime = _to_datetime
vxutils_stub.VXThreadPoolExecutor = _DummyExecutor
sys.modules["vxutils"] = vxutils_stub


# 构造 vxsched 包与子模块 stub
pkg = types.ModuleType("vxsched")
pkg.__path__ = []
sys.modules["vxsched"] = pkg


class _VXEvent(BaseModel):
    type: str
    data: Dict[str, Any] = {}
    priority: int = 10


class _VXEventHandlers:
    def __init__(self):
        self._handlers: Dict[str, List] = {}
        self.handled: List[_VXEvent] = []

    def add(self, event_type: str, func):
        self._handlers.setdefault(event_type, []).append(func)

    def merge(self, other: "_VXEventHandlers"):
        for k, v in other._handlers.items():
            for f in v:
                self.add(k, f)

    def handle(self, *args, **kwargs):
        event = kwargs.get("event")
        context = kwargs.get("context", {})
        if event is None and args:
            event = args[0]
        if event is None:
            return None
        self.handled.append(event)
        for f in self._handlers.get(event.type, []):
            f(context, event)


class _VXEventQueue:
    def __init__(self):
        from heapq import heappush, heappop

        self._heappush = heappush
        self._heappop = heappop
        self._heap = []
        self._seq = 0

    def put(self, event: _VXEvent, trigger=None):
        created_at = datetime.now().replace(microsecond=0)
        trigger_dt = getattr(trigger, "trigger_dt", created_at)
        key = (getattr(event, "priority", 10), trigger_dt, created_at, self._seq)
        self._seq += 1
        self._heappush(self._heap, (key, event))

    def get(self, timeout: float | None = None):
        if self._heap:
            _, event = self._heappop(self._heap)
            return event
        if timeout is None:
            raise Empty
        time.sleep(min(timeout, 0.01))
        raise Empty

    def __len__(self):
        return len(self._heap)


event_stub = types.ModuleType("vxsched.event")
event_stub.VXEvent = _VXEvent
event_stub.VXEventQueue = _VXEventQueue
event_stub.VXEventHandlers = _VXEventHandlers
sys.modules["vxsched.event"] = event_stub


# 加载 trigger 以提供 VXTrigger 类型（仅用于类型兼容）
trigger_path = SRC_ROOT / "vxsched" / "trigger.py"
spec_t = importlib.util.spec_from_file_location("vxsched.trigger", trigger_path)
mod_t = importlib.util.module_from_spec(spec_t)
sys.modules["vxsched.trigger"] = mod_t
assert spec_t and spec_t.loader
spec_t.loader.exec_module(mod_t)  # type: ignore


# 加载 base.py
base_path = SRC_ROOT / "vxsched" / "base.py"
spec_b = importlib.util.spec_from_file_location("vxsched.base", base_path)
base = importlib.util.module_from_spec(spec_b)
sys.modules["vxsched.base"] = base
assert spec_b and spec_b.loader
spec_b.loader.exec_module(base)  # type: ignore

# 使用测试版事件处理器替换模块实现，便于记录处理过的事件
base.VXEventHandlers = _VXEventHandlers


def test_initialize_sets_mutex_and_handles_init_event():
    sched = base.VXSched()
    ok = sched._initialize()
    assert ok is True
    assert not sched._stop_mutex.is_set()
    # 检查 INIT 事件已被处理
    assert any(e.type == base.INIT_EVENT for e in sched._event_handlers.handled)


def test_start_and_stop_handle_reserved_events():
    sched = base.VXSched()
    assert sched.start() is True
    time.sleep(0.05)
    sched.stop()
    # 检查 SHUTDOWN 事件已被处理
    assert any(e.type == base.SHUTDOWN_EVENT for e in sched._event_handlers.handled)


def test_submit_enqueues_and_handler_invoked():
    sched = base.VXSched()
    recorder: List[_VXEvent] = []

    h = _VXEventHandlers()
    h.add("foo", lambda ctx, ev: recorder.append(ev))
    sched.add_handlers(h)

    assert sched.start() is True
    ev = _VXEvent(type="foo")
    sched.submit(ev)
    time.sleep(0.05)

    assert any(e.type == "foo" for e in sched._event_handlers.handled)
    assert any(e.type == "foo" for e in recorder)


def test_submit_ignored_when_stopped_and_reserved_event():
    sched = base.VXSched()
    # 未启动情况下提交
    ev = _VXEvent(type="bar")
    sched.submit(ev)
    assert sched._event_queue.qsize() == 0

    # 启动后提交保留事件将被忽略
    assert sched.start() is True
    ev2 = _VXEvent(type=base.INIT_EVENT)
    sched.submit(ev2)
    time.sleep(0.02)
    # 未记录新的 INIT（初始化时已有一条）
    assert [e.type for e in sched._event_handlers.handled].count(base.INIT_EVENT) == 1


def test_config_is_immutable_deep():
    cfg = {"a": 1, "b": {"c": [1, 2]}}
    sched = base.VXSched(config=cfg)

    try:
        sched.config["a"] = 2
        assert False, "config 顶层应不可赋值"
    except TypeError:
        pass

    try:
        sched.config["b"]["d"] = 3
        assert False, "config 嵌套 dict 应不可赋值"
    except TypeError:
        pass

    try:
        sched.config["b"]["c"][0] = 9
        assert False, "config 嵌套 list 应被冻结为不可变序列"
    except TypeError:
        pass

    cfg["a"] = 5
    assert sched.config["a"] == 1
