from __future__ import annotations

from typing import List, Optional

from app.models.storage import Datastore
from app.repositories.storage import StorageRepository
from app.schemas.storage import DatastoreCreate, DatastoreUpdate, DatastoreOut


class StorageService:
    def __init__(self, storage_repo: StorageRepository):
        self.storage_repo = storage_repo

    async def get_datastore(self, ds_id: int) -> Optional[DatastoreOut]:
        datastore = await self.storage_repo.get(ds_id)
        if datastore:
            return DatastoreOut.model_validate(datastore)
        return None

    async def get_datastore_by_ds_id(self, ds_id: str) -> Optional[DatastoreOut]:
        datastore = await self.storage_repo.get_by_ds_id(ds_id)
        if datastore:
            return DatastoreOut.model_validate(datastore)
        return None

    async def create_datastore(self, datastore_data: DatastoreCreate) -> DatastoreOut:
        datastore = Datastore(**datastore_data.model_dump())
        created = await self.storage_repo.create(datastore)
        return DatastoreOut.model_validate(created)

    async def update_datastore(self, ds_id: int, datastore_data: DatastoreUpdate) -> Optional[DatastoreOut]:
        datastore = await self.storage_repo.get(ds_id)
        if not datastore:
            return None

        update_data = datastore_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(datastore, field, value)

        updated = await self.storage_repo.update(datastore)
        return DatastoreOut.model_validate(updated)

    async def list_datastores(self, *, skip: int = 0, limit: int = 100) -> List[DatastoreOut]:
        datastores = await self.storage_repo.list_datastores(skip=skip, limit=limit)
        return [DatastoreOut.model_validate(ds) for ds in datastores]

    async def delete_datastore(self, ds_id: int) -> bool:
        datastore = await self.storage_repo.get(ds_id)
        if not datastore:
            return False

        await self.storage_repo.delete(datastore)
        return True
