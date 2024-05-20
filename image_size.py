import os
from PIL import Image
import argparse

def resize_images(input_folder, output_folder, scale_factor=0.25):
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有图片文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                # 打开图片文件
                with Image.open(input_path) as img:
                    # 获取原始图片的大小
                    original_size = img.size

                    # 计算新的尺寸
                    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))

                    # 调整图片大小
                    img_resized = img.resize(new_size)

                    # 将图片转换为RGB模式（防止有些图片是RGBA模式）
                    img_resized = img_resized.convert('RGB')

                    # 保存调整大小后的图片，使用原始文件名
                    img_resized.save(output_path, format=img.format)

                    print(f"{filename}: 原大小 {original_size} -> 新大小 {new_size}, 已保存到 {output_path}")

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")


# input_folder = 'test/images'
# output_folder = 'test/images-new'

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--input', type=str, default='')
    parser.add_argument('--output', type=str, default='')

    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output

    resize_images(input_folder, output_folder, scale_factor=0.25)
