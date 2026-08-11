from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import require_admin, get_current_user
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).filter(User.organization_id == current_user.organization_id).all()


@router.get("/me")
def my_org(current_user: User = Depends(get_current_user)):
    org = current_user.organization
    return {"id": org.id, "name": org.name, "slug": org.slug}
