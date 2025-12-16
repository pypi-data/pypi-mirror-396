from datetime import datetime, timedelta
from pathlib import Path
import sys

# 允许直接从 src 布局导入包
SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import types
from pydantic import BaseModel


def _to_datetime(val):
    if isinstance(val, datetime):
        return val
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val).replace(microsecond=0)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val).replace(microsecond=0)
        except Exception:
            return datetime.now().replace(microsecond=0)
    return datetime.now().replace(microsecond=0)


# 注入最小可用的 vxutils 以满足导入需求
vxutils_stub = types.ModuleType("vxutils")
vxutils_stub.to_datetime = _to_datetime
vxutils_stub.VXDataModel = BaseModel
sys.modules["vxutils"] = vxutils_stub

import importlib.util

trigger_path = SRC_ROOT / "vxsched" / "trigger.py"
spec = importlib.util.spec_from_file_location("vxsched_trigger", trigger_path)
module = importlib.util.module_from_spec(spec)
sys.modules["vxsched_trigger"] = module
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore

OnceTrigger = module.OnceTrigger
once = module.once


def test_once_trigger_first_fire_running_when_future_no_skip():
    dt_future = datetime.now() + timedelta(hours=1)
    t = OnceTrigger(dt_future, skip_past=False)

    fire_time, status = t.get_first_fire_time()
    assert status == "Running"
    assert fire_time == dt_future

    next_time, next_status = t.get_next_fire_time()
    assert next_status == "Completed"
    assert next_time == datetime.max


def test_once_trigger_completed_when_past_and_skip_true():
    dt_past = datetime.now() - timedelta(hours=1)
    t = OnceTrigger(dt_past, skip_past=True)

    fire_time, status = t.get_first_fire_time()
    assert status == "Completed"
    assert fire_time == datetime.max

    # 迭代应立即结束
    it = iter(t)
    try:
        next(it)
        # 如果能取到值，则应该是 Completed 前抛出 StopIteration，不应到此
        assert False, "OnceTrigger 在 skip_past=True 且过去时间时不应产生迭代值"
    except StopIteration:
        pass


def test_once_trigger_iteration_yields_once_then_stops():
    dt_future = datetime.now() + timedelta(hours=1)
    t = OnceTrigger(dt_future, skip_past=False)

    collected = []
    for x in t:
        collected.append(x)

    # 只迭代一次，且对象本身即为迭代返回值
    assert collected == [t]
    assert t.status == "Completed"


def test_once_decorator_returns_once_trigger():
    dt = datetime.now() + timedelta(hours=2)
    t = once(dt)
    assert isinstance(t, OnceTrigger)
    assert t.trigger_dt == dt


def test_once_trigger_comparisons_by_trigger_dt():
    now = datetime.now()
    t1 = OnceTrigger(now + timedelta(minutes=1))
    t2 = OnceTrigger(now + timedelta(minutes=2))

    assert t1 < t2
    assert t1 <= t2
    assert t2 > t1
    assert t2 >= t1
