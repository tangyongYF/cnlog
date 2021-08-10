from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random


def get_color():
    return ((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

def get_valid_code_imgss(request):
    # 方式二
    # def get_color():
    #     import random
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # img = Image.new("RGB", (270, 40), color=get_color())
    #
    # with open("ValidCode.png", "wb") as f:
    #     img.save(f, "png")
    #
    # with open("ValidCode.png", "rb") as f:
    #     data = f.read()
    #
    # return HttpResponse(data)

    # 方式三
    # def get_color():
    #     import random
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # img = Image.new("RGB", (270, 40), color=get_color())
    #
    # from io import BytesIO
    #
    # f = BytesIO()
    # img.save(f, "png")
    # data = f.getvalue()

    # 方式四

    img = Image.new("RGB", (270, 40), color=get_color())

    draw = ImageDraw.Draw(img)
    hc = ImageFont.truetype("static/font/hc.ttf", size=28)
    random_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_pychar = chr(random.randint(97, 122))
        random_uper_pychar = chr(random.randint(65, 90))
        random_choice = random.choice([random_num, random_low_pychar, random_uper_pychar])

        draw.text((i * 50, 5), random_choice, get_color(), font=hc)
        random_str += random_choice
    print(f"random_str:{random_str}")
    request.session["random_str"] = random_str

    # width = 270
    # height = 40
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, y1, x2, y2), fill=get_color())
    #
    # for i in range(100):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_color())

    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()
    return data