from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import BootstrapOut
from app.services.bootstrap import build_bootstrap

router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])


@router.get("", response_model=BootstrapOut)
def get_bootstrap(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_bootstrap(user, db)
