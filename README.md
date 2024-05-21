# Detection-datasets-process
一些关于目标检测数据集处理的脚本。

## amp.py
#### 数据扩增：
```
python amp.py --need_num 10 --source_img_path IMGPATH --source_xml_path XMLPATH --save_img_path SAVE_IMGPATH --save_xml_path SAVE_XMLPATH
```
## image_size.py
#### 数据大小调整：
```
python image_size.py --size NUM --input INPUT_PATH --output OUTPUT_PATH
```
## xml2txt.py
#### VOC的xml转yolo的txt
```
python xml2txt.py --imgpath IMGPATH --xmlpath XMLPATH --txtpath TXTPATH
```

## txt2xml.py
#### yolo的txt转VOC的xml
```
python txt2xml.py --imgpath IMGPATH --txtpath TXTPATH --xmlpath XMLPATH
```
