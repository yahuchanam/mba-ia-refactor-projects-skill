from datetime import timedelta

from errors import ApiError
from services.serializers import serialize_user
from utils.datetime_utils import utc_now


class ReportService:
    def __init__(self, report_repository, user_repository):
        self.reports = report_repository
        self.users = user_repository

    def summary(self):
        now = utc_now()
        since = now - timedelta(days=7)
        status_counts = self.reports.task_counts_by_status()
        priority_counts = self.reports.task_counts_by_priority()
        overdue_tasks = self.reports.overdue_tasks(now)

        user_stats = []
        for user_id, user_name, total, completed in self.reports.user_productivity():
            completed = completed or 0
            user_stats.append(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": (
                        round((completed / total) * 100, 2) if total else 0
                    ),
                }
            )

        return {
            "generated_at": str(now),
            "overview": self.reports.entity_counts(),
            "tasks_by_status": {
                "pending": status_counts.get("pending", 0),
                "in_progress": status_counts.get("in_progress", 0),
                "done": status_counts.get("done", 0),
                "cancelled": status_counts.get("cancelled", 0),
            },
            "tasks_by_priority": {
                "critical": priority_counts.get(1, 0),
                "high": priority_counts.get(2, 0),
                "medium": priority_counts.get(3, 0),
                "low": priority_counts.get(4, 0),
                "minimal": priority_counts.get(5, 0),
            },
            "overdue": {
                "count": len(overdue_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (now - task.due_date).days,
                    }
                    for task in overdue_tasks
                ],
            },
            "recent_activity": {
                "tasks_created_last_7_days": self.reports.count_recent_created(since),
                "tasks_completed_last_7_days": self.reports.count_recent_completed(
                    since
                ),
            },
            "user_productivity": user_stats,
        }

    def user_report(self, user_id):
        user = self.users.get(user_id)
        if not user:
            raise ApiError("Usuário não encontrado", 404)

        statistics = self.reports.user_task_statistics(user_id, utc_now())
        total = statistics.total or 0
        done = statistics.done or 0
        return {
            "user": {
                key: value
                for key, value in serialize_user(user).items()
                if key in {"id", "name", "email"}
            },
            "statistics": {
                "total_tasks": total,
                "done": done,
                "pending": statistics.pending or 0,
                "in_progress": statistics.in_progress or 0,
                "cancelled": statistics.cancelled or 0,
                "overdue": statistics.overdue or 0,
                "high_priority": statistics.high_priority or 0,
                "completion_rate": round((done / total) * 100, 2) if total else 0,
            },
        }
