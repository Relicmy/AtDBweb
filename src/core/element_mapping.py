


class ElementUi:
    
    def __init__(self, data) -> None:
        self.class_name = data["class_name"]
        self.css_selector = data["css_selector"]
        self.text_selector = data["text_selector"]
        self.class_element = data["class_element"]
        
        
class SiteInfo:
    
    def __init__(self, data) -> None:
        self.url = data["url"]
        self.login = data["login"]
        self.password = data["password"]
        self.list_element = []
        
    def append_element(self, elem):
        for i in elem:
            self.list_element.append(i)
    
    def get_element(self):
        return self.list_element

