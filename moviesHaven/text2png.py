# coding=utf8
import os

from PIL import ImageFont, Image, ImageDraw


class ImageLib(object):
    def __init__(self):
        self.font_location = '/usr/share/fonts/truetype/DejaVuSans.ttf'
        self.width = 300
        self.height = 200
        self.font_color = "#ffffff"
        self.bg_color = "#31A8FF"
        self.text = "Hello, bub!"
        self.image_format = "PNG"

    def text2image(self, text=None, image_path=None, background_image=None, **kwargs):
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
        font_location = kwargs.get('font_location', None) if kwargs.get('font_location', None) else self.font_location
        if image_path and text:
            if os.path.exists(image_path):
                if background_image:
                    image = Image.open(background_image)
                    width, height = image.size
                    print(width, height)
                else:
                    image = Image.new("RGBA", (width, height), 'black')
                draw = ImageDraw.Draw(image)
                draw.ellipse((-87, -87, 600, 600), self.bg_color, self.bg_color)
                # draw.arc((40,50,50,55), 0, 360, 0)
                print(draw)
                text_length = (len(text)-1) if (len(text)-1) > 0 else 1
                fnt_size = width//text_length
                # fnt_size = width//1
                if os.path.exists(font_location):
                    font = ImageFont.truetype(font_location, fnt_size)
                else:
                    font = ImageFont.truetype(self.font_location, fnt_size)
                w, h = draw.textsize(text, font=font)
                draw_tuple = int((width - w) / 2), int((height - h) / 2)
                print(width, height)
                print(w, h)
                print(draw_tuple)
                try:
                    # draw.text((50, 50), "Sample Text", (255, 255, 255), font=font)
                    draw.text(draw_tuple, text, font_color, font=font)
                except Exception as e:
                    print(e)
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
    for i in range(1800, 2050):
        image_obj.text2image(text=str(i),
                             # background_image='/home/quixom/Project/meta_fetcher/staticfiles/assets/default_image.png',
                             image_path='/home/quixom/Project/meta_fetcher/static/fonts/years/',
                             font_location='/home/quixom/Project/meta_fetcher/staticfiles/assets/fonts/SovietProgram.ttf',
                             width=512, height=512)
