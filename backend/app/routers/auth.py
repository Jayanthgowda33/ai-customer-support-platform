from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password, create_access_token
from app.database import get_db
from app.deps import require_admin, get_current_user
from app.models import Organization, User, Role
from app.schemas import RegisterOrgRequest, LoginRequest, TokenResponse, InviteUserRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-organization", response_model=TokenResponse)
def register_organization(payload: RegisterOrgRequest, db: Session = Depends(get_db)):
    if db.query(Organization).filter(Organization.slug == payload.org_slug).first():
        raise HTTPException(400, "Organization slug already taken")

    org = Organization(name=payload.org_name, slug=payload.org_slug)
    db.add(org)
    db.flush()

    admin = User(
        organization_id=org.id,
        email=payload.admin_email,
        full_name=payload.admin_full_name,
        hashed_password=hash_password(payload.admin_password),
        role=Role.owner,
    )
    db.add(admin)
    db.commit()

    token = create_access_token({"user_id": admin.id, "org_id": org.id})
    return TokenResponse(access_token=token, role=admin.role.value, organization=org.slug)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.slug == payload.org_slug).first()
    if not org:
        raise HTTPException(401, "Invalid organization, email, or password")

    user = (
        db.query(User)
        .filter(User.organization_id == org.id, User.email == payload.email)
        .first()
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid organization, email, or password")

    token = create_access_token({"user_id": user.id, "org_id": org.id})
    return TokenResponse(access_token=token, role=user.role.value, organization=org.slug)


@router.post("/invite-user", response_model=UserOut)
def invite_user(
    payload: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if payload.role not in [r.value for r in Role]:
        raise HTTPException(400, "Invalid role")

    existing = (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id, User.email == payload.email)
        .first()
    )
    if existing:
        raise HTTPException(400, "User with this email already exists in your organization")

    user = User(
        organization_id=current_user.organization_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=Role(payload.role),
    )
    db.add(user)
    db.commit()
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
