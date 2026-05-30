from datetime import date

from sqlalchemy.orm import Session

from app.models import (
    ActivityLogEntry,
    Expense,
    Habit,
    HabitCompletion,
    JournalEntry,
    MoodLog,
    Note,
    PomodoroSession,
    Task,
    TopPriority,
    User,
    UserAchievement,
    UserProgress,
    UserSettings,
    WeeklyGoal,
    WellnessLog,
)
from app.routers.activity import _activity_out
from app.routers.expenses import _expense_out
from app.routers.habits import _habit_out
from app.routers.journal import _journal_out
from app.routers.me import DEFAULT_NOTIFICATIONS, _get_or_create_settings, _settings_out
from app.routers.notes import _note_out
from app.routers.pomodoro import _pomodoro_out
from app.routers.progress import _get_or_create_progress, _progress_out
from app.routers.tasks import _task_out
from app.schemas import BootstrapOut, CompletionOut, MoodOut, PrioritiesOut, WeeklyGoalsOut, WellnessOut
from app.schemas.serializers import uuid_str


def build_bootstrap(user: User, db: Session) -> BootstrapOut:
    habits = db.query(Habit).filter(Habit.user_id == user.id).order_by(Habit.created_at).all()
    habit_ids = [h.id for h in habits]
    completions: list[CompletionOut] = []
    if habit_ids:
        rows = db.query(HabitCompletion).filter(HabitCompletion.habit_id.in_(habit_ids)).all()
        completions = [CompletionOut(habit_id=uuid_str(c.habit_id), date=c.date) for c in rows]

    tasks = db.query(Task).filter(Task.user_id == user.id).order_by(Task.created_at).all()
    journal_entries = (
        db.query(JournalEntry).filter(JournalEntry.user_id == user.id).order_by(JournalEntry.date).all()
    )
    wellness_logs = db.query(WellnessLog).filter(WellnessLog.user_id == user.id).all()
    top_priorities = db.query(TopPriority).filter(TopPriority.user_id == user.id).all()
    mood_logs = db.query(MoodLog).filter(MoodLog.user_id == user.id).all()
    weekly_goals = db.query(WeeklyGoal).filter(WeeklyGoal.user_id == user.id).all()
    expenses = db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.created_at.desc()).all()
    notes = (
        db.query(Note)
        .filter(Note.user_id == user.id)
        .order_by(Note.pinned.desc(), Note.updated_at.desc())
        .all()
    )
    pomodoro_sessions = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user.id)
        .order_by(PomodoroSession.completed_at.desc())
        .all()
    )
    activity_log = (
        db.query(ActivityLogEntry)
        .filter(ActivityLogEntry.user_id == user.id)
        .order_by(ActivityLogEntry.created_at.desc())
        .limit(200)
        .all()
    )
    achievements = db.query(UserAchievement).filter(UserAchievement.user_id == user.id).all()

    settings = _get_or_create_settings(user, db)
    progress = _get_or_create_progress(user, db)

    return BootstrapOut(
        habits=[_habit_out(h) for h in habits],
        completions=completions,
        tasks=[_task_out(t) for t in tasks],
        meta={"lastOpenedDate": date.today().isoformat()},
        progress=_progress_out(progress),
        top_priorities=[PrioritiesOut(date=p.date, items=p.items) for p in top_priorities],
        journal_entries=[_journal_out(e) for e in journal_entries],
        wellness_logs=[
            WellnessOut(
                date=w.date,
                water_glasses=w.water_glasses,
                water_goal=w.water_goal,
                sleep=w.sleep,
                body=w.body,
            )
            for w in wellness_logs
        ],
        pomodoro_sessions=[_pomodoro_out(s) for s in pomodoro_sessions],
        settings=_settings_out(settings),
        mood_logs=[MoodOut(date=m.date, mood=m.mood) for m in mood_logs],
        weekly_goals=[WeeklyGoalsOut(week_start=g.week_start, goals=g.goals) for g in weekly_goals],
        expenses=[_expense_out(e) for e in expenses],
        notes=[_note_out(n) for n in notes],
        activity_log=[_activity_out(a) for a in activity_log],
        unlocked_achievements=[a.achievement_id for a in achievements],
    )
