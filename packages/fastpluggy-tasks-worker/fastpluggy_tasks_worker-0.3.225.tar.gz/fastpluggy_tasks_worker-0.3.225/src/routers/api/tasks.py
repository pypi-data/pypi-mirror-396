import inspect

from fastapi import Request, APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastpluggy.core.tools.serialize_tools import serialize_value
from sqlalchemy.orm import Session

from fastpluggy.core.database import get_db
from fastpluggy.core.tools.inspect_tools import process_function_parameters
from fastpluggy.fastpluggy import FastPluggy
from sqlalchemy.sql.operators import truediv

from ..schema import CreateTaskRequest
from ...persistence.models.context import TaskContextDB
from ...persistence.models.report import TaskReportDB
from ...persistence.repository.schedule_monitoring import FilterCriteria
from ...persistence.repository.tasks import get_task_context_reports_and_format
from ...registry.registry import task_registry

api_tasks_router = APIRouter(
    prefix='/api',
)


@api_tasks_router.get("/tasks", name="list_tasks")
async def list_tasks(
        db: Session = Depends(get_db),
        task_name: str | None = Query(None, description="Partial match on task name"),
        task_names: list[str] | None = Query(None, description="Exact task names list"),
        start_time: str | None = Query(None, description="Optional start time (ISO or relative like 1h, 7d)"),
        end_time: str | None = Query(None, description="Optional end time (ISO or relative like now, 1d)"),
        limit: int | None = Query(None, ge=1, le=10000, description="Max number of tasks to fetch")
):
    # Create filter criteria — dates optional, names optional
    filter_criteria = FilterCriteria(
        task_name=task_name,
        task_names=task_names,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )

    # Ensure we pass a concrete limit to repository
    effective_limit = limit if isinstance(limit, int) and limit > 0 else 20
    return get_task_context_reports_and_format(db, filter_criteria=filter_criteria, limit=effective_limit)

@api_tasks_router.get("/task/{task_id}/children", name="get_child_tasks")
def get_child_tasks(task_id: str, db: Session = Depends(get_db), child_status: str | None = Query(None, description="Filter child tasks by status: failed, success, running, queued, created, not_finished, all")):
    try:
        children_ctx = db.query(TaskContextDB).filter(TaskContextDB.parent_task_id == task_id).all()
        child_tasks = []
        error = None
        if children_ctx:
            child_ids = [c.task_id for c in children_ctx]
            reports = db.query(TaskReportDB).filter(TaskReportDB.task_id.in_(child_ids)).all()
            report_map = {r.task_id: r for r in reports}
            for c in children_ctx:
                r = report_map.get(c.task_id)
                child = {
                    "task_id": c.task_id,
                    "task_name": c.task_name,
                    "status": getattr(r, "status", None),
                    "start_time": getattr(r, "start_time", None),
                    "end_time": getattr(r, "end_time", None),
                    "duration": getattr(r, "duration", None),
                    "finished": getattr(r, "finished", False) if r is not None else False,
                }
                child_tasks.append(child)
        # Apply filter
        status_filter = (child_status or "").strip().lower() if child_status else None
        if status_filter and status_filter not in {"all", "failed", "success", "running", "queued", "created", "not_finished"}:
            status_filter = None
        filtered_child_tasks = child_tasks
        if status_filter and status_filter != "all":
            if status_filter == "not_finished":
                filtered_child_tasks = [c for c in child_tasks if not c.get("finished") or c.get("status") in {None, "created", "queued", "running"}]
            else:
                filtered_child_tasks = [c for c in child_tasks if (c.get("status") or "").lower() == status_filter]
        return JSONResponse(serialize_value({"items": filtered_child_tasks, "count": len(filtered_child_tasks), "error": error},serialize_dates=True))
    except Exception as e:
        return JSONResponse({"items": [], "count": 0, "error": str(e)}, status_code=500)


@api_tasks_router.get("/task/{task_id}", name="get_task")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    results = get_task_context_reports_and_format(db, task_id=task_id)
    if not results:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return results[0]


@api_tasks_router.post("/task/{task_id}/retry", name="retry_task")
def retry_task(task_id: str, request: Request, db=Depends(lambda: next(get_db()))):
    context = db.query(TaskContextDB).filter(TaskContextDB.task_id == task_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Task context not found")

    from ...core.utils import path_to_func
    func = path_to_func(context.func_name)
    if not func:
         raise HTTPException(status_code=400, detail={'message': "Function not found in registry", "func_name": context.func_name })

    task_name =f"{context.task_name} (retry)" if "(retry)" not in context.task_name else context.task_name
    # Re-submit the task with parent_task_id
    from fastpluggy_plugin.tasks_worker import TaskWorker
    new_task_id = TaskWorker.submit(
        func,
        args=context.args,
        kwargs=context.kwargs,
        task_name=task_name,
        parent_task_id=task_id,
        task_origin="api-retry",
    )

    return {"task_id": new_task_id}



@api_tasks_router.post("/task/{task_id}/cancel", name="cancel_task")
async def cancel_task(task_id: str):
    """
    Cancel a running task by task_id and mark its status as 'manual_cancel'.
    """
    # Retrieve the global task runner instance.
    runner = FastPluggy.get_global("tasks_worker")
    if not runner:
        raise HTTPException(status_code=500, detail="Task runner is not available")

    # Attempt to cancel the running future.
    success = runner.cancel_task_with_notification(task_id)

    if not success:
        raise HTTPException(status_code=400, detail="Task not running or already finished")

    return {"task_id": task_id, "cancelled": success, "status": "manual_cancel"}

@api_tasks_router.post("/task/submit", name="submit_task")
async def submit_task(request: Request, payload: CreateTaskRequest ):
    from ...registry.registry import task_registry
    func = task_registry.get(payload.function)
    if not func:
        return JSONResponse({"error": f"Function {payload.function} not found"}, status_code=400)

    sig = inspect.signature(func)
    input_kwargs = payload.kwargs
    typed_kwargs = process_function_parameters(func_signature=sig, param_values=input_kwargs)

    from fastpluggy_plugin.tasks_worker import TaskWorker
    task_id = TaskWorker.submit(
        func,
        kwargs=typed_kwargs,
        task_name=payload.name or payload.function,
        topic=payload.topic,
        task_origin="api",
        max_retries=payload.max_retries,
        retry_delay=payload.retry_delay,
        allow_concurrent=payload.allow_concurrent,
    )

    return {"task_id": task_id}


