# coding=utf8
import os

from PIL import ImageFont, Image, ImageDraw


class ImageLib(object):
    def __init__(self):
        self.font_location = '/usr/share/fonts/truetype/DejaVuSans.ttf'
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
        font_color = kwargs.get('font_color', None) if kwargs.get('font_color', None) else self.font_color
        bg_color = kwargs.get('bg_color', None) if kwargs.get('bg_color', None) else self.bg_color
        font_location = kwargs.get('font_location', None) if kwargs.get('font_location', None) else self.font
        if image_path and text:
            if os.path.exists(image_path):
                image = Image.new("RGBA", (width, height), bg_color)
                draw = ImageDraw.Draw(image)
                if os.path.exists(font_location):
                    font = ImageFont.truetype(font_location, width//(len(text)-1))
                else:
                    font = ImageFont.truetype(self.font_location, width//(len(text)-1))
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


if __name__ == "__main__":
    image_obj = ImageLib()
    image_obj.text2image(text="2013",
                         image_path='/home/quixom/Project/meta_fetcher/static/fonts/',
                         width=500, height=500)
