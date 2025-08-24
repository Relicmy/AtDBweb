from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



class Actions:
    
    def __init__(self) -> None:
        self.selenium_settings = None
        
        self.site_parametr = None
        self.route_map = None
        self.settings = None
        
    
    def set_site(self, site_parametr):
        pass
    
    def set_route(self, route_map):
        pass
    
    def set_settings(self, settings):
        pass
    
    def get_coords_ui(self):
        pass
    
    def save_screen(self):
        pass
    
    def save_txt(self):
        pass
    