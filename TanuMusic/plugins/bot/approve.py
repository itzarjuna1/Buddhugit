import json
import os
from TanuMusic import app
from pyrogram import filters
from pyrogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)

AUTO_FILE = "autoapprove.json"

# Load saved auto-approval groups
if os.path.exists(AUTO_FILE):
    with open(AUTO_FILE) as f:
        AUTO_APPROVE_GROUPS = set(json.load(f))
else:
    AUTO_APPROVE_GROUPS = set()


def save_autoapprove():
    with open(AUTO_FILE, "w") as f:
        json.dump(list(AUTO_APPROVE_GROUPS), f)


# Handle join requests (groups and channels)
@app.on_chat_join_request()
async def handle_join_request(client, message: ChatJoinRequest):
    user = message.from_user
    chat = message.chat

    # CHANNEL join requests — silent accept + DM only
    if chat.type == "channel":
        await client.approve_chat_join_request(chat.id, user.id)
        try:
            await client.send_message(
                user.id,
                f"✨ 𝐇𝐞𝐥𝐥𝐨 {user.mention},\n\n✅ 𝐘𝐨𝐮𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐭𝐨 𝐣𝐨𝐢𝐧 **{chat.title}** 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐚𝐜𝐜𝐞𝐩𝐭𝐞𝐝!\n\n— 𝐓𝐡𝐚𝐧𝐤𝐬 𝐟𝐨𝐫 𝐣𝐨𝐢𝐧𝐢𝐧𝐠."
            )
        except:
            pass
        return

    # GROUP join requests
    if chat.id in AUTO_APPROVE_GROUPS:
        await client.approve_chat_join_request(chat.id, user.id)
        await client.send_message(
            chat.id,
            f"✅ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇᴅ: {user.mention} ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ."
        )
        return

    # Manual approval needed
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴀᴄᴄᴇᴘᴛ", callback_data=f"accept_{chat.id}_{user.id}"),
            InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"reject_{chat.id}_{user.id}")
        ],
        [
            InlineKeyboardButton("⚙️ ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"toggle_{chat.id}")
        ]
    ])

    await client.send_message(
        chat.id,
        f"✨ **ɴᴇᴡ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ**\n\n"
        f"• ɴᴀᴍᴇ: {user.mention}\n"
        f"• ᴜsᴇʀ ɪᴅ: `{user.id}`",
        reply_markup=buttons
    )


# Accept/Reject handlers
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
        await callback_query.edit_message_text(f"⚠️ ᴇʀʀᴏʀ: `{e}`")


# Toggle auto-approve from button
@app.on_callback_query(filters.regex(r"^toggle_(\-?\d+)$"))
async def toggle_auto_approve_btn(client, callback_query: CallbackQuery):
    chat_id = int(callback_query.data.split("_")[1])
    if chat_id in AUTO_APPROVE_GROUPS:
        AUTO_APPROVE_GROUPS.remove(chat_id)
        save_autoapprove()
        text = "❌ **ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ᴅɪsᴀʙʟᴇᴅ**.\nᴍᴀɴᴜᴀʟ ᴀᴘᴘʀᴏᴠᴀʟ ɴᴏᴡ ʀᴇQᴜɪʀᴇᴅ."
    else:
        AUTO_APPROVE_GROUPS.add(chat_id)
        save_autoapprove()
        text = "✅ **ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ᴇɴᴀʙʟᴇᴅ**.\nɴᴇᴡ ʀᴇQᴜᴇsᴛs ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴀᴄᴄᴇᴘᴛᴇᴅ."
    await callback_query.answer()
    await callback_query.edit_message_text(text)


# /autoapprove command
@app.on_message(filters.command("autoapprove") & filters.group)
async def toggle_command(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    member = await client.get_chat_member(chat_id, user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.reply("❌ ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    if len(message.command) < 2:
        return await message.reply("⚙️ ᴜsᴀɢᴇ: `/autoapprove on` ᴏʀ `/autoapprove off`", quote=True)

    cmd = message.command[1].lower()
    if cmd == "on":
        AUTO_APPROVE_GROUPS.add(chat_id)
        save_autoapprove()
        await message.reply("✅ **ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ᴇɴᴀʙʟᴇᴅ!** ʀᴇQᴜᴇsᴛs ᴡɪʟʟ ʙᴇ ᴀᴄᴄᴇᴘᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.")
    elif cmd == "off":
        AUTO_APPROVE_GROUPS.discard(chat_id)
        save_autoapprove()
        await message.reply("❌ **ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ᴅɪsᴀʙʟᴇᴅ.** ᴍᴀɴᴜᴀʟ ᴀᴘᴘʀᴏᴠᴀʟ ʀᴇQᴜɪʀᴇᴅ.")
    else:
        await message.reply("⚙️ ᴜsᴀɢᴇ: `/autoapprove on` ᴏʀ `/autoapprove off`", quote=True)
