import pytest
from ewoksutils.task_utils import task_inputs

from ..app.integrate.workflow_executor import WorkflowExecutor

SUM_TASK_WORKFLOW = {
    "graph": {"id": "test"},
    "nodes": [
        {
            "id": "task",
            "task_type": "class",
            "task_identifier": "ewokscore.tests.examples.tasks.sumtask.SumTask",
        },
    ],
}


def test_success(qtbot):
    """Submit one workflow that succeed"""
    executor = WorkflowExecutor()

    inputs = task_inputs(inputs={"a": 1, "b": 2, "delay": 2})

    with qtbot.waitSignal(executor.jobSubmitted, timeout=1000) as blocker:
        job = executor.submit(True, graph=SUM_TASK_WORKFLOW, inputs=inputs)
    assert job is blocker.args[0]

    with qtbot.waitSignal(executor.finished, timeout=20000):
        executor.shutdown(wait=True, cancelFutures=False)

    assert not executor.isJobRunning()

    assert job.isLocal()

    arguments = job.getArguments()
    assert arguments["graph"] == SUM_TASK_WORKFLOW
    assert arguments["inputs"] == inputs

    future = job.getFuture()
    assert future.done()
    assert future.result() == {"result": 3}


def test_cancel(qtbot):
    """Submit 2 workflows and cancel second one"""
    executor = WorkflowExecutor()

    inputs = task_inputs(inputs={"a": 1, "b": 2, "delay": 2})

    job1 = executor.submit(True, graph=SUM_TASK_WORKFLOW, inputs=inputs)
    job2 = executor.submit(True, graph=SUM_TASK_WORKFLOW, inputs=inputs)

    assert executor.isJobRunning()

    future2 = job2.getFuture()
    assert future2.cancel()

    with qtbot.waitSignal(executor.finished, timeout=20000):
        executor.shutdown(wait=True, cancelFutures=False)

    assert job1.getFuture().done()
    assert future2.cancelled()


def test_failed(qtbot):
    """Submit one workflow that raises an exception"""
    executor = WorkflowExecutor()

    workflow = {
        "graph": {"id": "test"},
        "nodes": [
            {
                "id": "task",
                "task_type": "class",
                "task_identifier": "ewokscore.tests.examples.tasks.errorsumtask.ErrorSumTask",
            },
        ],
    }
    inputs = task_inputs(inputs={"raise_error": True})

    job = executor.submit(True, graph=workflow, inputs=inputs)

    with qtbot.waitSignal(executor.finished, timeout=20000):
        executor.shutdown(wait=True, cancelFutures=False)

    future = job.getFuture()
    assert future.done()
    with pytest.raises(RuntimeError):
        future.result()
    assert isinstance(future.exception(), RuntimeError)
