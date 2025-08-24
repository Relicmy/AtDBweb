from augmentations.utils.s_typing import ValidateBackgroundReplase, ValidateResize, ValidateElementGrouper
from pathlib import Path
from augmentations.utils.loger_config import Logger


class ConfigDescriptor:
    
    
    def __init__(self):
        logger_instance = Logger()
        self.logger = logger_instance.get_logger()
        self.name_subclass = None
        self.name = None

    def __set_name__(self, owner, name):
        print(f"DEBUG: __set_name__ вызван для {owner.__name__}.{name}")
        self.logger.info(f"Создана переменная {name} --")
        self.name = "_" + name
        
    def __get__(self, instance, owner):
        if self.name:
            return getattr(instance, self.name)
    
    def _validate_config(self, name_subclass, value):
        
        config_subclass = {"Resize": ValidateResize,
                           "BackgroundReplase": ValidateBackgroundReplase,
                           "ElementGrouper": ValidateElementGrouper}
        if not name_subclass or name_subclass not in config_subclass:
            raise ValueError(f"Дочерний класс не опознан или не назначен {name_subclass} ")
        if not value:
            raise ValueError("Данные для валидации дочернего классе не получены")
        self.logger.info(name_subclass)
        self.logger.info(f"Передано на валидацию в {config_subclass[name_subclass]}")
        config_subclass[name_subclass](**value)
        
    def __set__(self, instance, value):
        if not self.name:
            raise ValueError("Имя атрибута не установлено")
        if hasattr(instance, self.name):
            return
        try:
            self.name_subclass = f"{instance.__class__.__name__}"
            self._validate_config(self.name_subclass, value)
            instance.__dict__[self.name] = value  # сохраняем напрямую в __dict__
            self.logger.info(f"Установлен {self.name} = {value}")
        except Exception as e:
            self.logger.error(e)
            
        

if __name__ == "__main__":
    
    
    class Resize:
        data = ConfigDescriptor()
        
        def __init__(self, data) -> None:
            self.data = data
    
    class BackgroundReplase:
        data = ConfigDescriptor()
        
        def __init__(self, data) -> None:
            self.data = data
       
    class ElementGrouper:
        data = ConfigDescriptor()
        
        def __init__(self, data) -> None:
            self.data = data
    
    
    data = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
        "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
        "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
        "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
        "operations": {"squeeze": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                            "stretch": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"},
                            "reduce": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                            "increase": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"}}}
    
    data1 = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
                            "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
                            "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
                            "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
             "operations": {"path_background": "", "color_list": ["red","orange","yellow","green","blue","purple",
                                                                                    "pink","white","black","gray","brown","cyan","magenta","lime",
                                                                                    "gold","silver","maroon","olive","teal","navy"]},
            "process_task": "test_mode", "density": 0.5, "pole_size": 1280}
    data2 = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
        "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
        "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
        "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},"operations": {"group_only":{ "path_background": Path(r"tests\test_Augmentations\data\output_images"), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]},
                                                "group_all":{ "path_background": Path(r"tests\test_Augmentations\data\output_images"), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}},
                                        "process_task": "test_mode",
                                        "density": 0.5,
                                        "pole_size": 1280}
    
    
    new_c = BackgroundReplase(data2)
    print(new_c.data)