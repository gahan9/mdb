# coding=utf8
import os

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


class ImageLib(object):
    def __init__(self):
        self.font = '/usr/share/fonts/truetype/DejaVuSans.ttf'
        self.width = 300
        self.height = 200
        self.font_color = "#ffff00"
        self.bg_color = "#00ffff"
        self.text = "Hello, bub!"
        self.image_format = "PNG"

    def text2image(self, text=None, image_path=None, **kwargs):
        # image_dir = os.path.dirname(image_path)
        if not text:
            return "No text given"
        if not image_path:
            return "Kindly specify target image_path and check for permission"
        # set up all necessary parameters
        width = kwargs.get('width', None) if kwargs.get('width', None) else self.width
        height = kwargs.get('height', None) if kwargs.get('height', None) else self.height
        font = kwargs.get('font', None) if kwargs.get('font', None) else self.font
        font_color = kwargs.get('font_color', None) if kwargs.get('font_color', None) else self.font_color
        bg_color = kwargs.get('bg_color', None) if kwargs.get('bg_color', None) else self.bg_color
        if image_path and text:
            if os.path.exists(image_path):
                image = Image.new("RGBA", (width, height), bg_color)
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", width//(len(text)-1))
                w, h = draw.textsize(text, font=font)
                draw.text(((width - w) / 2, (height - h) / 2), text, font_color, font=font)
                image_name = os.path.join(image_path, "{}.{}".format(text, self.image_format))
                try:
                    image.save(image_name, self.image_format)
                except Exception as e:
                    return "Exception in saving image with text: {}\nreason: {}".format(text, e)
            else:
                return "Image path does not exist"
        else:
            return "Unknown Issue..."


def text2png(text, img_path, color="#ffff00", bgcolor="#00ffffff", font_path=None, font_size=150,
             l_padding=3, r_padding=3, width=500, height=500):
    # link_back = "created by J@RVIS"
    # font_link_back = ImageFont.truetype('/usr/share/fonts/truetype/DejaVuSans.ttf', 8)
    # link_backx = font_link_back.getsize(link_back)[0]
    # link_back_height = font_link_back.getsize(link_back)[1]

    # font = ImageFont.load_default() if font_path else ImageFont.truetype(font_path, font_size)

    img = Image.new("RGBA", (width, height), (120, 20, 20))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", font_size)
    draw.text((100, 100), text, color, font=font)
    img.save(img_path)


# show time
if __name__ == "__main__":
    image_obj = ImageLib()
    image_obj.text2image(text="2013",
                         image_path='/home/quixom/Project/meta_fetcher/static/fonts/',
                         width=500, height=500)
    # text2png("2013", '/home/quixom/Project/meta_fetcher/static/fonts/test.png',
    #          font_path="/home/quixom/Project/meta_fetcher/static/fonts/Monofett.ttf")
