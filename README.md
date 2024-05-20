# Detection-datasets-process
一些关于目标检测数据集处理的脚本。

## amp.py
```
数据扩增：
python amp.py --need_num 10 --source_img_path train/images --source_xml_path train/Annotations --save_img_path train_amp/images --save_xml_path train_amp/Annotations
```
## image_size.py
```
图片大小调整
```
### xml2txt.py
```
VOC的xml转yolo的txt
python xml2txt.py --imgpath new/images/train --xmlpath new/annotations/train --txtpath new/labels/train
```


