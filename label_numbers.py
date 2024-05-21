import os
import random
import matplotlib.pyplot as plt
import numpy as np

txt_path = 'data_amp_FIN/1/labels/test'
classes_file = os.path.join(txt_path, 'classes.txt')

# 读取类别名称
with open(classes_file, 'r') as f:
    class_list = [line.strip() for line in f.readlines()]

class_num = len(class_list)
class_num_list = [0] * class_num

# 获取标签文件列表
labels_list = os.listdir(txt_path)

# 遍历每个标签文件
for label_file in labels_list:
    file_path = os.path.join(txt_path, label_file)

    # 确保不处理 classes.txt 文件自身
    if os.path.isfile(file_path) and label_file != 'classes.txt':
        # 使用上下文管理器打开文件
        with open(file_path, 'r') as file:
            file_data = file.readlines()

        # 处理文件中的每一行
        for every_row in file_data:
            class_val = every_row.split(' ')[0]
            class_ind = int(class_val)
            class_num_list[class_ind] += 1

# 输出结果
for class_name, count in zip(class_list, class_num_list):
    print(f"{class_name}: {count}")
print('total:', sum(class_num_list))

# 生成随机颜色
colors = ['#'+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(class_num)]

# 竖向柱状图
plt.figure(figsize=(6, 6))
bars = plt.bar(np.arange(class_num), class_num_list, color=colors, width=0.3, tick_label=class_list)
plt.xlabel('Class Names')
plt.ylabel('Counts')
plt.xticks(rotation=45, ha='right')

for bar, count in zip(bars, class_num_list):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count), ha='center', va='bottom')

plt.tight_layout()
plt.legend(bars, class_list, loc='best')
plt.savefig('./img/1.jpg')
plt.show()

# 横向柱状图
plt.figure(figsize=(6, 6))
bars = plt.barh(np.arange(class_num), class_num_list, color=colors, height=0.3, tick_label=class_list)
plt.xlabel('Counts')
plt.ylabel('Class Names')
plt.yticks(rotation=45, ha='right')

for bar, count in zip(bars, class_num_list):
    plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, str(count), ha='left', va='center')

plt.tight_layout()
plt.legend(bars, class_list, loc='best')
plt.savefig('./img/2.jpg')
plt.show()


# 饼状图
plt.figure(figsize=(6, 6))
plt.pie(class_num_list, labels=class_list, colors=colors, autopct='%1.1f%%', startangle=140)
plt.axis('equal')

plt.tight_layout()
plt.legend(bars, class_list, loc='best')
plt.savefig('./img/3.jpg')
plt.show()
