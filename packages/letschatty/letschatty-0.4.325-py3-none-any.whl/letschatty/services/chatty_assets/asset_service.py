from __future__ import annotations
from typing import TypeVar, Generic, Type, Callable, Protocol, Optional, ClassVar, TYPE_CHECKING, List

from bson import ObjectId
from letschatty.models.utils.types import StrObjectId
from .base_container_with_collection import ChattyAssetCollectionInterface, ChattyAssetContainerWithCollection, CacheConfig
from ...models.base_models import ChattyAssetModel
from ...models.base_models.chatty_asset_model import ChattyAssetPreview
from ...models.data_base.mongo_connection import MongoConnection
import logging
import os

if TYPE_CHECKING:
    from ...models.analytics.events.base import EventType
    from ...models.company.empresa import EmpresaModel
    from ...models.execution.execution import ExecutionContext
    from ...models.company.assets.company_assets import CompanyAssetType
    from ...models.utils.types.deletion_type import DeletionType

logger = logging.getLogger("AssetService")

# Protocol for assets that specify their preview type
class AssetWithPreview(Protocol):
    preview_class: Type[ChattyAssetPreview]

T = TypeVar('T', bound=ChattyAssetModel)
P = TypeVar('P', bound=ChattyAssetPreview)  # Preview type

db_name = os.getenv("MONGO_DB_NAME")
logger.info(f"🚨🚨🚨🚨🚨🚨 db_name: {db_name}")
if db_name is None:
    raise ValueError("MONGO_DB_NAME is not set in the environment variables")


class AssetCollection(Generic[T, P], ChattyAssetCollectionInterface[T, P]):
    def __init__(self,
                 collection: str,
                 asset_type: Type[T],
                 connection: MongoConnection,
                 create_instance_method: Callable[[dict], T],
                 preview_type: Optional[Type[P]] = None):
        logger.debug(f"AssetCollection {self.__class__.__name__} initializing for {collection}")
        super().__init__(
            database=db_name, #type: ignore
            collection=collection,
            connection=connection,
            type=asset_type,
            preview_type=preview_type
        )
        self._create_instance_method = create_instance_method
        logger.debug(f"AssetCollection {self.__class__.__name__} initialized for {collection}")

    def create_instance(self, data: dict) -> T:
        if not isinstance(data, dict):
            raise ValueError(f"Data must be a dictionary, got {type(data)}: {data}")
        return self._create_instance_method(data)


class AssetService(Generic[T, P], ChattyAssetContainerWithCollection[T, P]):
    """
    Generic service for handling CRUD operations for any Chatty asset.

    Supports optional automatic event handling for API implementations.
    Set these class attributes to enable events:
    - asset_type_enum: CompanyAssetType (e.g., CompanyAssetType.PRODUCTS)
    - event_type_created: EventType (e.g., EventType.PRODUCT_CREATED)
    - event_type_updated: EventType (e.g., EventType.PRODUCT_UPDATED)
    - event_type_deleted: EventType (e.g., EventType.PRODUCT_DELETED)
    """

    # Optional: Set these in subclasses to enable automatic event handling
    asset_type_enum: ClassVar[Optional['CompanyAssetType']] = None
    event_type_created: ClassVar[Optional['EventType']] = None
    event_type_updated: ClassVar[Optional['EventType']] = None
    event_type_deleted: ClassVar[Optional['EventType']] = None

    collection: AssetCollection[T, P]  # Type annotation for better type checking

    def __init__(self,
                 collection: AssetCollection[T, P],
                 cache_config: CacheConfig = CacheConfig.default()):
        """
        Initialize AssetService with a pre-configured collection.

        The item_type and preview_type are automatically extracted from the collection,
        eliminating redundancy and simplifying the API.

        Args:
            collection: Pre-configured AssetCollection subclass
            cache_config: Cache configuration
        """
        logger.debug(f"AssetService {self.__class__.__name__} initializing with collection")
        super().__init__(
            item_type=collection.type,
            preview_type=collection.preview_type,
            collection=collection,
            cache_config=cache_config,
        )
        logger.debug(f"AssetService {self.__class__.__name__} initialized")

    @classmethod
    def from_config(cls,
                    collection_name: str,
                    asset_type: Type[T],
                    connection: MongoConnection,
                    create_instance_method: Callable[[dict], T],
                    preview_type: Optional[Type[P]] = None,
                    cache_config: CacheConfig = CacheConfig.default()) -> 'AssetService[T, P]':
        """
        Create an AssetService using the legacy configuration pattern.

        This class method is provided for backward compatibility.
        New code should use pre-configured AssetCollection subclasses.

        Args:
            collection_name: MongoDB collection name
            asset_type: The asset model type
            connection: MongoDB connection
            create_instance_method: Factory method to create asset instances
            preview_type: Optional preview type
            cache_config: Cache configuration

        Returns:
            AssetService instance
        """
        logger.debug(f"AssetService creating from config for {collection_name}")
        asset_collection = AssetCollection(
            collection=collection_name,
            asset_type=asset_type,
            connection=connection,
            create_instance_method=create_instance_method,
            preview_type=preview_type
        )
        return cls(
            collection=asset_collection,
            cache_config=cache_config
        )

    def _should_handle_events(self) -> bool:
        """Check if this service should handle events automatically"""
        return (self.asset_type_enum is not None and
                self.event_type_created is not None and
                self.event_type_updated is not None and
                self.event_type_deleted is not None)

    def _queue_event(self, item: T, event_type: 'EventType', execution_context: 'ExecutionContext', company_info: 'EmpresaModel'):
        """Queue an event for this asset if event handling is enabled"""
        if not self._should_handle_events() or not self.asset_type_enum:
            return

        try:
            from ...services.factories.analytics.events_factory import EventFactory
            from ...services.events import events_manager

            # Type guard - company_id should exist on ChattyAssetModel
            if not hasattr(item, 'company_id'):
                logger.warning(f"Asset {type(item).__name__} missing company_id, skipping event")
                return

            events = EventFactory.asset_events(
                company_id=item.company_id,  # type: ignore[attr-defined]
                executor_id=execution_context.executor.id,
                asset=item,
                asset_type=self.asset_type_enum,
                event_type=event_type,
                time=execution_context.time,
                trace_id=execution_context.trace_id,
                executor_type=execution_context.executor.type,
                company_info=company_info
            )
            events_manager.queue_events(events)
        except ImportError:
            # Events not available (microservice context) - skip
            pass

    # All methods are now async-only for better performance
    async def insert(self, item: T, execution_context: 'ExecutionContext', company_info: Optional['EmpresaModel'] = None) -> T:
        """Insert with automatic event handling if configured"""
        result = await super().insert(item, execution_context)
        if company_info and self._should_handle_events() and self.event_type_created:
            self._queue_event(result, self.event_type_created, execution_context, company_info)
        return result

    async def update(self, id: str, new_item: T, execution_context: 'ExecutionContext', company_info: Optional['EmpresaModel'] = None) -> T:
        """Update with automatic event handling if configured"""
        result = await super().update(id, new_item, execution_context)
        if company_info and self._should_handle_events() and self.event_type_updated:
            self._queue_event(result, self.event_type_updated, execution_context, company_info)
        return result

    async def delete(self, id: str, execution_context: 'ExecutionContext', company_info: Optional['EmpresaModel'] = None, deletion_type: Optional['DeletionType'] = None) -> T:
        """Delete with automatic event handling if configured"""
        from ...models.utils.types.deletion_type import DeletionType as DT
        result = await super().delete(id, execution_context, deletion_type or DT.LOGICAL)
        if company_info and self._should_handle_events() and self.event_type_deleted:
            self._queue_event(result, self.event_type_deleted, execution_context, company_info)
        return result

    async def restore(self, id: str, execution_context: 'ExecutionContext', company_info: Optional['EmpresaModel'] = None) -> T:
        """Restore with automatic event handling if configured"""
        result = await super().restore(id, execution_context)
        if company_info and self._should_handle_events() and self.event_type_updated:
            self._queue_event(result, self.event_type_updated, execution_context, company_info)
        return result

    # Generic convenience methods
    async def create_asset(self, data: dict, execution_context: 'ExecutionContext', company_info: 'EmpresaModel') -> T:
        """
        Generic create method - creates instance from dict and inserts with events.
        Can be called as create_asset or aliased to create_product/create_tag/etc.
        """
        data["company_id"] = execution_context.company_id
        item = self.collection.create_instance(data)
        return await self.insert(item, execution_context, company_info)

    async def update_asset(self, id: str, data: dict, execution_context: 'ExecutionContext', company_info: 'EmpresaModel') -> T:
        """
        Generic update method - creates instance from dict and updates with events.
        Can be called as update_asset or aliased to update_product/update_tag/etc.
        """
        new_item = self.collection.create_instance(data)
        return await self.update(id, new_item, execution_context, company_info)

    async def delete_asset(self, id: str, execution_context: 'ExecutionContext', company_info: 'EmpresaModel') -> T:
        """
        Generic delete method - deletes with events.
        Can be called as delete_asset or aliased to delete_product/delete_tag/etc.
        """
        return await self.delete(id, execution_context, company_info)

    def get_preview_type(self) -> Type[P]:
        """Get the preview type from the asset class if it has one"""
        if hasattr(self.item_type, 'preview_class') and self.item_type.preview_class is not None:
            return self.item_type.preview_class  # type: ignore
        return ChattyAssetPreview  # type: ignore

    def get_preview_by_id(self, id: str, company_id: str) -> P:
        """Get a preview by ID using the preview type from the asset class"""
        preview_type = self.get_preview_type()
        return super().get_preview_by_id(id, company_id, preview_type)

    # Additional async read methods (passthrough to base class)
    async def get_by_id(self, id: str) -> T:
        """Get by ID"""
        return await super().get_by_id(id)

    async def get_all(self, company_id: str) -> List[T]:
        """Get all for company"""
        return await super().get_all(company_id)

    async def get_by_query(self, query: dict, company_id: Optional[str]) -> List[T]:
        """Get by query"""
        return await super().get_by_query(query, company_id)

    async def get_item_dumped(self, id: str) -> dict:
        """Get item by ID and return as JSON serialized dict for frontend"""
        from ...models.utils.types.serializer_type import SerializerType
        item = await self.get_by_id(id)
        return item.model_dump_json(serializer=SerializerType.FRONTEND)

