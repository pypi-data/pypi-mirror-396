import logging
import os
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import IO, Any
from uuid import UUID

import orjson
import requests
from beartype import beartype
from picsellia_connexion_services import TokenServiceConnexion
from requests import Session
from requests.exceptions import ConnectionError

import picsellia.exceptions as exceptions
from picsellia import __version__
from picsellia.decorators import exception_handler, retry
from picsellia.services.upload.file import FileUploader
from picsellia.types.enums import ObjectDataType
from picsellia.utils import handle_response

logger = logging.getLogger("picsellia")

DEFAULT_TIMEOUT = 30

DATA_TYPE = str | bytes | Mapping[str, Any] | Iterable[tuple[str, str, None]] | IO


class Connexion(TokenServiceConnexion):
    def __init__(
        self,
        host: str,
        api_token: str,
        content_type: str = "application/json",
        session: Session | None = None,
    ) -> None:
        super().__init__(
            host, api_token, authorization_key="Bearer", content_type=content_type
        )
        self._connector_id = None
        self._organization_id = None
        self.add_header("User-Agent", f"Picsellia-SDK/{__version__}")
        if session is not None:
            self.session = session

    @property
    def connector_id(self):
        if self._connector_id is None:
            raise exceptions.NoConnectorFound(
                "This organization has no default connector, and connect retrieve and upload files."
            )
        return self._connector_id

    @connector_id.setter
    def connector_id(self, value):
        self._connector_id = value

    @property
    def organization_id(self):
        return self._organization_id

    @organization_id.setter
    def organization_id(self, value):
        self._organization_id = value
        self.add_header("X-Picsellia-Organization", str(self._organization_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Connexion):
            return self.host == __o.host and self.api_token == __o.api_token

        return False

    @handle_response
    @retry(requests.ConnectionError)
    def get(self, path: str, params: dict | None = None, stream=False):
        return super().get(path=path, params=params, stream=stream)

    @handle_response
    @retry(requests.ConnectionError)
    def xget(
        self,
        path: str,
        data: (
            None
            | str
            | bytes
            | Mapping[str, Any]
            | Iterable[tuple[str, str, None]]
            | IO
        ) = None,
        params: dict | None = None,
        stream=False,
    ):
        return super().xget(path=path, data=data, params=params, stream=stream)

    @handle_response
    @retry(requests.ConnectionError)
    def post(
        self,
        path: str,
        data: (
            str
            | bytes
            | Mapping[str, Any]
            | Iterable[tuple[str, str, None]]
            | IO
            | None
        ) = None,
        params: dict | None = None,
        files: Any | None = None,
    ):
        return super().post(path=path, data=data, params=params, files=files)

    @handle_response
    @retry(requests.ConnectionError)
    def put(
        self,
        path: str,
        data: DATA_TYPE | None = None,
        params: dict | None = None,
    ):
        return super().put(path=path, data=data, params=params)

    @handle_response
    @retry(requests.ConnectionError)
    def patch(
        self,
        path: str,
        data: DATA_TYPE | None = None,
        params: dict | None = None,
    ):
        return super().patch(path=path, data=data, params=params)

    @handle_response
    @retry(requests.ConnectionError)
    def delete(
        self,
        path: str,
        data: DATA_TYPE | None = None,
        params: dict | None = None,
    ):
        return super().delete(path=path, data=data, params=params)

    ##############################################################
    # ------------------------- UPLOAD ------------------------- #
    ##############################################################
    @exception_handler
    @beartype
    def _generate_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        connector_id: UUID | None = None,
        context: dict[str, UUID] | None = None,
        upload_dir: str | None = None,
    ) -> str:
        if connector_id is None:
            connector_id = self.connector_id

        payload: dict[str, Any] = {"filename": filename, "type": object_name_type}
        if context:
            payload["context"] = context

        if upload_dir:
            payload["upload_dir"] = upload_dir

        r = self.post(
            path=f"/api/organization/{self.organization_id}/connector/{connector_id}/generate_object_name",
            data=orjson.dumps(payload),
        ).json()
        return r["object_name"]

    @beartype
    def generate_data_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        connector_id: UUID | None = None,
        upload_dir: str | None = None,
    ):
        if object_name_type not in [
            ObjectDataType.DATA,
            ObjectDataType.DATA_PROJECTION,
        ]:
            raise RuntimeError(
                f"Cannot generate data object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename, object_name_type, connector_id, upload_dir=upload_dir
        )

    @beartype
    def generate_dataset_version_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        dataset_version_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type not in [ObjectDataType.CAMPAIGN_FILE]:
            raise RuntimeError(
                f"Cannot generate dataset version object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id,
            context={"dataset_version_id": dataset_version_id},
        )

    @beartype
    def generate_deployment_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        deployment_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type not in [ObjectDataType.REVIEW_CAMPAIGN_FILE]:
            raise RuntimeError(
                f"Cannot generate deployment object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id,
            context={"deployment_id": deployment_id},
        )

    @beartype
    def generate_job_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        job_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type not in [ObjectDataType.LOGGING]:
            raise RuntimeError(
                f"Cannot generate job object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"job_id": job_id},
        )

    @beartype
    def generate_experiment_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        experiment_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type not in (
            ObjectDataType.ARTIFACT,
            ObjectDataType.LOG_IMAGE,
            ObjectDataType.LOGGING,
        ):
            raise RuntimeError(
                f"Cannot generate experiment object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"experiment_id": experiment_id},
        )

    @beartype
    def generate_model_version_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        model_version_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type not in (
            ObjectDataType.MODEL_THUMB,
            ObjectDataType.MODEL_FILE,
        ):
            raise RuntimeError(
                f"Cannot generate model version object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"model_version_id": model_version_id},
        )

    @beartype
    def generate_report_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        dataset_version_id: UUID,
        report_id: UUID,
        connector_id: UUID | None = None,
    ):
        if object_name_type != ObjectDataType.AGENTS_REPORT:
            raise RuntimeError(
                f"Cannot generate report object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"report_id": report_id, "dataset_version_id": dataset_version_id},
        )

    def upload_file(
        self,
        object_name: str,
        path: str | Path,
        connector_id: UUID | None = None,
    ) -> tuple[requests.Response, bool, str]:
        """Upload a single file to the server.
        If file is bigger than 5Mb, it will send it by multipart.

        Arguments:
            path (str): Absolute path to the file
            object_name (str): Destination object name.
            connector_id (UUID): Connector on which you need to upload file, if it's not default connector.
        """
        if connector_id is None:
            connector_id = self.connector_id

        uploader = FileUploader(connector_id, self.session, self.host, self.headers)
        return uploader.upload(object_name, path)

    ##############################################################
    # ------------------------ DOWNLOAD ------------------------ #
    ##############################################################
    def init_download(self, object_name: str, connector_id: UUID | None = None) -> str:
        """Retrieve a presigned url of this object name in order to download it"""
        if connector_id is None:
            connector_id = self.connector_id

        payload = {"object_name": object_name}
        r = self.post(
            path=f"/api/object-storage/{connector_id}/retrieve_presigned_url",
            data=orjson.dumps(payload),
        )

        if r.status_code != 200:
            raise exceptions.DistantStorageError("Errors while getting a presigned url")

        r = r.json()
        if "presigned_url" not in r:
            raise exceptions.DistantStorageError(
                "Errors while getting a presigned url. Unparsable response"
            )

        return r["presigned_url"]

    def do_download_file(
        self,
        path: str | Path,
        url: str,
        is_large: bool,
        force_replace: bool,
        retry_count: int = 1,
    ) -> bool:
        try:
            return self._do_download_file(path, url, is_large, force_replace)
        except (exceptions.NetworkError, ConnectionError) as e:
            # Here for retro compatibility
            raise exceptions.DownloadError(
                f"Could not download {url} into {path}"
            ) from e

    @retry((exceptions.NetworkError, ConnectionError))
    def _do_download_file(
        self,
        path: str | Path,
        url: str,
        is_large: bool,
        force_replace: bool,
    ) -> bool:
        """Retrieve a presigned url of this object name in order to download it"""
        if os.path.exists(path) and not force_replace:
            return False

        parent_path = Path(path).parent.absolute()
        os.makedirs(parent_path, exist_ok=True)

        response = self.session.get(url, stream=is_large, timeout=DEFAULT_TIMEOUT)

        if response.status_code == 429 or (500 <= response.status_code < 600):
            raise exceptions.NetworkError(
                f"Response status code is {response.status_code}. Could not get {url}"
            )

        response.raise_for_status()

        total_length = response.headers.get("content-length")
        if total_length is None:
            raise exceptions.NetworkError(
                "Downloaded content is empty but response is 200"
            )

        with open(path, "wb") as handler:
            if not is_large:
                handler.write(response.content)
            else:
                for data in response.iter_content(chunk_size=4096):
                    handler.write(data)

        return True
