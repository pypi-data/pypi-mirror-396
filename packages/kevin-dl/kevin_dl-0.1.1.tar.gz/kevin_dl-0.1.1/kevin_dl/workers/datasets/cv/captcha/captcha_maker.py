import os
import copy
import torchvision.transforms as T
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import unicodedata
from kevin_toolbox.patches.for_numpy.random import get_rng
from kevin_toolbox.patches.for_matplotlib.color import Color_Format, convert_format

settings = [
    {
        "name": ":for_images:torchvision:ToTensor",
        "paras": {}
    },
    {
        "name": ":for_images:torchvision:RandomAffine",
        "paras": {
            "degrees": 45, "translate": (0.05, 0.1), "shear": 45, "fill": (1.0, 1.0, 1.0),
        }
    },
    {
        "name": ":for_images:torchvision:GaussianBlur",
        "paras": {
            "kernel_size": 3, "sigma": (0.1, 1.5)
        }
    },

    {
        "name": ":for_images:torchvision:ColorJitter",
        "paras": {
            "brightness": 0.3, "contrast": 0.3, "saturation": 0.3
        }
    }
]


def is_fullwidth(char):
    """判断字符是否为全角（Fullwidth）"""
    return unicodedata.east_asian_width(char) in ['F', 'W']


class Captcha_Maker:
    """
        生成验证码图像
            支持倾斜、扭曲、模糊、加噪点、不同颜色等干扰
    """

    def __init__(self, **kwargs):
        """
            参数：
                width、height:       <int> 图像宽、高
                font_size:          <int> 字体大小
                color_of_bg:        <int/float/list of ints or floats> 背景颜色
                b_use_transforms:   <boolean> 是否使用变换
                transforms:         <Pipeline/dict of paras/list of setting> 要使用的变换
                b_add_noise_line:   <boolean> 是否添加扰动线
                b_add_noise_point:  <boolean> 是否添加噪点
                max_offset_of_text: <list of int/float> 随机偏离中心的最大幅度
                                        依次为 (offset_of_width, offset_of_height)
                                        当给定值为 float 时，表示以不超出（使用 transforms 变换前的）画布为限制，所允许的最大偏移量的多少倍，
                                        当给定值为 int 时，表示像素值
        """
        super().__init__()

        # 默认参数
        paras = {
            #
            "width": 200,
            "height": 200,
            "font_size": 42,
            "color_options_of_text": None,
            "color_of_bg": 255,
            #
            "max_offset_of_text": (1.0, 1.0),
            "b_use_transforms": True,
            "transforms": None,
            "b_add_noise_line": True,
            "color_options_of_line": ("gray",),
            "b_add_noise_point": True,
            #
            "seed": 114514,
            "rng": None,
        }

        # 获取参数
        paras.update(kwargs)

        # 校验参数
        if not isinstance(paras["color_of_bg"], (list, tuple)):
            paras["color_of_bg"] = [paras["color_of_bg"]] * 3
        if isinstance(paras["color_of_bg"][0], (float,)):
            paras["color_of_bg"] = [int(np.clip(i * 255, 0, 255)) for i in paras["color_of_bg"]]
        else:
            paras["color_of_bg"] = [np.clip(i, 0, 255) for i in paras["color_of_bg"]]
        paras["color_of_bg"] = tuple(paras["color_of_bg"])
        for k in ["color_options_of_line", "color_options_of_text"]:
            if paras[k] is not None:
                paras[k] = [convert_format(var=i, output_format=Color_Format.RGBA_ARRAY)[:3] for i in paras[k]]
        if not isinstance(paras["max_offset_of_text"], (tuple, list)):
            paras["max_offset_of_text"] = [paras["max_offset_of_text"], ] * 2

        self._rng = get_rng(seed=paras["seed"], rng=paras["rng"])
        transforms = paras["transforms"]
        if paras["b_use_transforms"]:
            from kevin_dl.workers.transforms import Pipeline
            if transforms is None:
                transforms = copy.deepcopy(settings)
                transforms[1]["paras"]["fill"] = tuple(np.asarray(paras["color_of_bg"]) / 255)
            if not isinstance(transforms, Pipeline):
                if isinstance(transforms, (dict,)):
                    transforms = Pipeline(**transforms)
                elif isinstance(transforms, (list,)):
                    transforms = Pipeline(settings=transforms, b_include_details=False, seed=paras["seed"])
            assert isinstance(transforms, Pipeline)
        self.transforms = transforms
        try:
            self.font = ImageFont.truetype(font=os.path.expanduser("~/.kvt_data/fonts/SimHei.ttf"),
                                           size=paras["font_size"])
        except:
            self.font = ImageFont.load_default(size=paras["font_size"])
        self.paras = paras

    def generate(self, text, width=None, height=None, font_size=None):
        """
            参数：
                text:               <str> 要显示的验证码文本
                width、height:       <int> 图像宽、高
                font_size:          <int> 字体大小

            返回：
                PIL.Image: 添加干扰后的验证码图像
        """
        width = width if width is not None else self.paras["width"]
        height = height if height is not None else self.paras["height"]
        font_size = font_size if font_size is not None else self.paras["font_size"]
        self.font.size = font_size

        # 2. 创建空白图像
        image = Image.new('RGB', size=(width, height), color=self.paras["color_of_bg"])
        draw = ImageDraw.Draw(image)

        # 使用系统默认字体（或换成指定路径）

        # 3. 绘制文字（带颜色）
        for i, char in enumerate(text):
            if self.paras["color_options_of_text"] is None:
                color = tuple(self._rng.randint(10, 255) for _ in range(3))
            else:
                color = tuple(self._rng.choice(self.paras["color_options_of_text"]))
            w = width // len(text)
            h = height
            x_offset, y_offset = self.paras["max_offset_of_text"]
            y_mid = (h - font_size) // 2
            if y_offset != 0:
                if isinstance(y_offset, (float,)):
                    y_offset = int((h - font_size) * y_offset / 2)
                y_offset = self._rng.randint(-y_offset, y_offset + 1)
            if x_offset != 0:
                if isinstance(x_offset, (float,)):
                    if is_fullwidth(char=char):
                        x_offset = int((w - font_size) * x_offset / 2)
                    else:
                        x_offset = int((w - font_size // 2) * x_offset / 2)
                    x_offset = self._rng.randint(-x_offset, x_offset + 1)
            if is_fullwidth(char=char):
                x_mid = (w - font_size) // 2 + i * w
            else:
                x_mid = (w - font_size // 2) // 2 + i * w
            x, y = x_mid + x_offset, y_mid + y_offset

            draw.text(xy=(x, y), text=char, fill=color, font=self.font)

        # 4. 使用 torchvision 添加干扰变换
        if self.paras["b_use_transforms"]:
            img_tensor = self.transforms(input_s=dict(image=image))["image"]
            image = T.ToPILImage()(img_tensor)
            draw = ImageDraw.Draw(image)

        # 添加干扰线
        if self.paras["b_add_noise_line"]:
            for _ in range(self._rng.randint(0, 5)):
                x1, y1 = self._rng.randint(0, width), self._rng.randint(0, height)
                x2, y2 = self._rng.randint(0, width), self._rng.randint(0, height)
                if self.paras["color_options_of_line"] is None:
                    color = tuple(self._rng.randint(10, 255) for _ in range(3))
                else:
                    color = tuple(self._rng.choice(self.paras["color_options_of_line"]))
                draw.line(((x1, y1), (x2, y2)), fill=color,
                          width=self._rng.randint(1, int(max(min(height, width) * 0.05, 3))))
        # 添加随机点噪声
        if self.paras["b_add_noise_point"]:
            for _ in range(300):
                x, y = self._rng.randint(0, width - 1), self._rng.randint(0, height - 1)
                dot_color = tuple(self._rng.randint(0, 255) for _ in range(3))
                draw.point((x, y), fill=dot_color)

        return image


if __name__ == "__main__":
    captcha_maker = Captcha_Maker(seed=256, b_use_transforms=True)
    captcha_image = captcha_maker.generate(text="A大是")
    captcha_image.show()
    # captcha_maker = Captcha_Maker(seed=256, b_use_transforms=False, width=400, height=200,
    #                               font_size=50, max_offset_of_text=(0.9, 0.9))
    # captcha_image = captcha_maker.generate(text="A")
    # captcha_image.show()  # 显示验证码图像
