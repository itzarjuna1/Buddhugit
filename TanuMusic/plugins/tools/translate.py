from TanuMusic import app
from pyrogram import filters
from deep_translator import GoogleTranslator
import random

# -------------------------------
# /tr - Translate Command
# -------------------------------
@app.on_message(filters.command("tr"))
async def translate(client, message):
    if message.reply_to_message:
        text_to_translate = message.reply_to_message.text
        target_language = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else 'en'
    else:
        if len(message.text.split()) < 3:
            await message.reply_text("You can use this command by replying to a message or using: `/tr [lang] [text]`", parse_mode="Markdown")
            return
        target_language = message.text.split(None, 2)[1]
        text_to_translate = message.text.split(None, 2)[2]

    try:
        translated = GoogleTranslator(source='auto', target=target_language).translate(text_to_translate)
        await message.reply_text(f"<b>ᴛʀᴀɴsʟᴀᴛᴇᴅ ᴛᴏ</b> <code>{target_language}</code>\n\n<code>{translated}</code>", parse_mode="html")
    except Exception as e:
        await message.reply_text(f"An error occurred during translation: {str(e)}")

# -------------------------------
# /gm - Good Morning
# -------------------------------
@app.on_message(filters.command("gm"))
async def gm(_, message):
    gm_images = [
        "https://files.catbox.moe/tvkt2r.jpg",
        "https://files.catbox.moe/8q3k0u.jpg",
        "https://files.catbox.moe/b72yxr.jpg"
    ]
    text = "☀️ <b>Good Morning!</b>\nHave a wonderful day ahead!"
    await message.reply_photo(photo=random.choice(gm_images), caption=text, parse_mode="html")

# -------------------------------
# /gn - Good Night
# -------------------------------
@app.on_message(filters.command("gn"))
async def gn(_, message):
    gn_images = [
        "https://files.catbox.moe/3k8shf.jpg",
        "https://files.catbox.moe/7v29b1.jpg",
        "https://files.catbox.moe/0li4yv.jpg"
    ]
    text = "🌙 <b>Good Night!</b>\nSleep well and sweet dreams!"
    await message.reply_photo(photo=random.choice(gn_images), caption=text, parse_mode="html")

# -------------------------------
# Couple Bot - Match Random Users
# -------------------------------
@app.on_message(filters.command("couple"))
async def random_couple(_, message):
    chat_id = message.chat.id
    try:
        admins = await app.get_chat_administrators(chat_id)
        user_list = [admin.user for admin in admins if not admin.user.is_bot]

        if len(user_list) < 2:
            await message.reply_text("⚠️ Not enough members to form a couple!")
            return

        couple = random.sample(user_list, 2)

        def format_user(user):
            return f"{user.first_name} (@{user.username})" if user.username else user.first_name

        user1 = format_user(couple[0])
        user2 = format_user(couple[1])

        caption = f"💑 **Today's Couple:** {user1} ❤️ {user2}!"
        await message.reply_photo("https://files.catbox.moe/1ko4y2.jpg", caption=caption, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# -------------------------------
# Message Edit Detection - Deletes Edited Messages
# -------------------------------
@app.on_message(filters.edited_message)
async def handle_edited_message(_, message):
    chat_id = message.chat.id
    user = message.from_user
    edited_by = f"@{user.username}" if user.username else user.first_name

    try:
        await app.delete_messages(chat_id, message.message_id)
        await app.send_message(chat_id, f"⚠️ {edited_by}, editing messages is not allowed! 🚫")
    except Exception as e:
        print(f"Failed to delete message: {e}")

# -------------------------------
# OpenRouter AI Chat Functionality (Only Works with /tell Command)
# -------------------------------
@app.on_message(filters.command("tell"))
async def chat_with_ai(_, message):
    chat_id = message.chat.id
    user_message = message.text.replace('/tell', '', 1).strip()

    if not user_message:
        await message.reply_text("❓ Please type a question after `/tell`. Example: `/tell How are you?`", parse_mode="Markdown")
        return

    await message.reply_chat_action("typing")

    ai_response = await get_openrouter_response(user_message)
    await message.reply_text(ai_response)

# -------------------------------
# OpenRouter AI Response Function
# -------------------------------
async def get_openrouter_response(user_message):
    OPENROUTER_API_KEY = "your-api-key"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": user_message}]
    }

    for attempt in range(3):
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            print(f"Attempt {attempt + 1}: Connection error. Retrying in 2s...")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return "⚠️ AI service is currently unavailable. Please try again later."

    return "⚠️ AI service is currently unreachable."

# -------------------------------
# Message Counter & /topusers
# -------------------------------
user_activity = defaultdict(int)

@app.on_message(filters.text & ~filters.private)
async def count_messages(_, message):
    user_id = message.from_user.id
    user_activity[user_id] += 1

@app.on_message(filters.command("topusers"))
async def show_top_users(_, message):
    if not user_activity:
        await message.reply_text("No user activity recorded yet.")
        return

    sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = []
    for i, (user_id, count) in enumerate(sorted_users, start=1):
        try:
            user = await app.get_users(user_id)
            name = f"@{user.username}" if user.username else user.first_name
            lines.append(f"{i}. {name} — {count} messages")
        except:
            continue

    await message.reply_text("**🏆 Top Active Users:**\n\n" + "\n".join(lines))

# Run the bot
app.run()
