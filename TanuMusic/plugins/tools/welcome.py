from pyrogram import filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_group(_, member: ChatMemberUpdated):
    chat_id = member.chat.id

    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return

    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    try:
        await app.send_message(
            chat_id,
            text=f"""
ㅤㅤㅤ◦•●◉✿ ᴡᴇʟᴄᴏᴍᴇ ʙᴀʙʏ ✿◉●•◦
▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰

● ɴᴀᴍᴇ ➥  {user.mention}
● ᴜsᴇʀɴᴀᴍᴇ ➥  @{user.username if user.username else 'N/A'}
● ᴜsᴇʀ ɪᴅ ➥  {user.id}

❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ ˹ Kʀɪsʜɴᴇᴛᴇᴏʀᴋ™ ♡゙
▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ", url="https://t.me/CulturalMusicbot?startgroup=new"),
                    ]
                ]
            )
        )
    except Exception as e:
        LOGGER.error(e)
