import base64
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
import segno
import unicodedata
import re


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def generate_qr_code(data, corner_radius=16, scale=8, border=2):
    try:
        buffer = BytesIO()
        segno.make(data).save(buffer, kind='png', scale=scale, border=border)
        img = Image.open(buffer).convert('RGB')
        img_corners = add_corners(img, corner_radius)
        buffer = BytesIO()
        img_corners.save(buffer, 'PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as ex:
        print(str(ex))
        return ""


def remove_vietnamese_accents(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().replace(" ", "-")


async def task_insert_data_crawled(req, keyword, items):
    try:
        for i in items:
            doc = {
                "id": i["id"],
                "title": i["title"],
                "description": i["description"],
                "img": i["img"],
                "avg_rating": i["avg_rating"],
                "total_rating": i["total_rating"],
                "price": i["price"],
                "href_value": i["href_value"],
                "qrcode": i["qrcode"],
                "e_commerce_platform": i["e_commerce_platform"],
                "time_crawled": datetime.now(),
                "keyword": [keyword],
            }
            await req.app.ctx.mdb.smart_shop.update_one(
                {"id": i["id"]},
                {"$set": doc})
            # await req.app.ctx.mdb.smart_shop.insert_one(doc)
    except Exception as ex:
        print(str(ex))
