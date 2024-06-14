# coding: utf-8

from pathlib import Path

from PIL import Image

# Path setting
_root_path = Path("./data").absolute()
_legend_data_dir_name = "legend"
_component_data_dir_name = "component"
_origin_data_dir_name = "origin"
_origin_legend_image_filename = "legend.png"
_origin_diagram_image_filename = "diagram.png"

# Image setting
_image_size = (2000, 2000)
_image_background_color = (255, 255, 255)
_rectangle_width = 5
_rectangle_color = "red"
_line_width = 2
_line_color = (0, 0, 0)
_rotate_angles = [0, 90, 180, 270]
_resize_range = (0.5, 1.5)
_rectangle_use_max = False
_component_augmentation = False
_component_name_merge = False

# Normal setting
_seed = -1
_probability_seed = -1
_normal_variate_mu = 0.0
_normal_variate_sigma = 160.0
_min_component = 10
_min_line = 5
_logger_level = "INFO"
_max_iteration = 100
_count = 100000
_paste_legend_image = False
_tend_to_repeat_component = False

# Type
ImageType = Image.Image
