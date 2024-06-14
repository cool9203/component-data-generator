import os
from ultralytics import YOLO
model = YOLO("./custom_data/runs/detect/train/weights/best.pt")
#result = model.predict('test_data_cut/1_4.png', save=False, imgsz=640, conf=0.5)
#print(result[0].names)
#print('--'*30)

result_count = {}
result_page = {}
result_count_final = {}
#png_path = 'test_data_cut'
#png_path = 'cut_image/project_data_center'
#png_path = 'cut_image/project_general_electromechamin'
png_path = 'cut_image/project_wind_power'

for root, dirs, files in os.walk(png_path):
    for png_name in files:
        if not png_name.endswith('png'):
            continue
        png_file = os.path.join(root,png_name)
        result = model.predict(png_file, save=True, imgsz=640, conf=0.7)
        page_index = int(root[-1])
        #result_label_json = result[0].names
     
        for cls in result[0].boxes.cls:
            cls = int(cls)
            if cls not in result_count:
                result_count[cls] = 0
            result_count[cls] += 1
            if cls not in result_page:
                result_page[cls] = set()
            result_page[cls].add(page_index)
        #clss = [int(i) for i in result[0].boxes.cls]
        #print(result_label_json)
        #breakpoint()
for k,v in result_count.items():
    new_k = result[0].names[k].replace('.png','')
    page_index = result_page[k]
    result_count_final[new_k] = [v,page_index]
    #print(result[0].names[k],v)
print(result_count_final)
#print(result_count)
#print(result[0].names)
#breakpoint()
