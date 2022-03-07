from pydantic import BaseModel


class Employee(BaseModel):
    rfid_card_id: str
    name: str
    position: str
