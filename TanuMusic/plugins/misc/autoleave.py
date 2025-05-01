import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

import config
from TanuMusic import app
from TanuMusic.core.call import Tanu, autoend
from TanuMusic.utils.database import get_client, is_active_chat, is_autoend


# Auto leave inactive groups
async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT:
        while not await asyncio.sleep(900):
            from TanuMusic.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        if i.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                            if (
                                i.chat.id != config.LOGGER_ID
                                and i.chat.id != -1002117519350
                            ):
                                if left == 20:
                                    continue
                                if not await is_active_chat(i.chat.id):
                                    try:
                                        await client.leave_chat(i.chat.id)
                                        left += 1
                                    except:
                                        continue
                except:
                    pass

asyncio.create_task(auto_leave())


# Auto end and restart VC
async def auto_end():
    while True:
        await asyncio.sleep(5)
        ender = await is_autoend()
        if not ender:
            continue
        for chat_id in list(autoend):
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    autoend.pop(chat_id, None)
                    continue
                autoend.pop(chat_id, None)
                try:
                    await Tanu.stop_stream(chat_id)
                except:
                    continue
                try:
                    await app.send_message(
                        chat_id,
                        "❖ ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ."
                    )
                except:
                    continue
                try:
                    await Tanu.start_stream(chat_id, "input.raw")  # Use a silent placeholder
                    await app.send_message(
                        chat_id,
                        "➕ ɴᴇᴡ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ. ᴜsᴇ /play ᴛᴏ ᴘʟᴀʏ ᴀ sᴏɴɢ."
                    )
                except:
                    continue

asyncio.create_task(auto_end())


# Command to start VC manually
@app.on_message(filters.command("VCstart") & filters.group)
async def start_vc(_, message: Message):
    chat_id = message.chat.id
    try:
        await Tanu.start_stream(chat_id, "input.raw")  # Silent placeholder audio
        await message.reply("✅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ. ᴜsᴇ /play ᴛᴏ ᴘʟᴀʏ ᴀ sᴏɴɢ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴀʀᴛ ᴠᴄ.\n**Reason:** `{e}`")


# Command to end VC manually
@app.on_message(filters.command("endvc") & filters.group)
async def end_vc(_, message: Message):
    chat_id = message.chat.id
    try:
        await Tanu.stop_stream(chat_id)
        await message.reply("✅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴇɴᴅ ᴠᴄ.\n**Reason:** `{e}`")
