"""Files resource for the Addepar API."""
import json
import logging
from typing import Any, Dict, List, Optional, Union

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Valid included_objects filter values
INCLUDED_OBJECTS_VALUES = {"FILES_ONLY", "FOLDERS_ONLY", "FILES_AND_FOLDERS"}


class FilesResource(BaseResource):
    """
    Resource for Addepar Files API.

    Manage files and folders stored in Addepar, including uploading,
    downloading, archiving, and associating files with entities/groups.

    CRUD Methods:
        - get_file() - Get a single file/folder
        - list_files() - List files/folders with filters
        - download_file() - Download file content
        - upload_file() - Upload a file
        - update_file() - Rename or move a file
        - delete_file() - Delete/archive a file

    Archive Methods:
        - get_archived_file() - Get an archived file
        - list_archived_files() - List archived files/folders
        - download_archived_file() - Download archived file content

    Associated Groups Methods:
        - get_associated_groups() - Get groups associated with file
        - add_associated_groups() - Add groups to file
        - replace_associated_groups() - Replace all associated groups
        - remove_associated_groups() - Remove groups from file

    Associated Entities Methods:
        - get_associated_entities() - Get entities associated with file
        - add_associated_entities() - Add entities to file
        - replace_associated_entities() - Replace all associated entities
        - remove_associated_entities() - Remove entities from file
    """

    # =========================================================================
    # CRUD Methods
    # =========================================================================

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get a single file or folder by ID.

        Args:
            file_id: The ID of the file or folder to retrieve.

        Returns:
            The file resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/files/{file_id}")
        data = response.json()
        file = data.get("data", {})
        logger.debug(f"Retrieved file {file_id}")
        return file

    def list_files(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        entity_id: Optional[str] = None,
        group_id: Optional[str] = None,
        included_objects: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all files and/or folders with pagination and optional filters.

        Args:
            page_limit: Results per page (default: 500, max: 2000).
            created_after: Files created after date (ISO 8601).
            created_before: Files created before date (ISO 8601).
            entity_id: Filter by associated entity ID.
            group_id: Filter by associated group ID.
            included_objects: What to include - "FILES_ONLY" (default),
                "FOLDERS_ONLY", or "FILES_AND_FOLDERS".
            parent_folder_id: Filter by parent folder ID.

        Returns:
            List of file/folder resource objects.
        """
        params: Dict[str, Any] = {}

        if created_after is not None:
            params["filter[files][createdAfter]"] = created_after
        if created_before is not None:
            params["filter[files][createdBefore]"] = created_before
        if entity_id is not None:
            params["filter[files][entityId]"] = entity_id
        if group_id is not None:
            params["filter[files][groupId]"] = group_id
        if included_objects is not None:
            params["filter[files][includedObjects]"] = included_objects
        if parent_folder_id is not None:
            params["filter[files][parentFolderId]"] = parent_folder_id

        files = list(
            self._paginate("/files", page_limit=page_limit, params=params if params else None)
        )
        logger.debug(f"Listed {len(files)} files")
        return files

    def download_file(self, file_id: str) -> bytes:
        """
        Download a file's content.

        Args:
            file_id: The ID of the file to download.

        Returns:
            The raw file content as bytes.
        """
        response = self._get(f"/files/{file_id}/download")
        logger.debug(f"Downloaded file {file_id}")
        return response.content

    def upload_file(
        self,
        file_data: Union[bytes, str],
        name: str,
        *,
        parent_folder_id: Optional[str] = None,
        file_path: Optional[str] = None,
        entity_ids: Optional[List[str]] = None,
        group_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a new file.

        Args:
            file_data: File content as bytes, or path to file on disk.
            name: File name with extension (must match actual file type).
            parent_folder_id: Optional ID of folder to upload to.
            file_path: Optional path string (e.g., "Sample/Folder/Path/").
            entity_ids: Optional list of entity IDs to associate.
            group_ids: Optional list of group IDs to associate.

        Returns:
            The created file resource object.

        Example:
            # Upload from bytes
            with open("report.pdf", "rb") as f:
                file_data = f.read()
            file = client.admin.files.upload_file(
                file_data=file_data,
                name="report.pdf",
                parent_folder_id="12345"
            )

            # Upload from file path
            file = client.admin.files.upload_file(
                file_data="/path/to/report.pdf",
                name="report.pdf"
            )
        """
        # Handle file_data as path or bytes
        if isinstance(file_data, str):
            with open(file_data, "rb") as f:
                content = f.read()
        else:
            content = file_data

        # Build metadata
        attributes: Dict[str, Any] = {"name": name}
        if parent_folder_id is not None:
            attributes["parent_folder_id"] = parent_folder_id
        if file_path is not None:
            attributes["file_path"] = file_path

        metadata: Dict[str, Any] = {
            "data": {
                "type": "files",
                "attributes": attributes,
            }
        }

        # Add relationships if provided
        relationships: Dict[str, Any] = {}
        if entity_ids:
            relationships["associated_entities"] = {
                "data": [{"type": "entities", "id": eid} for eid in entity_ids]
            }
        if group_ids:
            relationships["associated_groups"] = {
                "data": [{"type": "groups", "id": gid} for gid in group_ids]
            }
        if relationships:
            metadata["data"]["relationships"] = relationships

        # Prepare multipart form data
        files_payload = {
            "file": (name, content),
            "metadata": (None, json.dumps(metadata), "application/json"),
        }

        # Make request without JSON content-type (requests handles multipart)
        url = f"{self._client._base_url}/files"
        headers = {k: v for k, v in self._client._headers.items() if k.lower() != "content-type"}
        response = self._client._session.post(url, files=files_payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        file = data.get("data", {})
        logger.info(f"Uploaded file: {file.get('id')}")
        return file

    def update_file(
        self,
        file_id: str,
        *,
        name: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a file's name or move it to another folder.

        Args:
            file_id: The ID of the file to update.
            name: New name for the file.
            parent_folder_id: ID of folder to move file to.

        Returns:
            The updated file resource object.
        """
        attributes: Dict[str, Any] = {}

        if name is not None:
            attributes["name"] = name
        if parent_folder_id is not None:
            attributes["parent_folder_id"] = parent_folder_id

        payload = {
            "data": {
                "id": file_id,
                "type": "files",
                "attributes": attributes,
            }
        }

        response = self._patch(f"/files/{file_id}", json=payload)
        data = response.json()
        file = data.get("data", {})
        logger.info(f"Updated file: {file_id}")
        return file

    def delete_file(self, file_id: str) -> None:
        """
        Delete (archive) a file or folder.

        Archived files can be retrieved via the archive methods.

        Args:
            file_id: The ID of the file or folder to delete.
        """
        self._delete(f"/files/{file_id}")
        logger.info(f"Deleted file: {file_id}")

    # =========================================================================
    # Archive Methods
    # =========================================================================

    def get_archived_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get an archived (deleted) file or folder by ID.

        Args:
            file_id: The ID of the archived file to retrieve.

        Returns:
            The archived file resource object.
        """
        response = self._get(f"/archive/files/{file_id}")
        data = response.json()
        file = data.get("data", {})
        logger.debug(f"Retrieved archived file {file_id}")
        return file

    def list_archived_files(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        included_objects: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all archived (deleted) files and/or folders.

        Args:
            page_limit: Results per page (default: 500, max: 2000).
            created_after: Files created after date (ISO 8601).
            created_before: Files created before date (ISO 8601).
            included_objects: What to include - "FILES_ONLY" (default),
                "FOLDERS_ONLY", or "FILES_AND_FOLDERS".
            parent_folder_id: Filter by parent folder ID.

        Returns:
            List of archived file/folder resource objects.
        """
        params: Dict[str, Any] = {}

        if created_after is not None:
            params["filter[files][createdAfter]"] = created_after
        if created_before is not None:
            params["filter[files][createdBefore]"] = created_before
        if included_objects is not None:
            params["filter[files][includedObjects]"] = included_objects
        if parent_folder_id is not None:
            params["filter[files][parentFolderId]"] = parent_folder_id

        files = list(
            self._paginate("/archive/files", page_limit=page_limit, params=params if params else None)
        )
        logger.debug(f"Listed {len(files)} archived files")
        return files

    def download_archived_file(self, file_id: str) -> bytes:
        """
        Download an archived file's content.

        Args:
            file_id: The ID of the archived file to download.

        Returns:
            The raw file content as bytes.
        """
        response = self._get(f"/archive/files/{file_id}/download")
        logger.debug(f"Downloaded archived file {file_id}")
        return response.content

    # =========================================================================
    # Associated Groups Methods
    # =========================================================================

    def get_associated_groups(self, file_id: str) -> List[Dict[str, Any]]:
        """
        Get groups associated with a file.

        Args:
            file_id: The ID of the file.

        Returns:
            List of group relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/files/{file_id}/relationships/associated_groups")
        data = response.json()
        groups = data.get("data", [])
        logger.debug(f"Retrieved {len(groups)} associated groups for file {file_id}")
        return groups

    def add_associated_groups(self, file_id: str, group_ids: List[str]) -> None:
        """
        Add groups to a file's associations.

        Args:
            file_id: The ID of the file.
            group_ids: List of group IDs to add.
        """
        payload = {
            "data": [
                {"type": "groups", "id": group_id}
                for group_id in group_ids
            ]
        }

        self._post(f"/files/{file_id}/relationships/associated_groups", json=payload)
        logger.info(f"Added {len(group_ids)} groups to file {file_id}")

    def replace_associated_groups(self, file_id: str, group_ids: List[str]) -> None:
        """
        Replace all groups associated with a file.

        Args:
            file_id: The ID of the file.
            group_ids: List of group IDs to set as the new associations.
        """
        payload = {
            "data": [
                {"type": "groups", "id": group_id}
                for group_id in group_ids
            ]
        }

        self._patch(f"/files/{file_id}/relationships/associated_groups", json=payload)
        logger.info(f"Replaced associated groups for file {file_id}")

    def remove_associated_groups(self, file_id: str, group_ids: List[str]) -> None:
        """
        Remove groups from a file's associations.

        Args:
            file_id: The ID of the file.
            group_ids: List of group IDs to remove.
        """
        payload = {
            "data": [
                {"type": "groups", "id": group_id}
                for group_id in group_ids
            ]
        }

        self._delete(f"/files/{file_id}/relationships/associated_groups", json=payload)
        logger.info(f"Removed {len(group_ids)} groups from file {file_id}")

    # =========================================================================
    # Associated Entities Methods
    # =========================================================================

    def get_associated_entities(self, file_id: str) -> List[Dict[str, Any]]:
        """
        Get entities associated with a file.

        Args:
            file_id: The ID of the file.

        Returns:
            List of entity relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/files/{file_id}/relationships/associated_entities")
        data = response.json()
        entities = data.get("data", [])
        logger.debug(f"Retrieved {len(entities)} associated entities for file {file_id}")
        return entities

    def add_associated_entities(self, file_id: str, entity_ids: List[str]) -> None:
        """
        Add entities to a file's associations.

        Args:
            file_id: The ID of the file.
            entity_ids: List of entity IDs to add.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._post(f"/files/{file_id}/relationships/associated_entities", json=payload)
        logger.info(f"Added {len(entity_ids)} entities to file {file_id}")

    def replace_associated_entities(self, file_id: str, entity_ids: List[str]) -> None:
        """
        Replace all entities associated with a file.

        Args:
            file_id: The ID of the file.
            entity_ids: List of entity IDs to set as the new associations.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._patch(f"/files/{file_id}/relationships/associated_entities", json=payload)
        logger.info(f"Replaced associated entities for file {file_id}")

    def remove_associated_entities(self, file_id: str, entity_ids: List[str]) -> None:
        """
        Remove entities from a file's associations.

        Args:
            file_id: The ID of the file.
            entity_ids: List of entity IDs to remove.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._delete(f"/files/{file_id}/relationships/associated_entities", json=payload)
        logger.info(f"Removed {len(entity_ids)} entities from file {file_id}")
