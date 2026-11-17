from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.customer import CustomerLocationDto
from app.services.store_service import StoreService

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.get("/location", response_model=CustomerLocationDto, status_code=status.HTTP_200_OK)
def get_customer_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = StoreService(db)
    return service.get_customer_location(current_user.id)


@router.patch("/location", response_model=CustomerLocationDto, status_code=status.HTTP_200_OK)
def update_customer_location(
    req: CustomerLocationDto,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = StoreService(db)
    return service.update_customer_location(current_user.id, req)
