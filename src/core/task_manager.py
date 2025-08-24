from db import mainDB
from core.base_create_config import CreateConfig
from src.augmentations.transformations import Resize, ElementGrouper, BackgroundReplase
import shutil
from pathlib import Path


class TaskManager:
    
    def __init__(self, name) -> None:
        self.name = name
        self.db = mainDB.DBManager(name)
        self.config_master = CreateConfig(name)
        self.transformation_class = {"Resize": Resize, "ElementGrouper": ElementGrouper, "BackgroundReplase": BackgroundReplase}
        self.path_directory = self.config_master.get_path()
        
        # выгрузка из бд
        self.transformations_list = [] # список активных трансформаций
        self.full_data_config = None # словарь параметров трансформаций
        self.main_settings = None # общие настройки таска
    
    def dellete_task(self):
        for dir_path in self.path_directory:
            try:
                shutil.rmtree(dir_path)  # Удаляет всё внутри
                print(f"Директория {dir_path} и её содержимое удалены")
            except FileNotFoundError:
                print("Директория не существует")
            except Exception as e:
                print(f"Ошибка: {e}")
        shutil.rmtree(self.config_master.path_dataset)
        
    
    def save_parametr(self, full_data):
        if self.db.append_settings(full_data):
            print("сохранение таска успешно")
            return True
        else:
            print("Есть проблемы")
            return False
    
    def set_base_parametr(self):
        self.full_data_config = self.config_master.create_base_parametr()
        if self.save_parametr(self.full_data_config):
            return True
        return False
    
    def set_custom_parametr(self, data):
        if self.save_parametr(self.full_data_config):
            return True
        return False
    
    def get_param(self):
        self.load_param()
        print("Загрузка параметров прошла успешно")
        if self.full_data_config:
            return self.full_data_config
    
    def load_param(self):
        print("Загрузка параметров началась")
        result = self.db.get_parametr(self.name)
        print("--------", result)
        if result:
            self.main_settings = result["main_settings"]
            self.transformations_list = result["transformation_list"]
            self.ui_element = result["ui_element"]
            self.full_data_config = result

    def start_transform(self):
        for func in self.transformations_list:
            if self.transformation_class.get(func):
                process = self.transformation_class[func]()
                
                process.import_config()



if __name__ == "__main__":
    ww = TaskManager("wwwwwww")
    ww.set_base_parametr()
    sss = TaskManager("ssss")
    sss.full_data_config = ww.__class__.__dict__["full_data_config"]
    ssspath_directory = ww.__class__.__dict__["path_directory"]
    
    