import logging
from uuid import UUID

import orjson
from beartype import beartype

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.label_group import LabelGroup
from picsellia.types.schemas import LabelSchema

logger = logging.getLogger("picsellia")


class Label(Dao):
    def __init__(
        self, connexion: Connexion, dataset_version_id: UUID, data: dict
    ) -> None:
        Dao.__init__(self, connexion, data)
        self._dataset_version_id = dataset_version_id

    @property
    def name(self) -> str:
        """Name of this (Label)"""
        return self._name

    @property
    def group_id(self) -> UUID | None:
        """Group ID of this (Label)"""
        return self._group_id

    def __str__(self):
        return f"{Colors.GREEN}Label '{self.name}'{Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/api/label/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> LabelSchema:
        schema = LabelSchema(**data)
        self._name = schema.name
        self._group_id = schema.group_id
        return schema

    @exception_handler
    @beartype
    def update(self, name: str = None, group_id: UUID = None) -> None:
        """Update this (Label) with a new name or with a new group.

        Examples:
            ```python
            a_label.update(name="new name")
            ```

        Arguments:
            name (str, optional): New name of this (Label)
            group_id (UUID, optional): New group of this (Label)
        """
        payload = {}
        if name:
            payload["name"] = name
        if group_id:
            payload["group_id"] = group_id
        r = self.connexion.patch(
            f"/api/label/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this (Label) from the platform.
        All annotations shape with this label will be deleted!
        This is a very dangerous move.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            this_label.delete()
            ```
        """
        self.connexion.delete(f"/api/label/{self.id}")
        logger.info(f"{self} deleted.")

    @exception_handler
    @beartype
    def get_group(self) -> LabelGroup | None:
        """Get (LabelGroup) parent of this (Label). If no (LabelGroup) is set, return None.

        Examples:
            ```python
            group = label_1.get_group()
            label_2.set_group(group)
            ```

        Returns:
            a (LabelGroup) if there is a parent, else None
        """
        if not self._group_id:
            return None

        r = self.connexion.get(f"/api/label/group/{self._group_id}").json()
        return LabelGroup(self.connexion, self._dataset_version_id, r)

    @exception_handler
    @beartype
    def set_group(self, group: LabelGroup) -> None:
        """Update this (Label) with a new group.

        Examples:
            ```python
            a_label.update(name="new name")
            ```

        Arguments:
            group (LabelGroup): new group of this (Label)
        """
        if group.dataset_version_id != self._dataset_version_id:
            raise ValueError("Cannot set a group from a different DatasetVersion")

        return self.update(group_id=group.id)

    @exception_handler
    @beartype
    def get_skeleton(self) -> dict:
        """Get the skeleton of this (Label).
        Returns:
            a dict with key edges and vertices
        """
        return self.connexion.get(f"/api/label/{self.id}/skeleton").json()

    @exception_handler
    @beartype
    def set_skeleton(self, vertices: list[str], edges: list[list[int]]) -> None:
        """Set the skeleton of this (Label).

        Arguments:
            vertices (list[str]): names of this skeleton vertices
            edges (list of 2 ints): edges are links between vertices with indexes starting at 1!
        """
        payload = {"vertices": vertices, "edges": edges}
        self.connexion.post(
            f"/api/label/{self.id}/skeleton", data=orjson.dumps(payload)
        )
        logger.info(f"{self}' skeleton updated")
