from letschatty.models.messages.chatty_messages.button import ChattyContentButton
from ...models.messages.chatty_messages.schema import ChattyContent, ChattyContentText, ChattyContentContacts, ChattyContentLocation, ChattyContentImage, ChattyContentVideo, ChattyContentAudio, ChattyContentDocument, ChattyContentSticker, ChattyContentReaction
class MessageTextOrCaptionOrPreview:
    @staticmethod
    def get_content_preview(message_content: ChattyContent) -> str:
        if isinstance(message_content, ChattyContentText):
            return message_content.body
        elif isinstance(message_content, ChattyContentContacts):
            return f"👤 *Contacto recibido:* {message_content.contacts[0].full_name} \n📞 *Teléfono:* {message_content.contacts[0].phone_number}"
        elif    isinstance(message_content, ChattyContentLocation):
            return f"📍 \nLatitud: {message_content.latitude} \nLongitud: {message_content.longitude}_"
        elif isinstance(message_content, ChattyContentImage):
            return "🖼️ Mensaje de tipo imagen"
        elif isinstance(message_content, ChattyContentVideo):
            return "🎥 Mensaje de tipo video"
        elif isinstance(message_content, ChattyContentAudio) and not message_content.transcription:
            return "🔊 Mensaje de tipo audio"
        elif isinstance(message_content, ChattyContentAudio) and message_content.transcription:
            return "🔊 Audio: " + message_content.transcription
        elif isinstance(message_content, ChattyContentDocument):
            return "📄 Mensaje de tipo documento"
        elif isinstance(message_content, ChattyContentSticker):
            return "😀 Mensaje de tipo sticker"
        elif isinstance(message_content, ChattyContentReaction):
            return "❤️ Mensaje de tipo reacción"
        elif isinstance(message_content, ChattyContentButton):
            return f"{message_content.payload}"
        else:
            return "Vista previa del mensaje"
