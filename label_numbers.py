import os

class_num = 3
txt_path = 'data_amp_FIN/labels/train'

class_list = [i for i in range(class_num)]
class_num_list = [0 for i in range(class_num)]
labels_list = os.listdir(txt_path)
for i in labels_list:
    file_path = os.path.join(txt_path, i)
    file = open(file_path, 'r')
    file_data = file.readlines()
    for every_row in file_data:
        class_val = every_row.split(' ')[0]
        class_ind = class_list.index(int(class_val))
        class_num_list[class_ind] += 1
    file.close()

print(class_num_list)
print('total:', sum(class_num_list))