from abc import ABC, abstractmethod

from foodeo_core.settings.models.reservation_settings import ReservationSettings


class IReservationSettings(ABC):

    @abstractmethod
    def get_settings(self) -> ReservationSettings:
        pass
