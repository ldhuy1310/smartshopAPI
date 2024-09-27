import base64
from io import BytesIO
from PIL import Image, ImageDraw

import segno


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
