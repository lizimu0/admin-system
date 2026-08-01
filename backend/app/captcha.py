"""算术验证码:生成图片与答案,内存存储,带 TTL 过期清理。"""
import base64
import io
import random
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

from .config import settings

_STORE: dict[str, dict] = {}  # captcha_id -> {"answer": str, "expires": float}


def _cleanup():
    now = time.time()
    expired = [k for k, v in _STORE.items() if v["expires"] < now]
    for k in expired:
        _STORE.pop(k, None)


def generate_captcha() -> dict:
    """生成算术验证码,返回 {captcha_id, image(base64 PNG)}。"""
    _cleanup()

    a = random.randint(10, 99)
    b = random.randint(1, 20)
    op = random.choice(["+", "-"])
    if op == "-":
        # 保证结果非负
        if a < b:
            a, b = b, a
    answer = str(a - b if op == "-" else a + b)
    text = f"{a} {op} {b} = ?"

    captcha_id = uuid.uuid4().hex[:16]
    _STORE[captcha_id] = {
        "answer": answer,
        "expires": time.time() + settings.CAPTCHA_TTL_MINUTES * 60,
    }

    # 绘制 120x40 图片
    width, height = 120, 40
    image = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(image)
    # 干扰线
    for _ in range(4):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
            ],
            fill=(random.randint(150, 220), random.randint(150, 220), random.randint(150, 220)),
            width=1,
        )
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    draw.text((12, 10), text, fill=(60, 60, 60), font=font)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {"captcha_id": captcha_id, "image": image_b64}


def verify_captcha(captcha_id: str, code: str) -> bool:
    """校验验证码,校验后无论成败都销毁该验证码。"""
    item = _STORE.pop(captcha_id, None)
    if item is None:
        return False
    if item["expires"] < time.time():
        return False
    return item["answer"] == code.strip()
