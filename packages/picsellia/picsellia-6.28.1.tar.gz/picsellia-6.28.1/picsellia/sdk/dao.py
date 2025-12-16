from abc import ABC, abstractmethod
from uuid import UUID

from picsellia.exceptions import UndefinedObjectError
from picsellia.sdk.connexion import Connexion
from picsellia.types.schemas import DaoSchema


class Dao(ABC):
    def __init__(self, connexion: Connexion, data: dict) -> None:
        self._connexion = connexion
        schema: DaoSchema = self.refresh(data)
        if schema.id is None:  # pragma: no cover
            raise UndefinedObjectError(
                "This object has no id. Something went wrong while retrieving data from platform."
            )
        self._id = schema.id

    @property
    def connexion(self) -> Connexion:
        """Connexion object used to connect to Picsellia platform"""
        return self._connexion

    @property
    def id(self) -> UUID:
        """UUID in Picsellia platform"""
        return self._id

    @property
    def ids(self) -> list[UUID]:
        return [self._id]

    def __str__(self) -> str:
        return f"Platform object (id: {self.id})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, type(self)):
            __o: Dao
            return self._id == __o.id and self._connexion == __o.connexion

        return False

    @abstractmethod
    def refresh(self, data: dict) -> DaoSchema:
        """
        Refresh the properties of this object with given data.
        This will not update the object in Picsellia database.
        It is only useful in some case, if you want to manually override attributes of this object.
        """
        pass

    @abstractmethod
    def sync(self) -> dict:
        """
        Retrieve the data of this object and reset properties.
        Useful when objects were retrieved a long time ago and to ensures synchronization with Picsellia database.
        This will also return some data stored in database, not used in SDK, as a dict.
        """
        pass
