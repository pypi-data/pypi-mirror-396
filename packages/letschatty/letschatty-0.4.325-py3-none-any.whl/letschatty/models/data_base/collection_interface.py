from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Generic, TypeVar, Type, Optional, Any
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from letschatty.models.chat.chat import Chat
from ...models.base_models.chatty_asset_model import ChattyAssetModel, CompanyAssetModel, ChattyAssetPreview
from ...models.utils.types import StrObjectId
from ...models.utils.types.serializer_type import SerializerType
from ...models.utils.types.deletion_type import DeletionType
from datetime import datetime
from zoneinfo import ZoneInfo
from ...models.utils.custom_exceptions.custom_exceptions import NotFoundError
import logging

logger = logging.getLogger("CollectionInterface")

if TYPE_CHECKING:
    from .mongo_connection import MongoConnection

T = TypeVar('T', bound=ChattyAssetModel | CompanyAssetModel)
P = TypeVar('P', bound=ChattyAssetPreview)

class ChattyAssetCollectionInterface(Generic[T, P], ABC):
    def __init__(self, database: str, collection: str, connection: MongoConnection, type: Type[T], preview_type: Optional[Type[P]] = None):
        logger.info(f"Initializing collection {collection} in database {database}")
        # Sync database and collection (existing)
        self.db: Database = connection.client[database]
        self.collection: Collection = connection.client[database][collection]

        # NEW: Async database and collection
        # Store connection reference to ensure we use current event loop
        self._connection = connection
        self._database_name = database
        self._collection_name = collection
        self._async_db: Optional[AsyncIOMotorDatabase] = None
        self._async_collection: Optional[AsyncIOMotorCollection] = None

        self.type = type
        self.preview_type = preview_type

    @property
    def async_db(self) -> AsyncIOMotorDatabase:
        """Get async database, ensuring it uses the current event loop"""
        # Always ensure connection's async client is using current loop (for Lambda compatibility)
        self._connection._ensure_async_client_loop()
        # Recreate database reference to ensure it uses the current client
        self._async_db = self._connection.async_client[self._database_name]
        return self._async_db

    @property
    def async_collection(self) -> AsyncIOMotorCollection:
        """Get async collection, ensuring it uses the current event loop"""
        # Always ensure connection's async client is using current loop (for Lambda compatibility)
        self._connection._ensure_async_client_loop()
        # Recreate collection reference to ensure it uses the current client
        self._async_collection = self._connection.async_client[self._database_name][self._collection_name]
        return self._async_collection
    @abstractmethod
    def create_instance(self, data: dict) -> T:
        """Factory method to create instance from data"""
        pass

    # All methods are now async-only for better performance
    async def insert(self, asset: T) -> StrObjectId:
        """Async insert operation"""
        if not isinstance(asset, self.type):
            raise ValueError(f"Asset must be of type {self.type.__name__}")
        document = asset.model_dump_json(serializer=SerializerType.DATABASE)
        logger.debug(f"Inserting document: {document}")
        result = await self.async_collection.insert_one(document)
        if not result.inserted_id:
            raise Exception("Failed to insert document")
        logger.debug(f"Inserted document with id {result.inserted_id}")
        return result.inserted_id

    async def update(self, asset: T) -> StrObjectId:
        """Async update operation"""
        logger.debug(f"Updating document with id {asset.id}")
        if not isinstance(asset, self.type):
            raise ValueError(f"Asset must be of type {self.type.__name__}")
        asset.update_now()
        document = asset.model_dump_json(serializer=SerializerType.DATABASE)
        document.pop('_id', None)
        result = await self.async_collection.update_one(
            {"_id": ObjectId(asset.id)},
            {"$set": document}
        )
        if result.matched_count == 0:
            raise NotFoundError(f"No document found with id {asset.id}")
        if result.modified_count == 0:
            logger.debug(f"No changes were made to the document with id {asset.id} probably because the values were the same")
        return asset.id

    async def get_by_id(self, doc_id: str) -> T:
        """Get by ID operation"""
        logger.debug(f"Getting document with id {doc_id} from collection {self.async_collection.name}")
        doc = await self.async_collection.find_one({"_id": ObjectId(doc_id)})
        if doc:
            return self.create_instance(doc)
        else:
            raise NotFoundError(f"No document found with id {doc_id} in collection")

    async def get_docs(self, company_id: Optional[StrObjectId], query={}, limit=0) -> List[T]:
        """Get multiple documents operation"""
        logger.debug(f"Getting documents from collection with company_id {company_id} and query {query}")
        if company_id:
            query = query.copy()
            query["company_id"] = company_id
        cursor = self.async_collection.find(filter=query)
        if limit:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=limit if limit > 0 else None)
        logger.debug(f"Found {len(docs)} documents")
        return [self.create_instance(doc) for doc in docs]

    async def delete(self, doc_id: str, deletion_type: DeletionType = DeletionType.LOGICAL) -> StrObjectId:
        """Delete operation"""
        logger.debug(f"Deleting document with id {doc_id} - deletion type: {deletion_type}")
        if deletion_type == DeletionType.LOGICAL:
            result = await self.async_collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {"deleted_at": datetime.now(ZoneInfo("UTC")), "updated_at": datetime.now(ZoneInfo("UTC"))}}
            )
            if result.modified_count == 0:
                raise NotFoundError(f"No document found with id {doc_id}")
            return doc_id
        elif deletion_type == DeletionType.PHYSICAL:
            result = await self.async_collection.delete_one({"_id": ObjectId(doc_id)})
            if result.deleted_count == 0:
                raise NotFoundError(f"No document found with id {doc_id}")
            return doc_id
        else:
            raise ValueError(f"Invalid deletion type: {deletion_type}")

    # Additional methods - keeping these sync as they're less critical
    def get_preview_docs(self, projection = {}, all=True) -> List[P]:
        """We get the previews of all the documents in the collection for all companies"""
        if not self.preview_type:
            raise ValueError(f"{self.__class__.__name__} has no preview class")
        logger.debug(f"Getting preview documents from collection {self.collection.name}")
        if all:
            docs = list(self.collection.find(projection=projection))
        else:
            docs = list(self.collection.find(filter={"deleted_at": None}, projection=projection))
        logger.debug(f"Found {len(docs)} preview documents in collection {self.collection.name}")
        return [self.preview_type.from_dict(doc) for doc in docs]

    def get_projection_by_query(self, query = {}, projection = {}) -> List[Dict[str, Any]]:
        docs = self.collection.find(query, projection=projection)
        return [doc for doc in docs]

    def get_by_query(self, query = {}) -> List[T]:
        docs = self.collection.find(query)
        return [self.create_instance(doc) for doc in docs]

    async def get_by_ids(self, ids: List[StrObjectId]) -> List[T]:
            """
            Get multiple assets by their IDs in a single query.

            Args:
                ids: List of asset IDs

            Returns:
                List of assets objects
            """
            if not ids:
                return []

            # Convert string IDs to ObjectIds
            object_ids = [ObjectId(id) for id in ids]

            # Query for all filter criteria with matching IDs
            query = {
                "_id": {"$in": object_ids},
                "deleted_at": None
            }

            # Use the sync collection directly (inherited from ChattyAssetCollectionInterface)
            docs = await self.async_collection.find(query).to_list(length=None)

            # Create FilterCriteria instances
            return [self.create_instance(doc) for doc in docs]

