from app.schemas.common import CamelModel


class CustomerLocationDto(CamelModel):
    address: str = "Indiranagar, Bangalore"
    lat: float = 12.9784
    lng: float = 77.6408
