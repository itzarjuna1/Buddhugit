from TanuMusic import app
from pyrogram import filters
from pyrogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)

# Set to keep track of groups with auto-approval enabled
AUTO_APPROVE_GROUPS = set()

# Handle join requests
@app.on_chat_join_request(filters.group)
async def handle_join_request(client, message: ChatJoinRequest):
    user = message.from_user
    chat = message.chat

    # If auto-approve is enabled for the group
    if chat.id in AUTO_APPROVE_GROUPS:
        await client.approve_chat_join_request(chat.id, user.id)
        await client.send_message(
            chat.id,
            f"✅ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇᴅ: {user.mention}"
        )
        return

    # Inline buttons for manual approval
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎀 ᴀᴄᴄᴇᴘᴛ", callback_data=f"accept_{chat.id}_{user.id}"),
            InlineKeyboardButton("🎀 ʀᴇᴊᴇᴄᴛ", callback_data=f"reject_{chat.id}_{user.id}")
        ],
        [
            InlineKeyboardButton("⚙️ ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"toggle_{chat.id}")
        ]
    ])

    # Send message with approval buttons
    sent_msg = await client.send_message(
        chat.id,
        f"✨ **New Join Request**\n\n"
        f"➤ **Name:** {user.mention}\n"
        f"➤ **User ID:** `{user.id}`\n"
        f"➤ **Chat:** {chat.title}",
        reply_markup=buttons
    )

# Handle Accept/Reject button actions
@app.on_callback_query(filters.regex(r"^(accept|reject)_(\-?\d+)_(\d+)$"))
async def handle_decision(client, callback_query: CallbackQuery):
    action, chat_id, user_id = callback_query.data.split("_")
    chat_id = int(chat_id)
    user_id = int(user_id)

    try:
        if action == "accept":
            await client.approve_chat_join_request(chat_id, user_id)
            await callback_query.message.delete()
        elif action == "reject":
            await client.decline_chat_join_request(chat_id, user_id)
            await callback_query.message.delete()
    except Exception as e:
        await callback_query.edit_message_text(f"⚠️ Error: `{e}`")

# Handle toggle button for auto-approve
@app.on_callback_query(filters.regex(r"^toggle_(\-?\d+)$"))
async def toggle_auto_approve_btn(client, callback_query: CallbackQuery):
    chat_id = int(callback_query.data.split("_")[1])

    if chat_id in AUTO_APPROVE_GROUPS:
        AUTO_APPROVE_GROUPS.remove(chat_id)
        text = "❌ **Auto-Approval Disabled**\nJoin requests will need manual approval."
    else:
        AUTO_APPROVE_GROUPS.add(chat_id)
        text = "✅ **Auto-Approval Enabled**\nNew users will be automatically accepted."

    await callback_query.answer()
    await callback_query.edit_message_text(text)
