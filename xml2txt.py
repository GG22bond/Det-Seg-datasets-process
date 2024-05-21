from xml.dom.minidom import Document
import os
import cv2
from tqdm import tqdm
import argparse

def makexml(picPath, txtPath, xmlPath, datasetName):

    dic = {'0': "type1",
           '1': "type2",
           '2': "type3",
           # ....
           }
    files = os.listdir(txtPath)
    for i, name in enumerate(tqdm(files)):
        if name == 'classes.txt':
            continue
        xmlBuilder = Document()
        annotation = xmlBuilder.createElement("annotation")  # annotation标签
        xmlBuilder.appendChild(annotation)
        txtFile = open(os.path.join(txtPath, name))
        txtList = txtFile.readlines()
        img = cv2.imread(os.path.join(picPath, name.replace('txt', 'jpg')))
        Pheight, Pwidth, Pdepth = img.shape

        folder = xmlBuilder.createElement("folder")  # folder标签
        foldercontent = xmlBuilder.createTextNode(datasetName)
        folder.appendChild(foldercontent)
        annotation.appendChild(folder)  # folder标签结束

        filename = xmlBuilder.createElement("filename")  # filename标签
        filenamecontent = xmlBuilder.createTextNode(name[0:-4] + ".jpg")
        filename.appendChild(filenamecontent)
        annotation.appendChild(filename)  # filename标签结束

        size = xmlBuilder.createElement("size")  # size标签
        width = xmlBuilder.createElement("width")  # size子标签width
        widthcontent = xmlBuilder.createTextNode(str(Pwidth))
        width.appendChild(widthcontent)
        size.appendChild(width)  # size子标签width结束

        height = xmlBuilder.createElement("height")  # size子标签height
        heightcontent = xmlBuilder.createTextNode(str(Pheight))
        height.appendChild(heightcontent)
        size.appendChild(height)  # size子标签height结束

        depth = xmlBuilder.createElement("depth")  # size子标签depth
        depthcontent = xmlBuilder.createTextNode(str(Pdepth))
        depth.appendChild(depthcontent)
        size.appendChild(depth)  # size子标签depth结束

        annotation.appendChild(size)  # size标签结束

        for j in txtList:
            oneline = j.strip().split(" ")
            object = xmlBuilder.createElement("object")  # object 标签
            picname = xmlBuilder.createElement("name")  # name标签
            namecontent = xmlBuilder.createTextNode(dic[oneline[0]])
            picname.appendChild(namecontent)
            object.appendChild(picname)  # name标签结束

            pose = xmlBuilder.createElement("pose")  # pose标签
            posecontent = xmlBuilder.createTextNode("Unspecified")
            pose.appendChild(posecontent)
            object.appendChild(pose)  # pose标签结束

            truncated = xmlBuilder.createElement("truncated")  # truncated标签
            truncatedContent = xmlBuilder.createTextNode("0")
            truncated.appendChild(truncatedContent)
            object.appendChild(truncated)  # truncated标签结束

            difficult = xmlBuilder.createElement("difficult")  # difficult标签
            difficultcontent = xmlBuilder.createTextNode("0")
            difficult.appendChild(difficultcontent)
            object.appendChild(difficult)  # difficult标签结束

            bndbox = xmlBuilder.createElement("bndbox")  # bndbox标签
            xmin = xmlBuilder.createElement("xmin")  # xmin标签
            mathData = int(((float(oneline[1])) * Pwidth + 1) - (float(oneline[3])) * 0.5 * Pwidth)
            xminContent = xmlBuilder.createTextNode(str(mathData))
            xmin.appendChild(xminContent)
            bndbox.appendChild(xmin)  # xmin标签结束

            ymin = xmlBuilder.createElement("ymin")  # ymin标签
            mathData = int(((float(oneline[2])) * Pheight + 1) - (float(oneline[4])) * 0.5 * Pheight)
            yminContent = xmlBuilder.createTextNode(str(mathData))
            ymin.appendChild(yminContent)
            bndbox.appendChild(ymin)  # ymin标签结束

            xmax = xmlBuilder.createElement("xmax")  # xmax标签
            mathData = int(((float(oneline[1])) * Pwidth + 1) + (float(oneline[3])) * 0.5 * Pwidth)
            xmaxContent = xmlBuilder.createTextNode(str(mathData))
            xmax.appendChild(xmaxContent)
            bndbox.appendChild(xmax)  # xmax标签结束

            ymax = xmlBuilder.createElement("ymax")  # ymax标签
            mathData = int(((float(oneline[2])) * Pheight + 1) + (float(oneline[4])) * 0.5 * Pheight)
            ymaxContent = xmlBuilder.createTextNode(str(mathData))
            ymax.appendChild(ymaxContent)
            bndbox.appendChild(ymax)  # ymax标签结束

            object.appendChild(bndbox)  # bndbox标签结束

            annotation.appendChild(object)  # object标签结束

        f = open(os.path.join(xmlPath, name.replace('txt', 'xml')), 'w')
        xmlBuilder.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
        f.close()


if __name__ == "__main__":

    # python txt2xml.py --imgpath ./valid/images --txtpath ./valid/labels --xmlpath ./valid/ann

    parser = argparse.ArgumentParser()

    parser.add_argument('--imgpath', type= str, default='./valid/images')  # 原图文件夹路径
    parser.add_argument('--txtpath', type=str, default='./valid/labels')   # 原txt标签文件夹路径
    parser.add_argument('--xmlpath', type=str, default='./valid/ann')   # 保存xml文件夹路径
    parser.add_argument('--datasetname',type=str, default='dataset')  # 数据集名称
    args = parser.parse_args()

    imgpath = args.imgpath
    txtpath = args.txtpath
    xmlpath = args.xmlpath
    datasetName = args.datasetname

    os.makedirs(xmlpath) if not os.path.exists(xmlpath) else None
    makexml(imgpath, txtpath, xmlpath, datasetName)
