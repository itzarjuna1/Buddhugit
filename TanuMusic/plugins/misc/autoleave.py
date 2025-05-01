import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram import raw

import config
from TanuMusic import app
from TanuMusic.core.call import Tanu, autoend
from TanuMusic.utils.database import get_client, is_active_chat, is_autoend
from TanuMusic.core.userbot import assistants

# Track VC status
vc_status = {}

# Auto leave inactive chats
async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT:
        while not await asyncio.sleep(900):
            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        if i.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                            if i.chat.id not in [config.LOGGER_ID, -1002117519350]:
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

# Auto end inactive streams
async def auto_end():
    while not await asyncio.sleep(5):
        if not await is_autoend():
            continue
        for chat_id in list(autoend):
            timer = autoend.get(chat_id)
            if not timer or datetime.now() < timer:
                continue
            if not await is_active_chat(chat_id):
                autoend.pop(chat_id, None)
                continue
            autoend.pop(chat_id, None)
            try:
                await Tanu.stop_stream(chat_id)
                vc_status[chat_id] = False
                userbot = await get_client(assistants[0])
                await userbot.invoke(
                    raw.functions.phone.DiscardGroupCall(
                        call=raw.types.InputGroupCall(
                            id=1,
                            access_hash=1
                        )
                    )
                )
                await app.send_message(chat_id, "❖ ʙᴏᴛ ᴀᴜᴛᴏ ʟᴇғᴛ ᴠᴄ ᴀs ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ.")
            except:
                continue

asyncio.create_task(auto_end())

# /VCstart - Start VC manually
@app.on_message(filters.command("VCstart") & filters.group)
async def start_vc(_, message: Message):
    chat_id = message.chat.id
    try:
        userbot = await get_client(assistants[0])
        await userbot.invoke(
            raw.functions.phone.CreateGroupCall(
                peer=await userbot.resolve_peer(chat_id),
                random_id=app.rnd_id(),
            )
        )
        vc_status[chat_id] = True
    except Exception as e:
        if "already started" not in str(e):
            await message.reply("❌ Failed to start VC.\nMake sure assistant is admin.")
            return
    try:
        await Tanu.start_stream(chat_id, "input.raw")
        await message.reply("✅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴀʀᴛ sᴛʀᴇᴀᴍ.\n**Reason:** `{e}`")

# /endvc - End VC manually
@app.on_message(filters.command("endvc") & filters.group)
async def end_vc(_, message: Message):
    chat_id = message.chat.id
    try:
        await Tanu.stop_stream(chat_id)
        vc_status[chat_id] = False
        userbot = await get_client(assistants[0])
        await userbot.invoke(
            raw.functions.phone.DiscardGroupCall(
                call=raw.types.InputGroupCall(
                    id=1,
                    access_hash=1
                )
            )
        )
        await message.reply("❎ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ ʙʏ ᴜꜱᴇʀʙᴏᴛ.")
    except Exception as e:
        await message.reply(f"⚠️ Cᴏᴜʟᴅɴ'ᴛ ᴇɴᴅ Vᴄ: `{e}`")

# Utility function to check VC status
def is_vc_active(chat_id):
    return vc_status.get(chat_id, False)

# Example patch to /play command (add this logic inside /play):
async def check_and_start_vc(chat_id, message):
    if not is_vc_active(chat_id):
        try:
            userbot = await get_client(assistants[0])
            await userbot.invoke(
                raw.functions.phone.CreateGroupCall(
                    peer=await userbot.resolve_peer(chat_id),
                    random_id=app.rnd_id(),
                )
            )
            vc_status[chat_id] = True
            await message.reply("✅ ᴀᴜᴛᴏ-sᴛᴀʀᴛᴇᴅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.")
        except Exception as e:
            if "already started" not in str(e):
                await message.reply(f"❌ ᴄᴀɴ'ᴛ ᴀᴜᴛᴏ-sᴛᴀʀᴛ ᴠᴄ: `{e}`")
