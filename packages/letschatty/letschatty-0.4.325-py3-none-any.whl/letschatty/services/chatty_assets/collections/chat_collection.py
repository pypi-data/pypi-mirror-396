"""Chat Collection - Pre-configured AssetCollection for Chats"""

from ..asset_service import AssetCollection
from ....models.chat.chat import Chat
from ....models.base_models import ChattyAssetPreview
from ....models.data_base.mongo_connection import MongoConnection
from ....services.factories.chats.chat_factory import ChatFactory


class ChatCollection(AssetCollection[Chat, ChattyAssetPreview]):
    """Pre-configured collection for Chat assets"""

    def __init__(self, connection: MongoConnection):
        super().__init__(
            collection="chats",
            asset_type=Chat,
            connection=connection,
            create_instance_method=ChatFactory.from_json,
            preview_type=None
        )

