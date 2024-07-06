import os
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import argparse

def csv_to_xml(image_folder, csv_folder, output_folder):

    for csv_file in os.listdir(csv_folder):
        if csv_file.endswith('.csv'):
            image_filename = csv_file.replace('.csv', '.jpg')
            image_path = os.path.join(image_folder, image_filename)
            csv_path = os.path.join(csv_folder, csv_file)

            # 读取图像尺寸
            with Image.open(image_path) as img:
                width, height = img.size

            # 读取CSV文件
            annotations = pd.read_csv(csv_path)

            # 创建XML文件的根节点
            annotation = ET.Element('annotation')

            # 添加文件名和路径节点
            ET.SubElement(annotation, 'filename').text = image_filename
            ET.SubElement(annotation, 'path').text = image_path

            # 创建size节点
            size = ET.SubElement(annotation, 'size')
            ET.SubElement(size, 'width').text = str(width)
            ET.SubElement(size, 'height').text = str(height)
            ET.SubElement(size, 'depth').text = str(3)

            # 遍历
            for index, row in annotations.iterrows():
                obj = ET.SubElement(annotation, 'object')
                ET.SubElement(obj, 'name').text = 'polyp'
                bndbox = ET.SubElement(obj, 'bndbox')
                ET.SubElement(bndbox, 'xmin').text = str(row['xmin'])
                ET.SubElement(bndbox, 'ymin').text = str(row['ymin'])
                ET.SubElement(bndbox, 'xmax').text = str(row['xmax'])
                ET.SubElement(bndbox, 'ymax').text = str(row['ymax'])

            # 创建
            tree = ET.ElementTree(annotation)
            xml_str = ET.tostring(annotation, 'utf-8')
            pretty_xml = parseString(xml_str).toprettyxml(indent="    ")
            pretty_xml = '\n'.join(pretty_xml.split('\n')[1:])

            # 保存
            xml_output_path = os.path.join(output_folder, csv_file.replace('.csv', '.xml'))
            with open(xml_output_path, 'w') as f:
                f.write(pretty_xml)

# python csv2xml.py --img_path ./train/images --csv_path ./train/bbox --xml_path ./train/xml
# python csv2xml.py --img_path ./train/images --csv_path ./train/bbox --xml_path ./train/xml

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--imgpath', type=str, default='./test/images')
    parser.add_argument('--csvpath', type=str, default='./test/bbox')
    parser.add_argument('--xmlpath', type=str, default='./test/xml')

    args = parser.parse_args()

    imgpath = args.imgpath
    csvpath = args.csvpath
    xmlpath = args.xmlpath

    os.makedirs(xmlpath, exist_ok=True)

    csv_to_xml(imgpath, csvpath, xmlpath)