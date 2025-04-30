from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from TanuMusic import app  # make sure your Client is named 'app'

WELCOME_MESSAGE = (
    "**ʜᴇʟʟᴏ {mention}**\n"
    "**ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {chat_title} ʙᴀʙʏ**\n\n"
    "**ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ ᴀᴜᴛᴏ ɴsғᴡ ʀᴇᴍᴏᴠᴇʀ ᴀɴᴅ ɢʀᴏᴜᴘ ɢᴜᴀʀᴅɪᴀɴ**\n\n"
    "**ᴄᴏᴍᴍᴀɴᴅs**: /help\n"
    "**ɢɪᴛʜᴜʙ**: [ᴋʀɪsʜ](https://github.com/krishbotdev)\n"
    "**sᴜᴘᴘᴏʀᴛ**: [ᴋʀɪsʜ sᴜᴘᴘᴏʀᴛ](https://t.me/Krishsupport)\n"
    "**ɴᴇᴛᴡᴏʀᴋ**: [ᴋʀɪsʜ ɴᴇᴛᴡᴏʀᴋ](https://t.me/krishnetwork)"
)

@app.on_chat_member_updated(filters.group)
async def welcome_new_member(client: Client, update: ChatMemberUpdated):
    new = update.new_chat_member
    old = update.old_chat_member

    # Make sure old member exists and was "left"
    if new is not None and old is not None and old.status == "left":
        user = new.user
        chat_title = update.chat.title

        await app.send_message(
            chat_id=update.chat.id,
            text=WELCOME_MESSAGE.format(
                mention=user.mention, chat_title=chat_title
            ),
            disable_web_page_preview=True
        )
