import os
import json
import shutil

rate_train = 0.8
rate_valid = 0.1
# rate_testt = 0.1

folder_input = "/home/iservcloud_com/component-data-generator/data/output"

folder_output = "/home/iservcloud_com/component-data-generator/data/custom_data"
folder_output_train = "/home/iservcloud_com/component-data-generator/data/custom_data/train"
folder_output_train_images = "/home/iservcloud_com/component-data-generator/data/custom_data/train/images"
folder_output_train_labels = "/home/iservcloud_com/component-data-generator/data/custom_data/train/labels"

folder_output_valid = "/home/iservcloud_com/component-data-generator/data/custom_data/valid"
folder_output_valid_images = "/home/iservcloud_com/component-data-generator/data/custom_data/valid/images"
folder_output_valid_labels = "/home/iservcloud_com/component-data-generator/data/custom_data/valid/labels"

folder_output_testt = "/home/iservcloud_com/component-data-generator/data/custom_data/testt"
folder_output_testt_images = "/home/iservcloud_com/component-data-generator/data/custom_data/testt/images"
folder_output_testt_labels = "/home/iservcloud_com/component-data-generator/data/custom_data/testt/labels"

os.makedirs(folder_output_train_images, exist_ok=True)
os.makedirs(folder_output_train_labels, exist_ok=True)

os.makedirs(folder_output_valid_images, exist_ok=True)
os.makedirs(folder_output_valid_labels, exist_ok=True)

os.makedirs(folder_output_testt_images, exist_ok=True)
os.makedirs(folder_output_testt_labels, exist_ok=True)

# generate all keys
for json_file in os.listdir(folder_input):
    if json_file.endswith((".txt", "png")):
        continue
    json_path = os.path.join(folder_input, json_file)
    print(json_path)
    with open(json_path, "r") as f:
        json_dict = json.load(f)
    classSet = []
    for key, value in json_dict["components_quantity"].items():
        classSet.append(key)
    with open(f"{folder_output}/data.yaml", "w") as w:
        w.write(f"train: {folder_output_train_images}\n")
        w.write(f"val: {folder_output_valid_images}\n")
        w.write(f"test: {folder_output_testt_images}\n")
        w.write("\n")
        w.write(f"nc: {len(classSet)}\n")
        w.write(f"names: {classSet}")
    break

file_count = len(os.listdir(folder_input))
total_file_count = file_count // 3
print(f"total_file_coun={total_file_count}")
# 3 possible {file_name_uuid}.json
#            {file_name_uuid}.txt
#            {file_name_uuid}.png

train_valid_bound_index = total_file_count * rate_train
valid_testt_bound_index = total_file_count * (rate_train + rate_valid)
# print(train_valid_bound_index, valid_testt_bound_index)

json_file_count = 0
for file_name in os.listdir(folder_input):
    if not file_name.endswith("json"):
        continue
    file_name_uuid = file_name.split(".")[0]
    file_name_png = f"{file_name_uuid}.png"
    file_name_txt = f"{file_name_uuid}.txt"

    path_file_name_png = os.path.join(folder_input, file_name_png)
    path_file_name_txt = os.path.join(folder_input, file_name_txt)

    json_file_count += 1
    if json_file_count > valid_testt_bound_index:
        png_copy_to_folder = folder_output_testt_images
        txt_copy_to_folder = folder_output_testt_labels
    elif train_valid_bound_index < json_file_count <= valid_testt_bound_index:
        png_copy_to_folder = folder_output_valid_images
        txt_copy_to_folder = folder_output_valid_labels
    else:
        png_copy_to_folder = folder_output_train_images
        txt_copy_to_folder = folder_output_train_labels

    shutil.copy2(path_file_name_png, png_copy_to_folder)
    shutil.copy2(path_file_name_txt, txt_copy_to_folder)

    if json_file_count % 10000 == 0:
        print(json_file_count, path_file_name_png, png_copy_to_folder)
        print(json_file_count, path_file_name_txt, txt_copy_to_folder)
