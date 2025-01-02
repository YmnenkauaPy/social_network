from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

async def notify_users_about_unread(chat):
    channel_layer = get_channel_layer()
    people = await database_sync_to_async(lambda: list(chat.people.all()))()

    for participant in people:
        await (channel_layer.group_send)(
            f"user_{participant.id}",
            {
                "type": "update_unread_counts",
                "chat_id": chat.id,
            }
        )
