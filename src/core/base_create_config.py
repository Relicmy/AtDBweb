from pathlib import Path


class CreateConfig:
    def __init__(self, name_task) -> None:
        self.name_task = name_task
        self.main_settings = None
        self.path_config = None
        self.element_ui = None
        self.selenium_settings = None
        self.resize_param = None
        self.background_replase_param = None
        self.element_group_param = None
        
        self.dir_datasets = Path("datasets")
        self.dir_input = Path("data/input")
        self.dir_output = Path("data/output")
        self.creater_file = ["img", "coords", "element", "background_image"]
        self.list_investment_set = ["train", "val", "test"]
        self.create_file_dataset = {"images": self.list_investment_set, "labels": self.list_investment_set}
        self.path_dataset = Path(self.dir_datasets / self.name_task)
        self.path_input = Path(self.dir_input / self.name_task)
        self.path_output = Path(self.dir_output / self.name_task)
        self.path_bg = Path(self.path_input / self.name_task)
        self.create_input_directory()
    
    def get_path(self):
        path_in_out = {"source_path_img": self.path_input,
                       "output_path_img": self.path_output,
                       "source_path_txt": self.path_input,
                       "output_path_txt": self.path_output,
                       "dataset_folder": self.path_dataset}
        
        return path_in_out
    
    def create_input_directory(self):
        if self.name_task:
            if Path(self.dir_input).exists() and Path(self.dir_output).exists():
                for folder in self.creater_file:
                    Path(self.dir_input / self.name_task / folder).mkdir(parents=True, exist_ok=True)
                    Path(self.dir_output / self.name_task / folder).mkdir(parents=True, exist_ok=True)
            Path(self.dir_input / self.name_task / "background_image").mkdir(parents=True, exist_ok=True)
            if Path(self.dir_datasets).exists():
                for file in self.create_file_dataset:
                    for item in self.create_file_dataset[file]:
                        Path(self.dir_datasets / self.name_task / file / item).mkdir(parents=True, exist_ok=True)
                
    def create_base_parametr(self):
        full_data_config = {}
        path_in_out = {"input_path_img": Path(self.path_input / "img"),
                       "output_path_img": Path(self.path_output / "img"),
                       "input_path_txt": Path(self.path_input / "coords"),
                       "output_path_txt": Path(self.path_output / "coords")}
        
        Resize_config = {"path_in_out": path_in_out, "operations": {"squeeze": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                            "stretch": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"},
                            "reduce": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                            "increase": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"}},
                            "process_task": "test_mode"}
        
        BackgroundReplase_config = {"path_in_out": path_in_out, "operations": {"replace":{ "path_background": Path(self.path_bg / "background_image"), 
                                                              "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                                                "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                                                "gold", "silver", "maroon", "olive", "teal", "navy"]}}, "process_task": "test_mode",
                                        "density": 0.5,
                                        "pole_size": 1280}
        
        ElementGrouper_config = {"path_in_out": path_in_out, "operations": {"group_only":{ "path_background": Path(self.path_bg / "background_image"), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]},
                                                "group_all":{ "path_background": Path(self.path_bg / "background_image"), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}},
                                        "process_task": "test_mode",
                                        "density": 0.5,
                                        "pole_size": 1280}
        
        full_data_config["Name_task"] = self.name_task
        full_data_config["Resize"] =  Resize_config
        full_data_config["ElementGrouper"] =  ElementGrouper_config
        full_data_config["BackgroundReplase"] =  BackgroundReplase_config
        
        return full_data_config
    
    
if __name__ == "__main__":
    test_class = CreateConfig("SurfEarner")
    