from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    created_at: datetime


class HabitCreate(BaseModel):
    name: str
    category: str
    icon: str
    description: str | None = None
    reminder_time: str | None = Field(None, alias="reminderTime")

    model_config = ConfigDict(populate_by_name=True)


class HabitUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    icon: str | None = None
    description: str | None = None
    reminder_time: str | None = Field(None, alias="reminderTime")

    model_config = ConfigDict(populate_by_name=True)


class HabitOut(BaseModel):
    id: str
    name: str
    category: str
    icon: str
    description: str | None = None
    reminder_time: str | None = Field(None, serialization_alias="reminderTime")
    created_at: str = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CompletionCreate(BaseModel):
    date: str


class CompletionOut(BaseModel):
    habit_id: str = Field(serialization_alias="habitId")
    date: str

    model_config = ConfigDict(populate_by_name=True)


class TaskCreate(BaseModel):
    title: str
    category: str
    priority: str = "medium"
    notes: str | None = None
    due_date: str | None = Field(None, alias="dueDate")
    time_block: str | None = Field(None, alias="timeBlock")
    recurring: str | None = None
    recurring_id: str | None = Field(None, alias="recurringId")
    is_recurring_template: bool | None = Field(None, alias="isRecurringTemplate")

    model_config = ConfigDict(populate_by_name=True)


class TaskUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    priority: str | None = None
    notes: str | None = None
    due_date: str | None = Field(None, alias="dueDate")
    time_block: str | None = Field(None, alias="timeBlock")
    recurring: str | None = None
    recurring_id: str | None = Field(None, alias="recurringId")
    is_recurring_template: bool | None = Field(None, alias="isRecurringTemplate")
    status: str | None = None
    completed_at: str | None = Field(None, alias="completedAt")

    model_config = ConfigDict(populate_by_name=True)


class TaskOut(BaseModel):
    id: str
    title: str
    category: str
    priority: str
    notes: str | None = None
    due_date: str | None = Field(None, serialization_alias="dueDate")
    time_block: str | None = Field(None, serialization_alias="timeBlock")
    recurring: str | None = None
    recurring_id: str | None = Field(None, serialization_alias="recurringId")
    is_recurring_template: bool | None = Field(None, serialization_alias="isRecurringTemplate")
    status: str
    created_at: str = Field(serialization_alias="createdAt")
    completed_at: str | None = Field(None, serialization_alias="completedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class JournalUpsert(BaseModel):
    went_well: str | None = Field(None, alias="wentWell")
    improve: str | None = None
    win: str | None = None
    gratitude: list[str] = Field(default_factory=lambda: ["", "", ""])

    model_config = ConfigDict(populate_by_name=True)


class JournalOut(BaseModel):
    id: str
    date: str
    went_well: str | None = Field(None, serialization_alias="wentWell")
    improve: str | None = None
    win: str | None = None
    gratitude: list[str]
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class WellnessPatch(BaseModel):
    water_glasses: int | None = Field(None, alias="waterGlasses")
    water_goal: int | None = Field(None, alias="waterGoal")
    sleep: dict | None = None
    body: dict | None = None

    model_config = ConfigDict(populate_by_name=True)


class WellnessOut(BaseModel):
    date: str
    water_glasses: int = Field(serialization_alias="waterGlasses")
    water_goal: int = Field(serialization_alias="waterGoal")
    sleep: dict | None = None
    body: dict | None = None

    model_config = ConfigDict(populate_by_name=True)


class PrioritiesUpsert(BaseModel):
    items: list[str]

    model_config = ConfigDict(populate_by_name=True)


class PrioritiesOut(BaseModel):
    date: str
    items: list[str]

    model_config = ConfigDict(populate_by_name=True)


class MoodUpsert(BaseModel):
    mood: int = Field(ge=1, le=5)


class MoodOut(BaseModel):
    date: str
    mood: int

    model_config = ConfigDict(populate_by_name=True)


class WeeklyGoalsUpsert(BaseModel):
    goals: list[str]

    model_config = ConfigDict(populate_by_name=True)


class WeeklyGoalsOut(BaseModel):
    week_start: str = Field(serialization_alias="weekStart")
    goals: list[str]

    model_config = ConfigDict(populate_by_name=True)


class ExpenseCreate(BaseModel):
    date: str
    amount: float
    category: str
    note: str | None = None


class ExpenseOut(BaseModel):
    id: str
    date: str
    amount: float
    category: str
    note: str | None = None
    created_at: str = Field(serialization_alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class NoteCreate(BaseModel):
    title: str
    content: str = ""
    pinned: bool = False


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    pinned: bool | None = None


class NoteOut(BaseModel):
    id: str
    title: str
    content: str
    pinned: bool
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class PomodoroCreate(BaseModel):
    date: str
    task_id: str | None = Field(None, alias="taskId")
    duration_mins: int = Field(alias="durationMins")
    type: str
    completed_at: str | None = Field(None, alias="completedAt")

    model_config = ConfigDict(populate_by_name=True)


class PomodoroOut(BaseModel):
    id: str
    date: str
    task_id: str | None = Field(None, serialization_alias="taskId")
    duration_mins: int = Field(serialization_alias="durationMins")
    type: str
    completed_at: str = Field(serialization_alias="completedAt")

    model_config = ConfigDict(populate_by_name=True)


class ActivityCreate(BaseModel):
    type: str
    message: str
    date: str


class ActivityOut(BaseModel):
    id: str
    type: str
    message: str
    date: str
    created_at: str = Field(serialization_alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class NotificationSettings(BaseModel):
    water_reminders: bool = Field(True, alias="waterReminders")
    habit_reminders: bool = Field(True, alias="habitReminders")
    streak_risk_alert: bool = Field(True, alias="streakRiskAlert")
    end_of_day_prompt: bool = Field(True, alias="endOfDayPrompt")
    morning_commitment: bool = Field(True, alias="morningCommitment")
    notifications_enabled: bool = Field(False, alias="notificationsEnabled")

    model_config = ConfigDict(populate_by_name=True)


class SettingsPatch(BaseModel):
    water_goal: int | None = Field(None, alias="waterGoal")
    currency_symbol: str | None = Field(None, alias="currencySymbol")
    notifications: NotificationSettings | None = None

    model_config = ConfigDict(populate_by_name=True)


class SettingsOut(BaseModel):
    water_goal: int = Field(serialization_alias="waterGoal")
    currency_symbol: str = Field(serialization_alias="currencySymbol")
    notifications: NotificationSettings

    model_config = ConfigDict(populate_by_name=True)


class ProgressPatch(BaseModel):
    xp: int | None = None
    level: int | None = None
    daily_awards: dict | None = Field(None, alias="dailyAwards")

    model_config = ConfigDict(populate_by_name=True)


class ProgressOut(BaseModel):
    xp: int
    level: int
    daily_awards: dict = Field(serialization_alias="dailyAwards")

    model_config = ConfigDict(populate_by_name=True)


class BootstrapOut(BaseModel):
    habits: list[HabitOut]
    completions: list[CompletionOut]
    tasks: list[TaskOut]
    meta: dict
    progress: ProgressOut
    top_priorities: list[PrioritiesOut] = Field(serialization_alias="topPriorities")
    journal_entries: list[JournalOut] = Field(serialization_alias="journalEntries")
    wellness_logs: list[WellnessOut] = Field(serialization_alias="wellnessLogs")
    pomodoro_sessions: list[PomodoroOut] = Field(serialization_alias="pomodoroSessions")
    settings: SettingsOut
    mood_logs: list[MoodOut] = Field(serialization_alias="moodLogs")
    weekly_goals: list[WeeklyGoalsOut] = Field(serialization_alias="weeklyGoals")
    expenses: list[ExpenseOut]
    notes: list[NoteOut]
    activity_log: list[ActivityOut] = Field(serialization_alias="activityLog")
    unlocked_achievements: list[str] = Field(serialization_alias="unlockedAchievements")

    model_config = ConfigDict(populate_by_name=True)
