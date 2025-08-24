from pathlib import Path
from augmentations.transformations import Resize
import pytest


# def test_BackgroundReplase_init():
#     """
#     Проверка на инициализацию класса и проверку переданных параметров
    
#     """
#     data = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
#             "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
#             "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
#             "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
#             "const_parametr": {"compress": {"start": 1.0,"step": 0.1,"stop": 0.7,"part": "none"},
#                               "decompress": {"start": 1.0,"step": 0.1,"stop": 1.5,"part": "none"},
#                               "resize": {"start": 1.1,"step": 0.1,"stop": 1.5,"operation": "all"}}, "process_task": "test_mode"}

#     new_c = Resize(data)
#     print(new_c.data_param)
#     new_c.run()