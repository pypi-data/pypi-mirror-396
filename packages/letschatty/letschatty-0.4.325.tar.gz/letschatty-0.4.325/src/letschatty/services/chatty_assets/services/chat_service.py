"""Chat Service - Pre-configured AssetService for Chats"""

from ..asset_service import AssetService, CacheConfig
from ..collections import ChatCollection
from ....models.chat.chat import Chat
from ....models.base_models import ChattyAssetPreview
from ....models.data_base.mongo_connection import MongoConnection


class ChatService(AssetService[Chat, ChattyAssetPreview]):
    """
    Pre-configured service for Chat assets with sensible defaults.

    Note: No event configuration - Chat events are handled by ChatsEditor, not AssetService.
    """

    def __init__(self,
                 connection: MongoConnection,
                 cache_config: CacheConfig = CacheConfig.default()):
        collection = ChatCollection(connection)
        super().__init__(
            collection=collection,
            cache_config=cache_config
        )

