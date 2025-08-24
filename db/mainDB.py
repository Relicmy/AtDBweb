import sqlite3
from augmentations.utils.s_typing import ValidateBackgroundReplase, ValidateResize, ValidateElementGrouper
from augmentations.utils.loger_config import Logger
from typing import Optional, Union
from augmentations.utils.descriptors import ConfigDescriptor
from pydantic import ValidationError
import json
from pathlib import Path



class TestingParametr:
    
    def __init__(self) -> None:
        log_class = Logger()
        self.logger = log_class.get_logger()
    
    def validate_background(self, data):
        print(data)
        if data is None:
            return None
        try:
            ValidateBackgroundReplase(**data)
            return True
        except ValidationError as e:
            print(e)
            return False

    def validate_resize(self, data):   
        if data is None:
            return None
        try:
            ValidateResize(**data)
            return True
        except ValidationError as e:
            print(e)
            return False
    
    def validate_element_group(self, data):
        if data is None:
            return None
        try:
            ValidateElementGrouper(**data)
            return True
            
        except ValidationError as e:
            print(e)
            return False

    def validate(self, data) -> Union[bool, tuple, None]:
        dc_active = {
            "bg_replase": self.validate_background(data.get("BackgroundReplase")),
            "bg_grouper": self.validate_element_group(data.get("ElementGrouper")),
            "bg_resize": self.validate_resize(data.get("Resize"))
        }
        
        for name, result in dc_active.items():
            if not result:
                self.logger.error(f"Validation failed for {name}: {result}")
                return False
            self.logger.debug(f"Validation passed for {name}")
        return True

        
class DBCreate:
    _instance: Optional['DBCreate'] = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_name: str = "db/main_data.db"):
        if not self._initialized:
            self.db_name = db_name
            self.conn = None
            self._create_tables()
            self._initialized = True
            self._closed = True
    
    def _create_tables(self):
        try:
            cursor = self.get_cursor()
            if self.conn is not None:
                with self.conn:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS config (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Name_task TEXT NOT NULL UNIQUE,
                            main_settings TEXT,
                            ui_element TEXT,
                            BackgroundReplase TEXT,
                            ElementGrouper TEXT,
                            Resize TEXT,
                            transformation_list TEXT
                        )
                    ''')
            self.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    def get_cursor(self) -> sqlite3.Cursor:
        """Получение курсора для выполнения запросов"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
            self._closed = False
        return self.conn.cursor()
    
    def close(self):
        if hasattr(self, 'conn') and self.conn and not self._closed:
            self.conn.commit()
            self.conn.close()
            self._closed = True
            self.conn = None
    
    def __del__(self):
        self.close()
    
    
class DBManager:
    
    db = DBCreate()
    list_transformation = ["Resize", "ElementGrouper", "BackgroundReplase"]
    
    def __init__(self, name_task) -> None:
        self.name = name_task
        self.test_parametr = TestingParametr()
    
    def validate_parametr(self, data):
        
        if self.test_parametr.validate(data) is True:
            return True
        else:
            return False
        

    def serialized_data(self, data_item, name_item):
        if data_item.get("path_in_out"):
            data_item["path_in_out"] = {key: value if isinstance(value, str) else str(value)
                                        for key, value in data_item["path_in_out"].items()}
        if name_item in self.list_transformation[1:]:
            if data_item.get("operations"):
                for i in data_item["operations"]:
                    data_item["operations"][i]["path_background"] = str(data_item["operations"][i]["path_background"])
        return data_item
    
    def unserialized_data(self, data_item, name_item):
        if data_item.get("path_in_out"):
            data_item["path_in_out"] = {key: Path(value)
                                        for key, value in data_item["path_in_out"].items()}
        if name_item in self.list_transformation[1:]:
            if data_item.get("operations"):
                for i in data_item["operations"]:
                    data_item["operations"][i]["path_background"] = Path(data_item["operations"][i]["path_background"])   
        return data_item
    
    def append_settings(self, data):
        if self.validate_parametr(data):
            for item in self.list_transformation:
                if data.get(item):
                    data[item] = self.serialized_data(data[item], item)
            js_data = {
                key: value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
                for key, value in data.items()
            }   
            
        
            columns = ', '.join(js_data.keys())
            placeholders = ', '.join(['?'] * len(js_data))
            
            cursor = self.db.get_cursor()
            
            sql = f"""
                    INSERT OR REPLACE INTO config 
                    ({columns}) 
                    VALUES ({placeholders})
                    """
            
            cursor.execute(sql, tuple(js_data.values()))
            self.db.close()
            return True
        return False 
    
    def get_parametr(self, name_task):
            """Получает ВСЕ данные задачи по её имени.
            Возвращает словарь с распарсенными JSON-данными из каждого поля.
            """
            query = """
            SELECT 
                Name_task, 
                main_settings, 
                ui_element, 
                BackgroundReplase, 
                ElementGrouper, 
                Resize, 
                transformation_list 
            FROM config
            WHERE Name_task = ?
            """
            cursor = self.db.get_cursor()
            cursor.execute(query, (name_task,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"Задача '{name_task}' не найдена в БД")
            
            parse_result = {
                "Name_task": result[0],
                "main_settings": json.loads(result[1]) if result[1] else None,
                "ui_element": json.loads(result[2]) if result[2] else None,
                "BackgroundReplase": json.loads(result[3]) if result[3] else None,
                "ElementGrouper": json.loads(result[4]) if result[4] else None,
                "Resize": json.loads(result[5]) if result[5] else None,
                "transformation_list": json.loads(result[6]) if result[6] else []
            }
            validate_parametr = {"BackgroundReplase": parse_result["BackgroundReplase"],
                                 "ElementGrouper": parse_result["ElementGrouper"],
                                 "Resize": parse_result["Resize"]}
            
            for item in self.list_transformation:
                if validate_parametr.get(item):
                    validate_parametr[item] = self.unserialized_data(validate_parametr[item], item)
            for key, value in validate_parametr.items():
                parse_result[key] = value
            if self.validate_parametr(validate_parametr):
                return parse_result
        
        
if __name__ == "__main__":
    new_db = DBCreate()
            