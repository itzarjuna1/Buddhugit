from TanuMusic import app
from os import environ
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Environment Setup
chat_id_env = environ.get("CHAT_ID")
CHAT_ID = [int(app) for app in chat_id_env.split(",")] if chat_id_env else []
TEXT = environ.get("APPROVED_WELCOME_TEXT", "❖ ʜᴇʟʟᴏ ʙᴀʙʏ ➥ {mention}\n\n❖ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ➥ {title}\n\n")

# Join Request Handler (only for groups, not channels)
@app.on_chat_join_request(filters.group & filters.chat(CHAT_ID) if CHAT_ID else filters.group)
async def handle_join_request(client: app, message: ChatJoinRequest):
    user = message.from_user
    chat = message.chat

    # Inline buttons for admins
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎀🐾 𝐃ᴏ 𝐘ᴏᴜ 𝐖ᴀɴᴛ 𝐀ᴄᴄᴇᴘᴛ", callback_data=f"accept_{chat.id}_{user.id}"),
            InlineKeyboardButton("🎀🐾 𝐃ᴏ 𝐘ᴏᴜ 𝐖ᴀɴᴛ 𝐑ᴇᴊᴇᴄᴛ", callback_data=f"reject_{chat.id}_{user.id}")
        ]
    ])

    await client.send_message(
        chat.id,
        f"New Join Request:\n\n**Name:** {user.mention}\n**ID:** `{user.id}`",
        reply_markup=buttons
    )

# Callback handler for Accept/Reject buttons
@app.on_callback_query(filters.regex(r"^(accept|reject)_(\-?\d+)_(\d+)$"))
async def handle_decision(client: app, callback_query: CallbackQuery):
    action, chat_id, user_id = callback_query.data.split("_")
    chat_id = int(chat_id)
    user_id = int(user_id)

    try:
        if action == "accept":
            await client.approve_chat_join_request(chat_id, user_id)
            await callback_query.edit_message_text("✅ ʀᴇǫᴜᴇsᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.")
        elif action == "reject":
            await client.decline_chat_join_request(chat_id, user_id)
            await callback_query.edit_message_text("❌ ʀᴇǫᴜᴇsᴛ ʀᴇᴊᴇᴄᴛᴇᴅ.")
    except Exception as e:
        await callback_query.edit_message_text(f"Error: {e}")
