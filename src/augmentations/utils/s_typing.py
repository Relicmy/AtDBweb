from pydantic import BaseModel, ValidationError, field_validator, ConfigDict, model_validator
from dataclasses import make_dataclass, field
from typing import Optional, ClassVar, Literal, Any, Union
from pathlib import Path
from augmentations.utils.default_parametr import color_group
from collections.abc import Mapping

#------------------ Path_in_out------------------
class iNOUT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    input_path_img: Optional[Path] = None
    output_path_img: Optional[Path] = None
    input_path_txt: Optional[Path] = None
    output_path_txt: Optional[Path] = None

#----------------- Operations --------------------
class ReduceParametr(BaseModel):
    """ reduce ---- """
    model_config = ConfigDict(extra="forbid")
    
    start: float
    step: float
    stop: float
    part: Optional[Literal["all"]] = None
    
    
    @model_validator(mode='after')
    def check_at_least_one(self):
        if not self.part is None:
            if not 0.9 >= self.start >= 0.6:
                raise ValueError(f"Param start not validate -- 0.9 >= {self.start} >= 0.6")
            if not 0.1 <= self.step <= 0.2:
                raise ValueError(f"Param step not validate -- 0.1 <= {self.start} <= 0.2")
            if not 0.8 >= self.stop >= 0.5:
                raise ValueError(f"Param stop not validate -- 1.0 <= {self.start} <= 1.6")
            if self.stop >= self.start:
                raise ValueError(f"Param not correct -- stop: {self.stop} >= start: {self.start} --")
            if not int((self.stop * 10) % (self.step * 10)) == 0:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} -- step: {self.step} --  not % == 0 -- ")
        return self  

class IncreaseParametr(BaseModel):
    """increase ++++"""
    model_config = ConfigDict(extra="forbid")
    
    start: float
    step: float
    stop: float
    part: Optional[Literal["all"]] = None
    
    
    @model_validator(mode='after')
    def check_at_least_one(self):
        if not self.part is None:
            if not 1.1 <= self.start <= 1.4:
                raise ValueError(f"Param start not validate -- 1.1 <= {self.start} <= 1.4")
            if not 0.1 <= self.step <= 0.2:
                raise ValueError(f"Param step not validate -- 0.1 <= {self.start} <= 0.2")
            if not 1.2 <= self.stop <= 1.6:
                raise ValueError(f"Param stop not validate -- 1.2 <= {self.start} <= 1.6")
            if self.stop <= self.start:
                raise ValueError(f"Param not correct -- stop: {self.stop} <= start: {self.start} --")
            if not int((self.stop * 10) % (self.step * 10)) == 0:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} -- step: {self.step} --  not % == 0 -- ")
        return self   

class StretchParametr(BaseModel):
    """stretch +++ width or height or all"""
    
    model_config = ConfigDict(extra="forbid")
    
    start: float
    step: float
    stop: float
    part: Optional[Literal["width", "height", "all"]] = None
    
    
    @model_validator(mode='after')
    def check_at_least_one(self):
        if not self.part is None:
            if not 1.0 <= self.start <= 1.5:
                raise ValueError(f"Param start not validate -- 1.0 <= {self.start} <= 1.5")
            if not 0.1 <= self.step <= 0.2:
                raise ValueError(f"Param step not validate -- 0.1 <= {self.start} <= 0.2")
            if not 1.1 <= self.stop <= 1.6:
                raise ValueError(f"Param stop not validate -- 1.1 <= {self.start} <= 1.6")
            if not int((self.stop * 10) % (self.step * 10)) == 0:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} -- step: {self.step} --  not % == 0 -- ")
            if self.stop <= self.start:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} not < start: {self.start} -- ")
        return self

class SqueezeParametr(BaseModel):
    """squeeze --- width or height or all"""
    model_config = ConfigDict(extra="forbid")
    
    start: float
    step: float
    stop: float
    part: Optional[Literal["width", "height", "all"]] = None
    
    @model_validator(mode='after')
    def check_at_least_one(self):
        if not not self.part is None:
            if not 1.0 >= self.start >= 0.5:
                raise ValueError(f"Param start not validate -- 1.0 <= {self.start} <= 0.5")
            if not 0.1 <= self.step <= 0.2:
                raise ValueError(f"Param step not validate -- 0.1 <= {self.start} <= 0.2")
            if not 0.6 <= self.stop <= 1.0:
                raise ValueError(f"Param stop not validate -- 0.6 <= {self.start} <= 1.0")
            if not int((self.stop * 10) % (self.step * 10)) == 0:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} -- step: {self.step} --  not % == 0 -- ")
            if self.stop >= self.start:
                raise ValueError(f"Not correct parameters -- stop: {self.stop} not > start: {self.start} -- ")
        return self

class OperationsTransorm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    # squeeze: Union[dict, SqueezeParametr, None] = None
    # stretch: Union[dict, StretchParametr, None] = None
    # reduce: Union[dict, ReduceParametr, None] = None
    # increase: Union[dict, IncreaseParametr, None] = None
    
    squeeze: SqueezeParametr
    stretch: StretchParametr
    reduce: ReduceParametr
    increase: IncreaseParametr
    
    @model_validator(mode="after")
    def validation_param(self):
        if not any(var is not None for var in [self.squeeze, self.stretch, self.reduce, self.increase]):
            raise ValueError(f" All value Operations is None!!!")
        return self
    
# ------------background transform -------

class PoleSize(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pole_size: int
    
    @field_validator("pole_size")
    @classmethod
    def size_validator(cls, pz: int) -> int:
        if not pz:
            return pz
        if not isinstance(pz, int):
            raise ValueError(f"pole_size is not type(int) -- {pz} --")
        if not 320 <= pz <= 2000:
            raise ValueError(f"pole_size is not validate 320 <= {pz} <= 2000")
        return pz

class DensityNumber(BaseModel):
    model_config = ConfigDict(extra="forbid")
    density: float
    
    @field_validator('density')
    @classmethod
    def _check_density(cls, dn: float)->float:
        if dn is None:
            return dn
        cls.density_validate(dn)
        return dn
    
    @classmethod
    def density_validate(cls, dn: float)->float:
        if not 0.1 < dn < 0.8:
            raise ValueError(f"Density is not 0.1 < {dn} < 0.8")
        return dn

class ListBackground(BaseModel):
    
    model_config = ConfigDict(extra="forbid")
    
    path_background: Optional[Path] = None
    color_list: Optional[list[str]] = None
    #suffix_file: ClassVar[list] = [".jpeg", ".png", ".jpg"]
    
    @model_validator(mode='after')
    def check_at_least_one(self):
        if self.path_background is None and self.color_list is None:
            raise ValueError("At least one of 'path_font' or 'color_list' must be provided")
        return self
    
    @field_validator('color_list')
    @classmethod
    def validate_colors(cls, cl: list[str] | None) -> list[str] | None:
        if cl is None:
            return cl
        return [cls.validate_single_color(color) for color in cl]
    
    @classmethod
    def validate_single_color(cls, color_str: str) -> str:
        list_color_group = color_group()
        if not list_color_group:
            raise ValueError(f" There is no color_group list ")
        if color_str not in list_color_group:
            raise ValueError(f"Invalid color: {color_str}. Must be one of {list_color_group}")
        return color_str

class OperationsBackground(BaseModel):
    model_config = ConfigDict(extra="forbid")
    replace: ListBackground
    
class OperationsElementGrouper(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group_only: ListBackground
    group_all: ListBackground
# ---------Globals abs class ------------

class ValidateResize(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    path_in_out: iNOUT
    process_task: Literal["test_mode", "production_mode"] = "test_mode"
    operations: OperationsTransorm
    
    
class ValidateElementGrouper(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    path_in_out: iNOUT
    process_task: Literal["test_mode", "production_mode"] = "test_mode"
    operations: OperationsElementGrouper
    density: float
    pole_size: int
    
    @field_validator('density')
    @classmethod
    def _check_density(cls, dn: float) -> float:
        if not 0.1 < dn < 0.8:
            raise ValueError(f"Density must be 0.1 < {dn} < 0.8")
        return dn


class ValidateBackgroundReplase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    path_in_out: iNOUT
    process_task: Literal["test_mode", "production_mode"] = "test_mode"
    operations: OperationsBackground
    density: float
    pole_size: int
    
    @field_validator('density')
    @classmethod
    def _check_density(cls, dn: float) -> float:
        if not 0.1 < dn < 0.8:
            raise ValueError(f"Density must be 0.1 < {dn} < 0.8")
        return dn
    
    
if __name__ == "__main__":
    
    
    class TestigClass:
        
        def __init__(self, data: dict) -> None:
            self.config = data
    
    
    dic1 = {"operations": {"squeeze": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                              "stretch": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"},
                              "reduce": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                              "increase": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"}}}
    
    dic2 = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
            "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
            "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
            "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},
            "operations": {"squeeze": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                              "stretch": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"},
                              "reduce": {"start": 0.9,"step": 0.1,"stop": 0.6,"part": "all"},
                              "increase": {"start": 1.1,"step": 0.1,"stop": 1.6,"part": "all"}}}
    
    data2 = {"path_in_out": {"input_path_img": Path(r"tests\test_Augmentations\data\test_images"),
    "output_path_img": Path(r"tests\test_Augmentations\data\output_images"),
    "input_path_txt": Path(r"tests\test_Augmentations\data\test_txt"),
    "output_path_txt": Path(r"tests\test_Augmentations\data\output_txt")},"operations": {"replace":{ "path_background": Path(r"tests\test_Augmentations\data\output_images"), "color_list": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                            "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                            "gold", "silver", "maroon", "olive", "teal", "navy"]}},
                                    "process_task": "test_mode",
                                    "density": 0.5,
                                    "pole_size": 1280}

    try:
        ValidateBackgroundReplase(**data2) # type: ignore

        new_clss1 = TestigClass(dic1)
        print(True)
        
    except ValidationError as e:
        print(e)
        
    
    # try:
       
    #     ValidateResize(**dic2)
    #     print(True)
    # except ValidationError as e:
    #     print(e)