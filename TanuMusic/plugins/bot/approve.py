from TanuMusic import app
from os import environ
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus

# ENV values
chat_id_env = environ.get("CHAT_ID")
CHAT_ID = [int(app) for app in chat_id_env.split(",")] if chat_id_env else []

TEXT = environ.get("APPROVED_WELCOME_TEXT", "❖ ʜᴇʟʟᴏ ʙᴀʙʏ ➥ {mention}\n\n❖ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ➥ {title}\n\n")

# Runtime flag
auto_accept_enabled = {}

# Create dynamic button with user ID
def get_buttons(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}"),
        ],
        [
            InlineKeyboardButton("⚡ Auto Accept ON", callback_data="enable_auto")
        ]
    ])

@app.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def handle_join_request(client: app, message: ChatJoinRequest):
    chat_id = message.chat.id
    user = message.from_user

    if auto_accept_enabled.get(chat_id):
        await client.approve_chat_join_request(chat_id=chat_id, user_id=user.id)
        await client.send_message(chat_id, f"✅ Auto Approved: {user.mention}")
    else:
        await client.send_message(
            chat_id,
            TEXT.format(mention=user.mention, title=message.chat.title),
            reply_markup=get_buttons(user.id)
        )

@app.on_callback_query(filters.regex(r"^(accept|reject)_(\d+)$"))
async def handle_decision(client: Client, callback_query: CallbackQuery):
    action, target_user_id = callback_query.data.split("_")
    chat_id = callback_query.message.chat.id
    user_id = int(target_user_id)

    # Only admins can act
    member = await client.get_chat_member(chat_id, callback_query.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await callback_query.answer("❌ Only admins can use this", show_alert=True)
        return

    if action == "accept":
        await client.approve_chat_join_request(chat_id, user_id)
        await callback_query.message.edit_text(f"✅ Approved [user](tg://user?id={user_id})")
        await callback_query.answer("Approved!")
    elif action == "reject":
        await client.reject_chat_join_request(chat_id, user_id)
        await callback_query.message.edit_text(f"❌ Rejected [user](tg://user?id={user_id})")
        await callback_query.answer("Rejected!")

@app.on_callback_query(filters.regex("enable_auto"))
async def enable_auto_accept(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await callback_query.answer("Only admins can enable auto accept!", show_alert=True)
        return

    auto_accept_enabled[chat_id] = True
    await callback_query.answer("⚡ Auto Accept Enabled")
    await callback_query.message.edit_text("✅ Auto Accept Mode is now ON.")

@app.on_message(filters.command("autorequestcancel") & filters.group)
async def cancel_auto_accept(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await message.reply("❌ Only admins can cancel auto accept.")
        return

    auto_accept_enabled[chat_id] = False
    await message.reply("✅ Auto Accept Disabled. Manual mode resumed.")
