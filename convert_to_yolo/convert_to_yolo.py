import json
import os
import sys
from PIL import Image
from pathlib import Path

# @start for俊德之前標記的資料
# imgDir = '/Users/wangchenwei/Documents/dataset/teco/300_img'
# jsonDir = '/Users/wangchenwei/Documents/dataset/teco/300_json'
# annotaionDir = '/Users/wangchenwei/Documents/dataset/teco/300_anno'
# @end for俊德之前標記的資料

# imgDir = '/Users/wangchenwei/Documents/dataset/teco/output/train/images'
# jsonDir = '/Users/wangchenwei/Documents/dataset/teco/output/json'
# annotaionDir = '/Users/wangchenwei/Documents/dataset/teco/output/train/labels'

imgDir = "/home/iservcloud_com/component-data-generator/data/output"
jsonDir = "/home/iservcloud_com/component-data-generator/data/output"
annotaionDir = "/home/iservcloud_com/component-data-generator/data/output"

# class_file_path='/home/iservcloud_com/component-data-generator/convert_to_yolo/1_18.txt'

os.makedirs(annotaionDir, exist_ok=True)
json_file_list = os.listdir(jsonDir)
img_file_list = os.listdir(imgDir)
# @start for俊德之前標記的資料
# classSet = 0
# @end for俊德之前標記的資料
# if class_file_path:
#    with open(class_file_path, 'r') as f:
# 讀取 JSON 檔案內容
#        classSet = json.load(f)
# else:
# classSet = ['voltage transformer', "3 position disconnector", "auxiliary earthing transformer",
#             "circuit breaker", "current transformer", "earthing switch",
#             "high speed earthing switch", "hv disconnector", "isolating link",
#             "main transformer", "reactor", "removable link",
#             "surge arrester",]
#    classSet = ["AUXILIARY/EARTHING TRANSFORMER", "CURRENT TRANSFORMER", "3 POSITION DISCONNECTOR",
#                "VOLTAGE TRANSFORMER", "ISOLATING LINK",  "HIGH SPEED EARTHING SWITCH",
#                "CIRCUIT BREAKER", "SURGE ARRESTOR", "REACTOR",
#                "HV DISCONNECTOR", "EARTHING SWITCH","MAIN TRANSFORMER"]

# find a jsonfile to make classSet
for json_file in json_file_list:
    if json_file.endswith((".txt", "png")):
        continue
    json_path = os.path.join(jsonDir, json_file)
    print(json_path)
    with open(json_path, "r") as f:
        json_dict = json.load(f)
    classSet = []
    for key, value in json_dict["components_quantity"].items():
        classSet.append(key)
    break


def find_matching_indexes(string, lst):
    for idx, item in enumerate(lst):
        if string == item:
            return idx


def convert_to_normalized_xywh(x1, y1, x2, y2, image_width, image_height):
    # Calculate width and height

    x2 = x1 + x2
    y2 = y1 + y2
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    # Normalize coordinates
    normalized_x = ((x1 + x2) / 2) / image_width
    normalized_y = ((y1 + y2) / 2) / image_height
    normalized_width = width / image_width
    normalized_height = height / image_height

    return normalized_x, normalized_y, normalized_width, normalized_height


for count_index, img_file_name in enumerate(img_file_list):
    if img_file_name.endswith(".png"):
        file_name_without_ext = os.path.splitext(img_file_name)[0]
        img_file_path = os.path.join(imgDir, img_file_name)
        img = Image.open(img_file_path)
        width, height = img.size

        json_file_path = os.path.join(jsonDir, f"{file_name_without_ext}.json")
        # 開啟 JSON 檔案
        with open(json_file_path, "r") as f:
            # 讀取 JSON 檔案內容
            data = json.load(f)
            for obj in data["components_detail"]:
                box_left_x, box_left_y, box_right_x, box_right_y = obj["position"]
                thisIdx = find_matching_indexes(obj["component_name"], classSet)
                box_left_x, box_left_y, box_right_x, box_right_y = convert_to_normalized_xywh(
                    box_left_x, box_left_y, box_right_x, box_right_y, width, height
                )
                # print(thisIdx, box_left_x, box_left_y, box_right_x, box_right_y)
                # 打開txt檔案，如果不存在則新建一個
                with open(f"{annotaionDir}/{file_name_without_ext}.txt", "a") as f:
                    # 寫入文字到檔案末尾
                    f.write(f"{thisIdx} {box_left_x} {box_left_y} {box_right_x} {box_right_y}\n")
        # 使用讀取到的資料，這裡可以根據需要進行後續處理
        if count_index % 10000 == 0:
            print(f"Done. 檔案名稱: {file_name_without_ext}")
            print("-" * 20)  # 分隔每個檔案的輸出

# for json_file_name in json_file_list:
#     if json_file_name.endswith('.json'):
#         # 設定完整的檔案路徑
#         file_path = os.path.join(jsonDir, json_file_name)
#         file_name_without_ext = os.path.splitext(json_file_name)[0]
#         # 開圖檔
#         # if file_name_without_ext.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
#         img_file_path = os.path.join(imgDir, f'{file_name_without_ext}.png')
#         img = Image.open(img_file_path)
#         width, height = img.size
#         # 開啟 JSON 檔案
#         with open(file_path, 'r') as f:
#             # 讀取 JSON 檔案內容
#             data = json.load(f)
#             for obj in data['components_detail']:
#                 box_left_x, box_left_y, box_right_x, box_right_y = obj['position']
#                 thisIdx = find_matching_indexes(obj['component_name'], classSet)
#                 box_left_x, box_left_y, box_right_x, box_right_y = convert_to_normalized_xywh(box_left_x, box_left_y, box_right_x, box_right_y, width, height)
#                 print(thisIdx, box_left_x, box_left_y, box_right_x, box_right_y)
#                 # 打開txt檔案，如果不存在則新建一個
#                 with open(f'{annotaionDir}/{file_name_without_ext}.txt', 'a') as f:
#                     # 寫入文字到檔案末尾
#                     f.write(f"{thisIdx} {box_left_x} {box_left_y} {box_right_x} {box_right_y}\n")
#         # 使用讀取到的資料，這裡可以根據需要進行後續處理
#         print(f'檔案名稱: {json_file_name}')
#         print('-' * 20)  # 分隔每個檔案的輸出

# @start for俊德之前標記的資料
# for json_file_name in json_file_list:
#     if json_file_name.endswith('.json'):
#         # 設定完整的檔案路徑
#         file_path = os.path.join(jsonDir, json_file_name)
#         file_name_without_ext = os.path.splitext(json_file_name)[0]
#         # 開圖檔
#         if file_name_without_ext.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
#             img_file_path = os.path.join(imgDir, file_name_without_ext)
#             img = Image.open(img_file_path)
#             width, height = img.size
#         # 開啟 JSON 檔案
#         with open(file_path, 'r') as f:
#             # 讀取 JSON 檔案內容
#             data = json.load(f)
#             for obj in data:
#                 box_left_x, box_left_y, box_right_x, box_right_y = data[obj]['origin']['value']
#                 box_left_x, box_left_y, box_right_x, box_right_y = convert_to_normalized_xywh(box_left_x, box_left_y, box_right_x, box_right_y, width, height)
#                 print(box_left_x, box_left_y, box_right_x, box_right_y)
#                 # 打開txt檔案，如果不存在則新建一個
#                 pure_file_name = os.path.splitext(file_name_without_ext)[0]
#                 with open(f'{annotaionDir}/{pure_file_name}.txt', 'a') as f:
#                     # 寫入文字到檔案末尾
#                     f.write(f"{classSet} {box_left_x} {box_left_y} {box_right_x} {box_right_y}\n")

#         # 使用讀取到的資料，這裡可以根據需要進行後續處理
#         print(f'檔案名稱: {json_file_name}')
#         print('-' * 20)  # 分隔每個檔案的輸出
# @end for俊德之前標記的資料
