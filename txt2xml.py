from xml.dom.minidom import Document
import os
import cv2
from tqdm import tqdm
import argparse

classes = ['type1', 'type2', 'type3']

def makexml(picPath, txtPath, xmlPath):
    datasetName = 'dataset'
    files = os.listdir(txtPath)
    for i, name in enumerate(tqdm(files)):
        if name == 'classes.txt':
            continue

        xmlBuilder = Document()
        annotation = xmlBuilder.createElement("annotation")
        xmlBuilder.appendChild(annotation)

        txtFile = open(os.path.join(txtPath, name))
        txtList = txtFile.readlines()
        txtFile.close()

        img_path = os.path.join(picPath, name.replace('.txt', '.jpg'))
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to read image {img_path}, skipping.")
            continue
        Pheight, Pwidth, Pdepth = img.shape

        # folder
        folder = xmlBuilder.createElement("folder")
        folder.appendChild(xmlBuilder.createTextNode(datasetName))
        annotation.appendChild(folder)

        # filename
        filename = xmlBuilder.createElement("filename")
        filename.appendChild(xmlBuilder.createTextNode(name[:-4] + ".jpg"))
        annotation.appendChild(filename)

        # size
        size = xmlBuilder.createElement("size")
        for tag, val in [("width", Pwidth), ("height", Pheight), ("depth", Pdepth)]:
            elem = xmlBuilder.createElement(tag)
            elem.appendChild(xmlBuilder.createTextNode(str(val)))
            size.appendChild(elem)
        annotation.appendChild(size)

        # objects
        for line in txtList:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls_id, x_center, y_center, w_norm, h_norm = parts
            cls_idx = int(cls_id)
            if cls_idx < 0 or cls_idx >= len(classes):
                print(f"Warning: class index {cls_idx} out of range, skipping.")
                continue

            obj = xmlBuilder.createElement("object")
            # name
            name_tag = xmlBuilder.createElement("name")
            name_tag.appendChild(xmlBuilder.createTextNode(classes[cls_idx]))
            obj.appendChild(name_tag)
            # pose, truncated, difficult
            for tag, text in [("pose", "Unspecified"), ("truncated", "0"), ("difficult", "0")]:
                elem = xmlBuilder.createElement(tag)
                elem.appendChild(xmlBuilder.createTextNode(text))
                obj.appendChild(elem)

            # bndbox
            bndbox = xmlBuilder.createElement("bndbox")
            x_center_f = float(x_center) * Pwidth + 1
            y_center_f = float(y_center) * Pheight + 1
            half_w = float(w_norm) * 0.5 * Pwidth
            half_h = float(h_norm) * 0.5 * Pheight
            coords = {
                "xmin": int(max(0, x_center_f - half_w)),
                "ymin": int(max(0, y_center_f - half_h)),
                "xmax": int(min(Pwidth, x_center_f + half_w)),
                "ymax": int(min(Pheight, y_center_f + half_h)),
            }
            for tag, val in coords.items():
                elem = xmlBuilder.createElement(tag)
                elem.appendChild(xmlBuilder.createTextNode(str(val)))
                bndbox.appendChild(elem)
            obj.appendChild(bndbox)
            annotation.appendChild(obj)

        # write XML
        xml_file = os.path.join(xmlPath, name.replace('.txt', '.xml'))
        with open(xml_file, 'w', encoding='utf-8') as f:
            xmlBuilder.writexml(f, indent='\t', newl='\n', addindent='\t')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert YOLO txt annotations to Pascal VOC XML.")
    parser.add_argument('--imgpath', type=str, default='./test/images', help='Path to images')
    parser.add_argument('--txtpath', type=str, default='./test/labels', help='Path to YOLO txt labels')
    parser.add_argument('--xmlpath', type=str, default='./test/3', help='Output path for XML')
    args = parser.parse_args()

    os.makedirs(args.xmlpath, exist_ok=True)

    makexml(args.imgpath, args.txtpath, args.xmlpath)
