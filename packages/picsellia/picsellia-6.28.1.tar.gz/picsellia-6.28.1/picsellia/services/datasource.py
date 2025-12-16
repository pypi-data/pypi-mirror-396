from uuid import UUID

from orjson import orjson

from picsellia import exceptions
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.datasource import DataSource
from picsellia.utils import filter_payload


class DataSourceService:
    @classmethod
    def create_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        params = {"name": name}
        r = connexion.post(
            f"/api/organization/{organization_id}/datasources",
            data=orjson.dumps(params),
        ).json()
        return DataSource(connexion, r)

    @classmethod
    def get_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        params = {"name": name}
        r = connexion.get(
            f"/api/organization/{organization_id}/datasources/find",
            params=params,
        ).json()
        return DataSource(connexion, r)

    @classmethod
    def get_or_create_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        try:
            return cls.get_datasource(connexion, organization_id, name)
        except exceptions.ResourceNotFoundError:
            return cls.create_datasource(connexion, organization_id, name)

    @classmethod
    def list_datasources(
        cls,
        connexion: Connexion,
        organization_id: UUID,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[str] | None = None,
    ) -> list[DataSource]:
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = connexion.get(
            f"/api/organization/{organization_id}/datasources",
            params=params,
        ).json()
        return [DataSource(connexion, item) for item in r["items"]]
