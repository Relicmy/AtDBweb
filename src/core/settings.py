import json


def parametr_resize():
    source_path_img = "test_images/screenshot.png"
    output_path_img = "test_output_img"
    source_path_txt = "test_txt/screenshot.txt"
    output_path_txt = "test_output_txt"
    compress = {"start": "0.5", "step": "0.1", "stop": "1.0", "part": "all"}
    decompress = {"start": "1.0", "step": "0.1", "stop": "1.5", "part": "all"}
    resize = {"start": "1.0", "step": "0.1", "stop": "1.5", "part": "full"}
    process_task = "test_mode"
    pack_param = {"source_path_img": source_path_img, "output_path_img": output_path_img,
                  "source_path_txt": source_path_txt, "output_path_txt": output_path_txt,
                  "const_parametr": {"compress": compress,
                                     "decompress": decompress,
                                     "resize": resize},
                  "process_task": process_task
                }
    

    with open("Augmentations/param_resize.json", "w", encoding="utf-8") as file:
        json.dump(pack_param, file, indent=4)
        
def parametr_background():
    source_path_img = "Augmentations/test_images/screenshot.png"
    output_path_img = "Augmentations/test_output_background_image"
    source_path_txt = "Augmentations/test_txt/screenshot.txt"
    output_path_txt = "Augmentations/test_output_bacground_txt"
    list_background = {"path": "", "color": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}
    process_task = "test_mode"
    pack_param = {"source_path_img": source_path_img, "output_path_img": output_path_img,
                  "source_path_txt": source_path_txt, "output_path_txt": output_path_txt,
                  "list_background": list_background,
                  "process_task": process_task
                }
    with open("Augmentations/param_replase_background.json", "w", encoding="utf-8") as file:
        json.dump(pack_param, file, indent=4)
        

def parametr_group():
    source_path_img = "Augmentations/test_images/screenshot.png"
    output_path_img = "Augmentations/test_output_background_image"
    source_path_txt = "Augmentations/test_txt/screenshot.txt"
    output_path_txt = "Augmentations/test_output_bacground_txt"
    density = 50
    pole_size = 1280
    classes_group = [0]
    list_background = {"path": "", "color": ["red", "orange", "yellow", "green", "blue", "purple", "pink",
                                             "white", "black", "gray", "brown", "cyan", "magenta", "lime",
                                             "gold", "silver", "maroon", "olive", "teal", "navy"]}
    
    process_task = "test_mode"
    pack_param = {"source_path_img": source_path_img, "output_path_img": output_path_img,
                  "source_path_txt": source_path_txt, "output_path_txt": output_path_txt,
                  "list_background": list_background,
                  "process_task": process_task,
                  "density": density,
                  "pole_size": pole_size,
                  "classes_group": classes_group
                }
    with open("Augmentations/parametr_group_button.json", "w", encoding="utf-8") as file:
        json.dump(pack_param, file, indent=4)

parametr_group()