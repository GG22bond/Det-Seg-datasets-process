import random
import copy
import cv2
import os
import math
import numpy as np
from skimage.util import random_noise
from lxml import etree, objectify
import xml.etree.ElementTree as ET
import argparse

class DataAugmentForObjectDetection():
    def __init__(self, rotation_rate=0.5, max_rotation_angle=5,
                 crop_rate=0.5, shift_rate=0.5, change_light_rate=0.5,
                 add_noise_rate=0.5, flip_rate=0.5,
                 cutout_rate=0.5, cut_out_length=50, cut_out_holes=1, cut_out_threshold=0.5,
                 is_addNoise=True, is_changeLight=True, is_cutout=True, is_rotate_img_bbox=True,
                 is_crop_img_bboxes=True, is_shift_pic_bboxes=True, is_filp_pic_bboxes=True):

        self.rotation_rate = rotation_rate
        self.max_rotation_angle = max_rotation_angle
        self.crop_rate = crop_rate
        self.shift_rate = shift_rate
        self.change_light_rate = change_light_rate
        self.add_noise_rate = add_noise_rate
        self.flip_rate = flip_rate
        self.cutout_rate = cutout_rate

        self.cut_out_length = cut_out_length
        self.cut_out_holes = cut_out_holes
        self.cut_out_threshold = cut_out_threshold
                     
        self.is_addNoise = is_addNoise
        self.is_changeLight = is_changeLight
        self.is_cutout = is_cutout
        self.is_rotate_img_bbox = is_rotate_img_bbox
        self.is_crop_img_bboxes = is_crop_img_bboxes
        self.is_shift_pic_bboxes = is_shift_pic_bboxes
        self.is_filp_pic_bboxes = is_filp_pic_bboxes

    # ----1.加噪声---- #
    def _addNoise(self, img):

        # return cv2.GaussianBlur(img, (11, 11), 0)

        var = 0.003 # gaussian

        return random_noise(img, mode="gaussian", var = var, clip=True) * 255


    # ---2.调整亮度--- #
    def _changeLight(self, img):
        alpha = random.uniform(0.55, 1)
        blank = np.zeros(img.shape, img.dtype)
        return cv2.addWeighted(img, alpha, blank, 1 - alpha, 0)

    # ---3.cutout--- #
    def _cutout(self, img, bboxes, length=100, n_holes=1, threshold=0.5):
        '''
        https://github.com/uoguelph-mlrg/Cuto ut/blob/master/util/cutout.py
        '''

        def cal_iou(boxA, boxB):

            # determine the (x, y)-coordinates of the intersection rectangle
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])

            if xB <= xA or yB <= yA:
                return 0.0

            # compute the area of intersection rectangle
            interArea = (xB - xA + 1) * (yB - yA + 1)

            # compute the area of both the prediction and ground-truth
            # rectangles
            boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
            boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
            iou = interArea / float(boxBArea)
            return iou

        # 得到h和w
        if img.ndim == 3:
            h, w, c = img.shape
        else:
            _, h, w, c = img.shape
        mask = np.ones((h, w, c), np.float32)
        for n in range(n_holes):
            chongdie = True 
            while chongdie:
                y = np.random.randint(h)
                x = np.random.randint(w)

                y1 = np.clip(y - length // 2, 0,
                             h)  
                y2 = np.clip(y + length // 2, 0, h)
                x1 = np.clip(x - length // 2, 0, w)
                x2 = np.clip(x + length // 2, 0, w)

                chongdie = False
                for box in bboxes:
                    if cal_iou([x1, y1, x2, y2], box) > threshold:
                        chongdie = True
                        break
            mask[y1: y2, x1: x2, :] = 0.
        img = img * mask
        return img

    # ---4.旋转--- #
    def _rotate_img_bbox(self, img, bboxes, angle=5, scale=1.):

        # 旋转图像
        w = img.shape[1]
        h = img.shape[0]
        # 角度变弧度
        rangle = np.deg2rad(angle)  # angle in radians
        # now calculate new image width and height
        nw = (abs(np.sin(rangle) * h) + abs(np.cos(rangle) * w)) * scale
        nh = (abs(np.cos(rangle) * h) + abs(np.sin(rangle) * w)) * scale
        # ask OpenCV for the rotation matrix
        rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)
        # calculate the move from the old center to the new center combined
        # with the rotation
        rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))
        # the move only affects the translation, so update the translation
        rot_mat[0, 2] += rot_move[0]
        rot_mat[1, 2] += rot_move[1]
        # 仿射变换
        rot_img = cv2.warpAffine(img, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))), flags=cv2.INTER_LANCZOS4)

        rot_bboxes = list()
        for bbox in bboxes:
            xmin = bbox[0]
            ymin = bbox[1]
            xmax = bbox[2]
            ymax = bbox[3]
            point1 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymin, 1]))
            point2 = np.dot(rot_mat, np.array([xmax, (ymin + ymax) / 2, 1]))
            point3 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymax, 1]))
            point4 = np.dot(rot_mat, np.array([xmin, (ymin + ymax) / 2, 1]))
            # 合并np.array
            concat = np.vstack((point1, point2, point3, point4))
            # 改变array类型
            concat = concat.astype(np.int32)
            # 得到旋转后的坐标
            rx, ry, rw, rh = cv2.boundingRect(concat)
            rx_min = rx
            ry_min = ry
            rx_max = rx + rw
            ry_max = ry + rh
            # 加入list中
            rot_bboxes.append([rx_min, ry_min, rx_max, ry_max])

        return rot_img, rot_bboxes

    # ---5.裁剪--- #
    def _crop_img_bboxes(self, img, bboxes):

        # 裁剪图像
        w = img.shape[1]
        h = img.shape[0]
        x_min = w  # 裁剪后的包含所有目标框的最小的框
        x_max = 0
        y_min = h
        y_max = 0
        for bbox in bboxes:
            x_min = min(x_min, bbox[0])
            y_min = min(y_min, bbox[1])
            x_max = max(x_max, bbox[2])
            y_max = max(y_max, bbox[3])

        d_to_left = x_min  # 包含所有目标框的最小框到左边的距离
        d_to_right = w - x_max  # 包含所有目标框的最小框到右边的距离
        d_to_top = y_min  # 包含所有目标框的最小框到顶端的距离
        d_to_bottom = h - y_max  # 包含所有目标框的最小框到底部的距离

        # 随机扩展这个最小框
        crop_x_min = int(x_min - random.uniform(0, d_to_left))
        crop_y_min = int(y_min - random.uniform(0, d_to_top))
        crop_x_max = int(x_max + random.uniform(0, d_to_right))
        crop_y_max = int(y_max + random.uniform(0, d_to_bottom))

        # 确保不要越界
        crop_x_min = max(0, crop_x_min)
        crop_y_min = max(0, crop_y_min)
        crop_x_max = min(w, crop_x_max)
        crop_y_max = min(h, crop_y_max)

        crop_img = img[crop_y_min:crop_y_max, crop_x_min:crop_x_max]

        # 裁剪boundingbox
        # 裁剪后的boundingbox坐标计算
        crop_bboxes = list()
        for bbox in bboxes:
            crop_bboxes.append([bbox[0] - crop_x_min, bbox[1] - crop_y_min, bbox[2] - crop_x_min, bbox[3] - crop_y_min])

        return crop_img, crop_bboxes

    # ---6.平移--- #
    def _shift_pic_bboxes(self, img, bboxes):

        # 平移图像
        w = img.shape[1]
        h = img.shape[0]
        x_min = w  # 裁剪后的包含所有目标框的最小的框
        x_max = 0
        y_min = h
        y_max = 0
        for bbox in bboxes:
            x_min = min(x_min, bbox[0])
            y_min = min(y_min, bbox[1])
            x_max = max(x_max, bbox[2])
            y_max = max(y_max, bbox[3])

        d_to_left = x_min  # 包含所有目标框的最大左移动距离
        d_to_right = w - x_max  # 包含所有目标框的最大右移动距离
        d_to_top = y_min  # 包含所有目标框的最大上移动距离
        d_to_bottom = h - y_max  # 包含所有目标框的最大下移动距离

        x = random.uniform(-(d_to_left - 1) / 3, (d_to_right - 1) / 3)
        y = random.uniform(-(d_to_top - 1) / 3, (d_to_bottom - 1) / 3)

        M = np.float32([[1, 0, x], [0, 1, y]])  # x为向左或右移动的像素值,正为向右负为向左; y为向上或者向下移动的像素值,正为向下负为向上
        shift_img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

        #  平移boundingbox
        shift_bboxes = list()
        for bbox in bboxes:
            shift_bboxes.append([bbox[0] + x, bbox[1] + y, bbox[2] + x, bbox[3] + y])

        return shift_img, shift_bboxes

    # ---7.镜像--- #
    def _filp_pic_bboxes(self, img, bboxes):

        # 翻转图像

        flip_img = copy.deepcopy(img)
        h, w, _ = img.shape

        sed = random.random()

        if 0 < sed < 0.33:  # 0.33的概率水平翻转，0.33的概率垂直翻转,0.33是对角反转
            flip_img = cv2.flip(flip_img, 0)  # _flip_x
            inver = 0
        elif 0.33 < sed < 0.66:
            flip_img = cv2.flip(flip_img, 1)  # _flip_y
            inver = 1
        else:
            flip_img = cv2.flip(flip_img, -1)  # flip_x_y
            inver = -1

        # 调整boundingbox
        flip_bboxes = list()
        for box in bboxes:
            x_min = box[0]
            y_min = box[1]
            x_max = box[2]
            y_max = box[3]

            if inver == 0:
                # 0：垂直翻转
                flip_bboxes.append([x_min, h - y_max, x_max, h - y_min])
            elif inver == 1:
                # 1：水平翻转
                flip_bboxes.append([w - x_max, y_min, w - x_min, y_max])
            elif inver == -1:
                # -1：水平垂直翻转
                flip_bboxes.append([w - x_max, h - y_max, w - x_min, h - y_min])
        return flip_img, flip_bboxes

    # 图像增强方法
    def dataAugment(self, img, bboxes):

        change_num = 0  # 改变的次数
        # print('------')
        while change_num < 1:  # 默认至少有一种数据增强生效

            if self.is_rotate_img_bbox:
                if random.random() > self.rotation_rate:  # 旋转
                    change_num += 1
                    angle = random.uniform(-self.max_rotation_angle, self.max_rotation_angle)
                    scale = random.uniform(0.7, 0.8)
                    img, bboxes = self._rotate_img_bbox(img, bboxes, angle, scale)

            if self.is_shift_pic_bboxes:
                if random.random() < self.shift_rate:  # 平移
                    change_num += 1
                    img, bboxes = self._shift_pic_bboxes(img, bboxes)

            if self.is_changeLight:
                if random.random() > self.change_light_rate:  # 改变亮度
                    change_num += 1
                    img = self._changeLight(img)

            if self.is_addNoise:
                if random.random() < self.add_noise_rate:  # 加噪声
                    change_num += 1
                    img = self._addNoise(img)
            if self.is_cutout:
                if random.random() < self.cutout_rate:  # cutout
                    change_num += 1
                    img = self._cutout(img, bboxes, length=self.cut_out_length, n_holes=self.cut_out_holes,
                                       threshold=self.cut_out_threshold)
            if self.is_filp_pic_bboxes:
                if random.random() < self.flip_rate:  # 翻转
                    change_num += 1
                    img, bboxes = self._filp_pic_bboxes(img, bboxes)

        return img, bboxes


class ToolHelper():

    def parse_xml(self, path):

        tree = ET.parse(path)
        root = tree.getroot()
        objs = root.findall('object')
        coords = list()
        for ix, obj in enumerate(objs):
            name = obj.find('name').text
            box = obj.find('bndbox')
            x_min = int(box[0].text)
            y_min = int(box[1].text)
            x_max = int(box[2].text)
            y_max = int(box[3].text)
            coords.append([x_min, y_min, x_max, y_max, name])
        return coords

    def save_img(self, file_name, save_folder, img):
        cv2.imwrite(os.path.join(save_folder, file_name), img)

    def save_xml(self, file_name, save_folder, img_info, height, width, channel, bboxs_info):

        folder_name, img_name = img_info

        E = objectify.ElementMaker(annotate=False)

        anno_tree = E.annotation(
            E.folder(folder_name),
            E.filename(img_name),
            E.path(os.path.join(folder_name, img_name)),
            E.source(
                E.database('Unknown'),
            ),
            E.size(
                E.width(width),
                E.height(height),
                E.depth(channel)
            ),
            E.segmented(0),
        )

        labels, bboxs = bboxs_info
        for label, box in zip(labels, bboxs):
            anno_tree.append(
                E.object(
                    E.name(label),
                    E.pose('Unspecified'),
                    E.truncated('0'),
                    E.difficult('0'),
                    E.bndbox(
                        E.xmin(box[0]),
                        E.ymin(box[1]),
                        E.xmax(box[2]),
                        E.ymax(box[3])
                    )
                ))

        etree.ElementTree(anno_tree).write(os.path.join(save_folder, file_name), pretty_print=True)


if __name__ == '__main__':

    is_endwidth_dot = True

    dataAug = DataAugmentForObjectDetection()

    toolhelper = ToolHelper()

    # 获取相关参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--need_num', type=int , default=20)
    parser.add_argument('--source_img_path', type=str, default='valid/images')
    parser.add_argument('--source_xml_path', type=str, default='valid/Annotations')
    parser.add_argument('--save_img_path', type=str, default='data_amp_FIN/images/val')
    parser.add_argument('--save_xml_path', type=str, default='data_amp_FIN/Annotations/val')
    args = parser.parse_args()

    need_num = args.need_num

    source_img_path = args.source_img_path
    source_xml_path = args.source_xml_path

    save_img_path = args.save_img_path
    save_xml_path = args.save_xml_path

    if not os.path.exists(save_img_path):
        os.mkdir(save_img_path)

    if not os.path.exists(save_xml_path):
        os.mkdir(save_xml_path)

    for parent, _, files in os.walk(source_img_path):
        files.sort()
        for file in files:
            cnt = 0
            pic_path = os.path.join(parent, file)
            xml_path = os.path.join(source_xml_path, file[:-4] + '.xml')
            values = toolhelper.parse_xml(xml_path)
            coords = [v[:4] for v in values]
            labels = [v[-1] for v in values]

            if is_endwidth_dot:

                dot_index = file.rfind('.')
                _file_prefix = file[:dot_index]
                _file_suffix = file[dot_index:]
            img = cv2.imread(pic_path)

            while cnt < need_num:
                auged_img, auged_bboxes = dataAug.dataAugment(img, coords)
                auged_bboxes_int = np.array(auged_bboxes).astype(np.int32)
                height, width, channel = auged_img.shape
                img_name = '{}_{}{}'.format(_file_prefix, cnt + 1, _file_suffix)
                # save img
                toolhelper.save_img(img_name, save_img_path,auged_img)
                # save xml
                toolhelper.save_xml('{}_{}.xml'.format(_file_prefix, cnt + 1),
                                    save_xml_path, (save_img_path, img_name), height, width, channel,
                                    (labels, auged_bboxes_int))

                print(img_name)
                cnt += 1

'''
python amplification.py --need_num 25 --source_img_path train/images --source_xml_path train/Annotations --save_img_path train_amp/images --save_xml_path train_amp/Annotations

python amplification.py --need_num 25 --source_img_path valid/images --source_xml_path valid/Annotations --save_img_path val_amp/images --save_xml_path val_amp/Annotations

python amplification.py --need_num 30 --source_img_path train/images --source_xml_path train/Annotations --save_img_path new/images/train --save_xml_path new/annotations/train

python amplification.py --need_num 30 --source_img_path valid/images --source_xml_path valid/Annotations --save_img_path new/images/val --save_xml_path new/annotations/val
'''
