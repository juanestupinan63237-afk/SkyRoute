from pydantic import BaseModel
class Activity(BaseModel):
    name: str
    type: str
    duration: int
    price: float