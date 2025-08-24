
import string
import numpy as np
import asyncio
from itertools import chain
from pathlib import Path
from PIL import Image, ImageDraw
from augmentations.utils.loger_config import Logger, LoadingBar
from pathlib import Path
from typing import Optional, Iterator, Any
from random import choice
from abc import abstractmethod
from augmentations.utils.descriptors import ConfigDescriptor



class TwoList:

    def __init__(self,key: str, value: Any)->None:
        self.task_name: Any = key
        self.task_config: str = value
        self.previous_example: Optional['TwoList'] = None
        self.next_example: Optional['TwoList'] = None
    

class StackManager:
    
    def __init__(self)->None:
        self.first_element: Optional[TwoList] = None
        self.last_element: Optional[TwoList] = None
        self.len_list: int = 0
        
    def append_task_left(self, task_name, task_config):
        new_node = TwoList(task_name, task_config)
        if not self.first_element:
            self.first_element = new_node
            self.last_element = self.first_element
            self.len_list += 1
        else:
            new_node.next_example = self.first_element
            self.first_element.previous_example = new_node
            self.first_element = new_node
            self.len_list += 1
    
    def iterator_stack(self) -> Iterator[tuple]:
        current_node = self.last_element
        while current_node is not None:
            yield (current_node.task_name, current_node.task_config)
            current_node = current_node.previous_example
    
    def __len__(self):
        return self.len_list

        
    
class Augmentations:
    data_param = ConfigDescriptor()
    
    def __init__(self, name_subclass) -> None:
        
        self.name_subclass = name_subclass
        log_class = Logger()
        self.logger = log_class.get_logger()
        self.iteration_util = LoadingBar()
        self._dynamic_attrs: dict[str, Any] = {}
        self.stack_manager = StackManager()
        self.all_task = []
    
    def import_config(self, data):
        try:
            self.data_param = data
        except ValueError as e:
            self.logger.error(e)
        finally:
            return False
    
    def create_stack_task(self):
        for ts in self.all_task:
            if ts in self._dynamic_attrs:
                if self._dynamic_attrs[ts] is not None:
                    task_name, task_config = ts, self._dynamic_attrs[ts]
                    self.stack_manager.append_task_left(task_name, task_config)
                    self.logger.info(f"задача {task_name} добавлена в стек")
        
    def run(self):
        self.create_element_data()
        self.create_stack_task()
        self.logger.info(f"запущен run method")
        for value in self.process_get_file():
            self.logger.info(f"Получены набор данных {value}")
            for task_data in self.stack_manager.iterator_stack():
                self.logger.info(f"Таск подъехал {task_data}")
                self.processor(task_data, value)
    
    def processor(self, task_data, value):
        """Распаковывает имя метода и вызывает его передавая параметры"""
        task_name, task_config = task_data
        method = f"{task_name}_mode"
        self.logger.info(f"Processor is start name method: {method}")
        if hasattr(self, method):
            self.logger.info(f" метод {method} обнаружен, {task_config}")
            getattr(self, method)(task_config, value)
        else:
            self.logger.warning(f" Не найден метод -- {method} --")
    
    def process_get_file(self):
        """Итерируется по генератору и открывает полученные пути с данными"""
        for t_val in self.get_couple():
            path_img, path_txt = t_val
            img = self.open_image_path(path_img)
            coords_class = self.open_txt_path(path_txt)
            yield (img, coords_class)
    
    def process_set_file(self, resurse):
        image, coords = resurse
        """Процесс сохрания данных"""
        name = self.random_name_file()
        self.save_output_image(image, name)
        self.save_output_txt(coords, name)
    
    def unpacking_parametr(self, task_data):
        """Распаковка параметров для изменения размера
           с учетом обратного ресайза если указано в resize_mode
        """
        start = int(task_data["start"] * 10)
        stop = int(task_data["stop"] * 10)
        step = int(task_data["step"] * 10)  
        return start, stop, step
    
    def change_coords(self, coords_class: list[list[int]], factor: float, part: str) -> list[list[int]]:
        """Изменяет координаты с учетом масштабирования и части изображения."""
        new_coords = []
        for coords in coords_class:
            cl, x, y, w, h = coords  # предполагается, что координаты имеют 5 элементов
            if part == "all":
                x, y, w, h = int(x * factor), int(y * factor), int(w * factor), int(h * factor)
            elif part == "width":
                x, w = int(x * factor), int(w * factor)
            elif part == "height":
                y, h = int(y * factor), int(h * factor)
            new_coords.append([cl, x, y, w, h])
        return new_coords
    
    def change_img(self, image, factor, part):
        width, height = image.size
        new_image = None
        if part == "all":
            new_image = image.resize((int(width * factor), int(height * factor)))
        elif part == "width":
            new_image = image.resize((int(width * factor), height))
        elif part == "height":
            new_image = image.resize((width, int(height * factor)))
        else:
            raise ValueError(f"part value is not correct {part}")
        return new_image
    
    def recursive_create_element(self, item):
        for name, value in item.items():
            if isinstance(value, dict) and any(isinstance(v,dict) for k, v in value.items()):
                self.recursive_create_element(value)
            else:
                self._dynamic_attrs[name] = value
            
    def create_element_data(self):
        try:
            if self.data_param is None:
                raise ValueError(f"Конфиг для подкласса небыл передан -- {self.name_subclass} --")
            for name, value in self.data_param.items(): # type: ignore
                if isinstance(value, dict):
                    self.recursive_create_element(value)
                else:
                    self._dynamic_attrs[name] = value
        except ValueError as e:
            self.logger.error(e)
            raise
        else:
             self.logger.info(f"создан набор переменных {self._dynamic_attrs}")
    
    def random_name_file(self, length=16):
        chars = string.ascii_letters + string.digits
        return ''.join(choice(chars) for _ in range(length))
    
    def create_background(self, size_image: dict, list_background: dict) -> Iterator[Image.Image]:
        """Генератор фоновых изображений из путей или цветов.
        
        Args:
            size_image: Словарь с размерами {'width': int, 'height': int}
            list_background: Словарь с параметрами фона:
                - path_background: Path к директории с изображениями (опционально)
                - color_list: Список цветов в формате RGB (опционально)
        
        Yields:
            Image.Image: Сгенерированные фоновые изображения
        
        Raises:
            ValueError: Если ни один тип фона не указан
        """
        
        self.logger.info(f"Background list -- {list_background} --")
        
        has_paths = 'path_background' in list_background and list_background['path_background'] is not None
        has_colors = 'color_list' in list_background and list_background['color_list'] is not None
        
        if not has_paths and not has_colors:
            raise ValueError("Должен быть указан хотя бы один тип фона (path_background или color_list)")
        
        # Обработка изображений-фонов
        if has_paths:
            for img_path in list_background['path_background'].glob("*"):
                if img_path.is_file():  # Проверка, что это файл
                    try:
                        yield self.open_image_path(img_path)
                    except Exception as e:
                        self.logger.warning(f"Не удалось открыть {img_path}: {e}")
        
        # Обработка цветных фонов
        if has_colors:
            for color in list_background['color_list']:
                try:
                    yield Image.new("RGB", (size_image["width"], size_image["height"]), color=color)
                except Exception as e:
                    self.logger.warning(f"Не удалось создать фон с цветом {color}: {e}")
    
    def get_couple(self):
        """Итерируется по директории и возвращает изображение и файл с его координатами"""
        input_path_image = self._dynamic_attrs["input_path_img"]
        input_path_txt = self._dynamic_attrs["input_path_txt"]
        for img in input_path_image.glob("*"):
            path_txt = Path(f"{input_path_txt}/{img.stem}.txt")
            yield (img, path_txt)
    
    def open_image_path(self, input_path):
        image = Image.open(Path(input_path))
        return image
    
    def open_txt_path(self, input_path):
        all_coords = []
        with open(input_path, "r") as file:
            for line in file:
                parts = line.strip().split(", ")
                try:
                    coords = list(map(int, parts))
                    all_coords.append(coords)
                except ValueError as e:
                    self.logger.warning(f"Ошибка при парсинге строки: {line}. Ошибка: {e}")
        return all_coords
    
    def save_output_image(self, image, name):
        output_path = self._dynamic_attrs["output_path_img"]
        image.save(f'{output_path}/{name}.png')
    
    def save_output_txt(self, coords, name):
        output_path = self._dynamic_attrs["output_path_txt"]
        self.logger.info(f"Coords == {coords}")
        with open(f'{output_path}/{name}.txt', "w") as file:
                for lst in coords:
                    file.write(f"{lst[0]}, {lst[1]}, {lst[2]}, {lst[3]}, {lst[4]}" + "\n")
                
    def image_draw_rectangle(self, image, coords):
        draw = ImageDraw.Draw(image)
        draw.rectangle(coords, outline="mediumblue", width=3)
        return image
        
        
class Resize(Augmentations):
    """
    Class resize image (jpg, jpeg, png)
            PARAMETR in self class
            
    --- _dynamic_attrs{
                 data_param: input config class
                 stack_manager: link example two_list StackManager
                 input_path_img: input path image folder
                 output_path_img: output path image folder
                 input_path_txt: input path txt folder
                 output_path_txt: output path txt folder
                 compress: dict parametr compressing mode
                 decompress: dict parametr decompressing mode
                 resize: dict parametr resize mode
                 } ---
    """
    
    def __init__(self):
        super().__init__(self.__class__.__name__)

        self.all_task = ["squeeze", "stretch", "reduce", "increase"]
    
    def _only_mode(self, image, coords, factor, part):
        factor = factor / 10
        new_image = self.change_img(image, factor, part)
        new_coords = self.change_coords(coords, factor, part)
        self.process_set_file((new_image, new_coords))
    
    def _double_mode(self, image, coords, factor):
        n_part = ["width", "height"]
        for i in n_part:
            new_image = self.change_img(image, factor, i)
            new_coords = self.change_coords(coords, factor, i)
            self.process_set_file((new_image, new_coords))
    
    def reduce_mode(self, task_data, value):
        """Метод уменьшения"""
        image, coords = value
        part = "all"
        start, stop, step = self.unpacking_parametr(task_data)
        for factor in range(stop, start + 1, step):
            self._only_mode(image, coords, factor, part)

    def increase_mode(self, task_data, value):
        """Метод увеличения"""
        image, coords = value
        start, stop, step = self.unpacking_parametr(task_data)
        part = "all"
        for factor in range(start, stop, step):
            self._only_mode(image, coords, factor, part)
            
    def squeeze_mode(self, task_data, value):
        """Сжатие"""
        image, coords = value
        start, stop, step = self.unpacking_parametr(task_data)
        part = task_data["part"]
        for factor in range(stop, start, step):
            factor = factor / 10
            if part == "all":
                self._double_mode(image, coords, factor)
            else:
                self._only_mode(image, coords, factor, part)
                
    def stretch_mode(self, task_data, value):
        """Расжатие"""
        image, coords = value
        start, stop, step = self.unpacking_parametr(task_data)
        part = task_data["part"]
        for factor in range(start, stop, step):
            factor = factor / 10
            if part == "all":
                self._double_mode(image, coords, factor)
            else:
                self._only_mode(image, coords, factor, part)
        
        
class ElementGrouper(Augmentations):
    
    def __init__(self):
        super().__init__(self.__class__.__name__)

        self.all_task = ["group_only", "group_all"]
        self.coords_x = []
        self.coords_y = []
        self.set_coords = []
            
    def append_coords(self, size_pole, box_element):
        widht_pole, height_pole = size_pole
        widht_elem, height_elem = box_element
        self.coords_x = list(range(5, widht_pole - widht_elem - 5))
        self.coords_y = list(range(5, height_pole - height_elem - 5))
        
    def set_coords_set(self, x, y, box_element):
        new_rect = (
            x - 2, 
            y - 2, 
            x + box_element[0] + 2, 
            y + box_element[1] + 2
        )
        # Проверка со всеми существующими прямоугольниками
        for existing in self.set_coords:
            # Если НЕ выполняется условие НЕпересечения
            if not (new_rect[2] < existing[0] or  # new_right < existing_left
                    existing[2] < new_rect[0] or  # existing_right < new_left
                    new_rect[3] < existing[1] or  # new_bottom < existing_top
                    existing[3] < new_rect[1]):   # existing_bottom < new_top
                return False
        # Если пересечений нет - добавляем
        self.set_coords.append(new_rect)
        return True
        
    def generation_coords(self, box_element):
        x = None
        y = None
        while True:
            nx = choice(self.coords_x)
            ny = choice(self.coords_y)
            if self.set_coords_set(nx, ny, box_element):
                x = nx
                y = ny
                return x, y
            else:
                continue
            
    def density_count(self, size_pole, box_element):
        density = self._dynamic_attrs["density"]
        pole_width, pole_height = (size_pole)
        button_width, buttun_height = box_element
        count_width = pole_width // (button_width + 20)
        count_height = pole_height // (buttun_height + 20)
        count_element = int((count_height + count_width) * density)
        return count_element
    
    def clear_param(self):
        self.coords_x = []
        self.coords_y = []
        self.set_coords = []
    
    def group_only_mode(self,  task_data, value):
        width = height = self._dynamic_attrs["pole_size"]
        self.logger.info("Запущен task group_only_mode")
        image, coords = value
        self.logger.info(f"Coords in ----- {self.group_only_mode.__name__} ---{coords}--")
        for img in self.create_background({"width": width, "height": height}, task_data):
            new_coords_file = []
            for cs_e in coords:
                x0, x1, y1, x2, y2 = cs_e
                crop_image = image.crop((x1, y1, x1 + x2,y1 + y2))
                box_element = crop_image.size
                size_create_pole = img.size
                iterations_paste = self.density_count(size_create_pole, box_element)
                self.logger.info(f"Колличество итераций для --- density: {iterations_paste} ---")
                self.append_coords(size_create_pole, box_element)
                for it in range(iterations_paste):
                    copy_origin = img
                    random_coords = self.generation_coords(box_element)
                    self.logger.info(f"------ random_coords: {random_coords}----")
                    copy_origin.paste(crop_image, random_coords)
                    if self._dynamic_attrs["process_task"] == "test_mode":
                        x1, y1, x2, y2 = (*random_coords, *box_element)
                        img = self.image_draw_rectangle(copy_origin, (x1, y1, x2 + x1, y2 + y1))
                    new_coords_file.append([x0, *random_coords, *box_element])
            self.process_set_file((img, new_coords_file))
            self.clear_param()
            
    def group_all_mode(self,  task_data, value):
        self.logger.info("Запущен task group_all_mode")
        image, coords = value
        original_width, original_height = image.size
        pass
            
            
class BackgroundReplase(Augmentations):
    
    
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.all_task = ["replace"]
    
    def replace_mode(self, task_data, value):
        self.logger.info("Запущен task replace_mode")
        image, coords = value
        original_width, original_height = image.size
        for ty_coords in coords:
            x0 = ty_coords[0]
            x1, y1, x2, y2 = ty_coords[1:]
            crop_image = image.crop((x1, y1, x1 + x2,y1 + y2))
            for backg in self.create_background({"width": original_width, "height": original_height}, task_data):
                new_image = backg
                new_image.paste(crop_image, (x1, y1))
                new_name = self.random_name_file()
                self.process_set_file((new_image, [[x0, x1, y1, x2, y2]]))
                self.logger.info(f" {self.replace_mode.__name__} -- Create images {new_name}.png --- Create txt {new_name}.txt")



if __name__ == "__main__":
    
    data = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
        "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
        "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
        "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
        "operations": {"squeeze": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                       "stretch": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"},
                            "reduce": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                            "increase": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"}}}


    new_r = Resize()
    new_r.import_config(data)
    new_r.run()
    
    dt = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
        "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
        "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
        "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
        "process_task": "test_mode",
        "density": 0.5,
        "pole_size": 1280,
        "operations": {"replace":{ "path_background": Path(r'tests\test_Augmentations\data\input_background_site'), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}}}
                                
    new_c = BackgroundReplase()
    new_c.import_config(dt)
    new_c.run()
    
    kt = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
        "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
        "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
        "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
        "process_task": "test_mode",
        "density": 0.5,
        "pole_size": 1280,
        "operations": {"group_only":{ "path_background": Path(r'tests\test_Augmentations\data\input_background_site'), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}}}
    
    new_s = ElementGrouper()
    new_s.import_config(kt)
    new_s.run()