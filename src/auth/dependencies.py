import os

from fastapi import HTTPException, Header, status

from .database import MongoDbWrapper
from .models import Employee

TESTING_VALUE: str = "1111111111"


async def authenticate(rfid_card_id: str = Header(TESTING_VALUE)) -> Employee:
    try:
        if rfid_card_id == TESTING_VALUE and os.getenv("PRODUCTION_ENVIRONMENT", False):
            raise ValueError("Development credentials are not allowed in production environment")

        return await MongoDbWrapper().get_concrete_employee(rfid_card_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )
