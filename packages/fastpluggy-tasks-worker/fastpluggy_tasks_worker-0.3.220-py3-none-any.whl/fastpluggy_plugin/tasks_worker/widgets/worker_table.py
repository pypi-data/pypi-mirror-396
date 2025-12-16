
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastpluggy.core.widgets import AbstractWidget

from ..broker.factory import get_broker
from ..broker.contracts import BrokerUtils


class WorkerTableView(AbstractWidget):
    """
    Full custom widget with its own Jinja template, similar to TaskFormView.
    It renders a Tabler-styled table of workers with an Info modal per row (modal markup in template).
    """

    widget_type = "worker_table_view"
    template_name: str = "tasks_worker/widgets/worker_table.html.j2"

    # Default columns mapping for workers table
    DEFAULT_FIELDS = [
        "worker_id",
        "host",
        "pid",
        "role",
        "capacity",
        "running",
        "stale",
        "topics",
        "last_seen_min",
        "details",
    ]

    DEFAULT_HEADERS: Dict[str, str] = {
        "worker_id": "Worker ID",
        "host": "Host",
        "pid": "PID",
        "role": "Role",
        "capacity": "Capacity",
        "running": "Running",
        "stale": "Stale",
        "topics": "Topics",
        "last_seen_min": "Last seen",
        "details": "Info",
    }

    def __init__(
        self,
        *,
        title: str = "Workers",
        data: Optional[List[Dict[str, Any]]] = None,
        fields: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        broker: Optional[Any] = None,
        include_tasks: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self._input_data = data
        self.fields = fields or self.DEFAULT_FIELDS
        self.headers = dict(self.DEFAULT_HEADERS)
        if headers:
            self.headers.update(headers)
        self.broker = broker
        self.include_tasks = include_tasks
        # processed attributes for template
        self.data: List[Dict[str, Any]] = []

    def _format_last_seen(self, last_heartbeat: Optional[Any], now_utc: Optional[datetime] = None) -> str:
        """Return a safe HTML string with a colored badge for minutes since last heartbeat.
        Accepts ISO string or datetime for last_heartbeat.
        """
        try:
            if now_utc is None:
                now_utc = BrokerUtils.now_utc()
            hb = last_heartbeat
            if isinstance(hb, str):
                dt = BrokerUtils.parse_date(hb)
                ls_text = hb
            elif isinstance(hb, datetime):
                dt = hb
                ls_text = hb.isoformat()
            else:
                dt = None
                ls_text = ""
            if dt is None:
                return '<span class="badge bg-secondary" title="No heartbeat">-</span>'
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            minutes = int(max(0, (now_utc - dt).total_seconds()) // 60)
            # Severity coloring
            if minutes <= 2:
                cls = "bg-green"
            elif minutes <= 5:
                cls = "bg-yellow"
            else:
                cls = "bg-red"
            return f'<span class="badge {cls}" title="Last heartbeat: {ls_text}">{minutes}m</span>'
        except Exception:
            return '<span class="badge bg-secondary">-</span>'

    def _make_dialog_id(self, row: Dict[str, Any]) -> Optional[str]:
        """Create a stable, sanitized dialog id for a worker row."""
        try:
            base_id = str(row.get("worker_id") or f"{row.get('host','')}-{row.get('pid','')}")
            safe_id = "".join(ch if (ch.isalnum() or ch in ("-", "_")) else "-" for ch in base_id)
            return f"wkdlg-{safe_id}"
        except Exception:
            return None

    def _enrich_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        now_utc = BrokerUtils.now_utc()
        out: List[Dict[str, Any]] = []
        for w in rows:
            w = dict(w)
            # compute last_seen_min safe HTML string (template will mark safe)
            w["last_seen_min"] = self._format_last_seen(w.get("last_heartbeat"), now_utc)

            # Provide a stable dialog id for the template; modal markup lives in template.
            dlg = self._make_dialog_id(w)
            if dlg:
                w["dialog_id"] = dlg

            out.append(w)
        return out

    def process(self, **kwargs):
        # load data if not provided
        data: Optional[List[Dict[str, Any]]] = self._input_data
        if data is None:
            try:
                b = self.broker or get_broker()
                items = b.get_workers(include_tasks=self.include_tasks) or []
                data = [asdict(i) if is_dataclass(i) else i for i in items]
            except Exception:
                data = []
        data = list(data or [])
        self.data = self._enrich_rows(data)
        # expose headers/fields to template
        self.use_fields = self.fields
        self.use_headers = self.headers
        self.table_id = kwargs.get("table_id") or "workers-table"
        self.card_class = kwargs.get("card_class") or "card"
        self.table_class = kwargs.get("table_class") or "table table-vcenter"
