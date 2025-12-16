from typing import Annotated

from fastapi import Depends, APIRouter, Query, Body
from fastapi.responses import HTMLResponse
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.widgets import CustomTemplateWidget
from sqlalchemy.orm import Session
from starlette.requests import Request

from ...persistence.models.report import TaskReportDB
from ...persistence.repository.schedule_monitoring import FilterCriteria

monitoring_task_duration = APIRouter(
    prefix="/monitoring", tags=["monitoring"]
)


@monitoring_task_duration.get("/task_duration", response_class=HTMLResponse, name="task_duration_analytics")
async def task_duration_analytics(request: Request, view_builder=Depends(get_view_builder), ):
    # Generate the URL for the grouped task-reports API endpoint using url_for
    api_task_reports_grouped_url = request.url_for("get_task_reports_grouped")

    items = [
        CustomTemplateWidget(
            template_name='tasks_worker/monitoring/task_time.html.j2',
            context={
                "request": request,
                "api_task_reports_grouped_url": api_task_reports_grouped_url,
            }
        ),
    ]

    return view_builder.generate(
        request,
        widgets=items
    )


# Custom dependency to build FilterCriteria from plain query params (strings/lists)
async def build_filter_criteria(
        task_name: str | None = Query(None, description="Partial match on task name (function)"),
        task_names: list[str] | None = Query(None, description="Exact task names (list)"),
        start_time: str | None = Query(None, description="Start time (ISO or relative like 1h, 7d)"),
        end_time: str | None = Query(None, description="End time (ISO or relative like now, 1d)"),
        limit: int | None = Query(None, ge=1, le=10000, description="Max number of reports to fetch"),
        page: int = Query(1, ge=1),
        page_size: int = Query(25, ge=1, le=100),
) -> FilterCriteria:
    # Let the Pydantic validators parse relative/ISO times
    return FilterCriteria(
        task_name=task_name,
        task_names=task_names,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        page=page,
        page_size=page_size,
    )


@monitoring_task_duration.post("/task_duration/group_by_name", name="get_task_reports_grouped")
async def get_task_reports_grouped(
        request: Request,
        filter_criteria: Annotated[FilterCriteria, Depends(build_filter_criteria)],
        details: bool = Query(False, description="Include detailed list of tasks per group"),
        _body: dict | None = Body(None),
        db: Session = Depends(get_db)
):
    """
    Return aggregated analytics grouped by task function name.
    Response format:
    {
      "items": [
         {"task_name": str, "count": int, "avg_duration": float, "min_duration": float, "max_duration": float,
          "success_count": int, "success_percent": float, "details": [ ... optional list of tasks ... ]}
      ],
      "total_executions": int,
      "total_success_percent": float,
      "total_avg_duration": float
    }
    """
    # Base query with optional filters
    query = db.query(TaskReportDB)

    if filter_criteria.task_name:
        query = query.filter(TaskReportDB.function.ilike(f"%{filter_criteria.task_name}%"))

    if filter_criteria.task_names:
        query = query.filter(TaskReportDB.function.in_(filter_criteria.task_names))

    if filter_criteria.start_time:
        query = query.filter(TaskReportDB.start_time >= filter_criteria.start_time)

    if filter_criteria.end_time:
        query = query.filter(TaskReportDB.end_time <= filter_criteria.end_time)

    query = query.order_by(TaskReportDB.start_time.desc())
    if filter_criteria.limit:
        query = query.limit(int(filter_criteria.limit))

    rows = query.all()

    # Aggregate in Python (small result sets thanks to limit; simpler to implement cross-DB)
    grouped = {}
    total_duration = 0.0
    total_executions = 0
    total_success = 0

    for r in rows:
        name = r.function
        if name not in grouped:
            grouped[name] = {
                "task_name": name,
                "count": 0,
                "total_duration": 0.0,
                "min_duration": float('inf'),
                "max_duration": 0.0,
                "success_count": 0,
                "details": [] if details else None,
            }
        g = grouped[name]
        d = float(r.duration or 0)
        g["count"] += 1
        g["total_duration"] += d
        g["min_duration"] = min(g["min_duration"], d)
        g["max_duration"] = max(g["max_duration"], d)
        if (r.status or "").lower() == "success":
            g["success_count"] += 1
        if details:
            g["details"].append({
                "id": r.id,
                "function": r.function,
                "duration": r.duration,
                "status": r.status,
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "end_time": r.end_time.isoformat() if r.end_time else None,
            })
        total_duration += d
        total_executions += 1
        if (r.status or "").lower() == "success":
            total_success += 1

    items = []
    for name, g in grouped.items():
        count = g["count"] or 1
        avg = g["total_duration"] / count
        success_percent = (g["success_count"] / count) * 100.0
        min_d = 0.0 if g["min_duration"] == float('inf') else g["min_duration"]
        item = {
            "task_name": name,
            "count": g["count"],
            "avg_duration": avg,
            "min_duration": min_d,
            "max_duration": g["max_duration"],
            "success_count": g["success_count"],
            "success_percent": success_percent,
        }
        if details:
            item["details"] = g["details"]
        items.append(item)

    overall_avg = (total_duration / total_executions) if total_executions else 0.0
    overall_success_percent = (total_success / total_executions * 100.0) if total_executions else 0.0

    return {
        "items": sorted(items, key=lambda x: x["avg_duration"], reverse=True),
        "total_executions": total_executions,
        "total_success_percent": overall_success_percent,
        "total_avg_duration": overall_avg,
    }
