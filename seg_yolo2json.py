import json
import os
from PIL import Image
import numpy as np
import base64
import argparse

# img_dir = "test/json/"  # 图片地址
# txt_dir = "test/seg/yolo/"  # txt地址
#
# class_names = ["polyp"]  # 标签名称

def txt_to_json(img_dir, txt_dir, class_names):

    for txt_filename in os.listdir(txt_dir):
        if txt_filename.endswith('.txt'):
            base_filename = txt_filename[:-4]
            img_path = os.path.join(img_dir, base_filename + '.jpg')
            json_path = os.path.join(img_dir, base_filename + '.json')

            image_data = {
                "version": "5.5.0",
                "flags": {},
                "shapes": [],
                "imagePath": os.path.basename(img_path),
                "imageData": None,
                "imageHeight": None,
                "imageWidth": None
            }

            with Image.open(img_path) as img:
                img_array = np.array(img)
                height, width = img_array.shape[:2]
                image_data["imageHeight"] = height
                image_data["imageWidth"] = width

                with open(img_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read())
                    image_data["imageData"] = encoded_image.decode('utf-8')

            with open(os.path.join(txt_dir, txt_filename), 'r') as file:
                for line in file.readlines():
                    content = line.strip().split()
                    label_index = int(content[0])
                    points = [float(x) for x in content[1:]]

                    shape = {
                        "label": class_names[label_index],
                        "points": [[points[i] * width, points[i + 1] * height] for i in range(0, len(points), 2)],
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {}
                    }
                    image_data["shapes"].append(shape)

            with open(json_path, 'w') as json_file:
                json.dump(image_data, json_file, indent=2)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--img', type=str, default='./test/json')  # img and json
    parser.add_argument('--txt', type=str, default='./test/seg/yolo')   # txt
    parser.add_argument('--classes', type=str, default=['polyp'])  # txt

    args = parser.parse_args()

    img_dir = args.img
    txt_dir = args.txt
    class_names = args.classes

    txt_to_json(img_dir, txt_dir, class_names)



