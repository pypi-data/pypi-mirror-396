from kevin_dl.workers.transforms.for_images.utils import convert_format, Image_Format
from kevin_dl.workers.transforms import Base_Transform
from kevin_dl.workers.variable import TRANSFORMS
from kevin_dl.tools.variable import TOOLS


@TRANSFORMS.register()
class Align_and_Crop_Face(Base_Transform):
    """
        人脸转正和裁剪
    """
    name = ":for_images:face:Align_and_Crop_Face"

    def cal(self, input_s, method=":face:alignment:by_bbox:affine_trans", **kwargs):
        """
            参数：
                input_s:                <dict>
                                            其中包含：
                                                image:      <np.array> shape [H, W, C]
                                                bbox or landmarks:      具体根据 method 对应的转正方法而定，比如：
                                                        - ":face:alignment:by_landmarks:affine_trans":      landmarks
                                                        - ":face:alignment:by_landmarks:prn_method":        landmarks
                                                        - ":face:alignment:by_bbox:affine_trans":           bbox
                method:                 <str> 要使用的人脸转正方法
                                            默认为 ":face:alignment:by_bbox:affine_trans"
                （其余参数请参考 method 对应的转正方法进行补充）
        """
        image = convert_format(image=input_s["image"], output_format=Image_Format.NP_ARRAY)
        assert image.ndim == 3
        worker = TOOLS.get(name=method)

        paras = input_s.copy()
        paras.update(kwargs)
        paras["image"] = image

        input_s["image"] = worker(**paras)

        # 补充详细信息
        input_s["details"] = dict(method=method)

        return input_s


if __name__ == '__main__':
    import os
    from PIL import Image
    from kevin_dl.workers.transforms.for_images.utils import get_format
    from kevin_toolbox.data_flow.file import json_

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test", "test_data", "data_1")
    image = Image.open(os.path.join(data_dir, "Tadokor_Koji_the_Japanese_representative.jpg"))
    ann_s = json_.read(file_path=os.path.join(data_dir, "ann_s_for_Tadokor_Koji_the_Japanese_representative.json"),
                       b_use_suggested_converter=True)
    image.show()

    # output_s = TRANSFORMS.get(name=":for_images:face:Align_and_Crop_Face")(
    #     b_include_details=True, method=":face:alignment:by_bbox:affine_trans",
    #     template="edge_corner", match_pattern="expanded_bbox",
    #     desired_face_size=108, desired_image_size=1.3
    # )(
    #     input_s=dict(image=image, bbox=ann_s["detect_faces"][0]["bbox"])
    # )
    output_s = TRANSFORMS.get(name=":for_images:face:Align_and_Crop_Face")(
        b_include_details=True, method=":face:alignment:by_bbox:affine_trans",
        template="edge_corner", match_pattern="expanded_bbox",
        desired_face_size=108, desired_image_size=1.3
    )(
        input_s=dict(image=image, bbox=ann_s["detect_faces"][0]["bbox"])
    )
    print(get_format(image=output_s["image"]))
    print(output_s)
    output = convert_format(image=output_s["image"], output_format=Image_Format.PIL_IMAGE)
    output.show()
