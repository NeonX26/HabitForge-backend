from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User, UserSettings
from app.schemas import NotificationSettings, SettingsOut, SettingsPatch

router = APIRouter(prefix="/me", tags=["me"])

DEFAULT_NOTIFICATIONS = {
    "waterReminders": True,
    "habitReminders": True,
    "streakRiskAlert": True,
    "endOfDayPrompt": True,
    "morningCommitment": True,
    "notificationsEnabled": False,
}


def _settings_out(s: UserSettings) -> SettingsOut:
    notif = s.notifications or DEFAULT_NOTIFICATIONS
    return SettingsOut(
        water_goal=s.water_goal,
        currency_symbol=s.currency_symbol,
        notifications=NotificationSettings(**notif),
    )


def _get_or_create_settings(user: User, db: Session) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if settings is None:
        settings = UserSettings(
            user_id=user.id,
            water_goal=8,
            currency_symbol="₹",
            notifications=DEFAULT_NOTIFICATIONS,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=SettingsOut)
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _settings_out(_get_or_create_settings(user, db))


@router.patch("/settings", response_model=SettingsOut)
def patch_settings(
    body: SettingsPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = _get_or_create_settings(user, db)
    if body.water_goal is not None:
        settings.water_goal = body.water_goal
    if body.currency_symbol is not None:
        settings.currency_symbol = body.currency_symbol
    if body.notifications is not None:
        current = settings.notifications or DEFAULT_NOTIFICATIONS
        current.update(body.notifications.model_dump(by_alias=True))
        settings.notifications = current
    db.commit()
    db.refresh(settings)
    return _settings_out(settings)
