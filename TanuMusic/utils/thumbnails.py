import os
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat
from youtubesearchpython.__future__ import VideosSearch
from config import FAILED

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
CARD_WIDTH, CARD_HEIGHT = 1000, 600
CARD_RADIUS = 54
PADDING_X, PADDING_Y = 140, 80

FONT_TITLE = "TanuMusic/assets/font.ttf"
FONT_SUB = "TanuMusic/assets/font2.ttf"

def truncate_text(text, font, max_width):
    ellipsis = "..."
    if font.getlength(text) <= max_width:
        return text
    while font.getlength(text + ellipsis) > max_width and text:
        text = text[:-1]
    return text + ellipsis if text else ellipsis

def get_average_color(image: Image.Image) -> tuple:
    small = image.resize((50, 50))
    stat = ImageStat.Stat(small)
    return tuple(int(c) for c in stat.mean[:3])

def get_brightness(color: tuple) -> float:
    r, g, b = color
    return (0.299*r + 0.587*g + 0.114*b)

async def get_thumb(videoid: str, progress_ratio: float = 0.5) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_musiccard.jpg")
    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(videoid, limit=1)
        data = (await results.next())["result"][0]
        title = data.get("title", "Unknown Title")
        channel = data.get("channel", {}).get("name", "Unknown Channel")
        thumbnail = data.get("thumbnails", [{}])[0].get("url", FAILED)
        views = data.get("viewCount", {}).get("text", "0 views")
    except Exception:
        title, channel, thumbnail, views = "Unknown Title", "Unknown Channel", FAILED, "0 views"

    if thumbnail == FAILED or not thumbnail:
        return FAILED

    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    return FAILED
    except Exception:
        return FAILED

    try:
        album_art_raw = Image.open(thumb_path).convert("RGB")

        bg = album_art_raw.resize((WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(24))
        draw = ImageDraw.Draw(bg)

        avg_color = get_average_color(album_art_raw)
        card_color = tuple(int(c * 0.6) for c in avg_color)

        brightness = get_brightness(card_color)
        if brightness < 130:
            text_color = (255, 255, 255)
            meta_text_color = (220, 220, 220)
            progress_color = (255, 255, 255)
        else:
            text_color = (40, 40, 40)
            meta_text_color = (80, 80, 80)
            progress_color = (255, 255, 255)
            

        card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card)
        card_draw.rounded_rectangle((0, 0, CARD_WIDTH, CARD_HEIGHT), radius=CARD_RADIUS, fill=card_color)

        art_box = (60, 40, CARD_WIDTH - 60, 440)
        art_width = art_box[2] - art_box[0]
        art_height = art_box[3] - art_box[1]
        album_art = album_art_raw.resize((art_width, art_height))
        mask = Image.new("L", (art_width, art_height), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, art_width, art_height), radius=40, fill=255)
        card.paste(album_art, (art_box[0], art_box[1]), mask)

        try:
            title_font = ImageFont.truetype(FONT_TITLE, 46)
            meta_font = ImageFont.truetype(FONT_SUB, 32)
        except:
            title_font = meta_font = ImageFont.load_default()

        text_y = art_box[3] + 25
        text_x = art_box[0]
        max_text_width = CARD_WIDTH - 2 * text_x

        short_title = truncate_text(title, title_font, max_text_width)
        short_meta = truncate_text(f"{channel} â€¢ {views}", meta_font, max_text_width)

        card_draw.text((text_x, text_y), short_title, font=title_font, fill=text_color)
        card_draw.text((text_x, text_y + 55), short_meta, font=meta_font, fill=meta_text_color)

        # Progress bar spacing fix
        progress_top = text_y + 55 + 50  # 50px below subtitle
        bar_height = 10
        bar_radius = 5
        bar_width = max_text_width
        fill_width = int(bar_width * max(0.0, min(progress_ratio, 1.0)))
        dot_radius = 12

        # background bar
        card_draw.rounded_rectangle(
            (text_x, progress_top, text_x + bar_width, progress_top + bar_height),
            radius=bar_radius, fill=(120, 120, 120)
        )
        # progress fill
        card_draw.rounded_rectangle(
            (text_x, progress_top, text_x + fill_width, progress_top + bar_height),
            radius=bar_radius, fill=progress_color
        )
        # circular thumb
        dot_center_x = text_x + fill_width
        dot_center_y = progress_top + bar_height // 2
        card_draw.ellipse(
            (dot_center_x - dot_radius//2, dot_center_y - dot_radius//2,
             dot_center_x + dot_radius//2, dot_center_y + dot_radius//2),
            fill=progress_color
        )

        mask_card = Image.new("L", (CARD_WIDTH, CARD_HEIGHT), 0)
        ImageDraw.Draw(mask_card).rounded_rectangle((0, 0, CARD_WIDTH, CARD_HEIGHT), radius=CARD_RADIUS, fill=255)
        bg.paste(card, (PADDING_X, PADDING_Y), mask_card)

        os.remove(thumb_path)
        bg.save(cache_path, format="JPEG", quality=95)
        return cache_path

    except Exception as e:
        import traceback
        traceback.print_exc()
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        return FAILED
