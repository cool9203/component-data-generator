# component-data-generator

## 目的

自動產生電路圖與圖例的結合, 便於 VLM 利用 VQA 自動計算電路圖上的元件數量

<details>
    <summary>Table of Content</summary>

- [component-data-generator](#component-data-generator)
  - [目的](#目的)
  - [如何使用](#如何使用)
    - [component data](#component-data)
      - [一般啟動](#一般啟動)
      - [生成沒有框線的版本](#生成沒有框線的版本)
      - [會貼 legend image 與 傾向使用重複的元件](#會貼-legend-image-與-傾向使用重複的元件)
      - [使用整張底圖 + 影像增強 + 沒有框線 + 底圖大小為640\*640](#使用整張底圖--影像增強--沒有框線--底圖大小為640640)
  - [重複跑的 ubuntu 指令](#重複跑的-ubuntu-指令)
  - [prompt data](#prompt-data)
  - [test data](#test-data)
  - [pdf to image](#pdf-to-image)
  - [cut image](#cut-image)
  - [combine image](#combine-image)
</details>

## 如何使用

### component data

生成給 LLAVA 的訓練影像

#### 一般啟動

`python -m component_data_generator`

#### 生成沒有框線的版本

`python -m component_data_generator --rectangle_width 0`

#### 會貼 legend image 與 傾向使用重複的元件

`python -m component_data_generator --paste_legend_image --tend_to_repeat_component`

#### 使用整張底圖 + 影像增強 + 沒有框線 + 底圖大小為640*640

`python -m component_data_generator --rectangle_width 0 --rectangle_use_max --component_augmentation --image_size 640 640 -c 10000`


## 重複跑的 ubuntu 指令

`seq <REPEAT_TIMES> | xargs -Iz <COMMAND>`

Reference: <https://askubuntu.com/a/523279>

---

## prompt data

生成給 LLAVA 的訓練 prompt

`python -m component_data_generator.generate_prompt -t <YOUR_TARGET_PATH>`

---

## test data

當前不支援 argparse

生成給 LLAVA 的測試資料

`python -m component_data_generator.generate_test_data`

---

## pdf to image

`python component_data_generator/convert_pdf_to_png.py -p <YOUR_PDF_PATH> -o <OUTPUT_DIR> [-d <DPI>]`

---

## cut image

`python component_data_generator/cut_image.py -i <YOUR_IMAGE_PATH_OR_DIR> -o <OUTPUT_DIR> [-s <CUT_IMAGE_SIZE>]`

---

## combine image

`python component_data_generator/combine_image.py -i <YOUR_IMAGE_FOLDER> -o <OUTPUT_FILENAME>`
