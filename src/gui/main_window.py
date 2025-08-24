import sys
from pydantic import ValidationError
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, Qt, QUrl, QPoint
from PySide6.QtGui import QFont
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QFrame, QApplication, QTabWidget
)
import json
from src.core.task_manager import TaskManager
from jinja2 import Template
from bs4 import BeautifulSoup


class RenderAugmentationHTML:
    
    def __init__(self, param) -> None:
        self.resize = param["Resize"]["operations"]
        self.bg_replase = param["BackgroundReplase"]["operations"]
        self.elem_group = param["ElementGrouper"]["operations"]
        
        
    
    def get_page(self):
        html_path = Path(r"src\gui\resources\_augment_settings.html")
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            return "<div>Ошибка: HTML файл не найден</div>"
        except Exception as e:
            return f"<div>Ошибка чтения файла: {str(e)}</div>"
        template = Template(html_content)
        page = template.render(resize=self.resize, bg_replase=self.bg_replase, elem_group=self.elem_group)
        return page


class TaskBridge(QObject):
    tasks_updated = Signal(list)
    
    
    def __init__(self):
        super().__init__()
        self.tasks = []
    
    @Slot(str, str, result=str)
    def update_augmentations(self, name_task, page_update):
        soup = BeautifulSoup(page_update, 'html.parser')
        return page_update
    
    @Slot(str, result=str) 
    def renderHTML(self, task_name):
        try:
            print(f"Запрос HTML для задачи: {task_name}")
            task_obj = TaskManager(task_name)
            print(task_obj)
            params = task_obj.get_param()
            print(params)
            if params:
                cl_generate = RenderAugmentationHTML(params)
                render_page = cl_generate.get_page()
                return render_page
            else:
                return "<div>Параметры задачи не найдены</div>"
        except Exception as e:
            print(f"Ошибка в renderHTML: {e}")
            return f"<div>Ошибка: {str(e)}</div>"
    
    @Slot(result=str)
    def openDirectoryDialog(self):
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(None, "Выберите папку")
        return dir_path if dir_path else ""

    @Slot(str, result=str)
    def startAugmentation(self, config_json):
        try:
            config = json.loads(config_json)
            print("Получена конфигурация аугментации:", config)
            return "success"
        except Exception as e:
            print("Ошибка обработки конфигурации:", str(e))
            return "error"
    
    @Slot(str)
    def update_task(self, task_name):
        pass
    
    @Slot(str)
    def dellTask(self, task_name):
        if task_name in self.tasks:
            deleted = TaskManager(task_name)
            deleted.dellete_task()
            self.tasks.remove(task_name)
            self._save_tasks()
            self.tasks_updated.emit(self.tasks)
            print("Задача удалена")

    @Slot(str)
    def addTask(self, task_name):
        
        new_task = TaskManager(task_name)
        if new_task.set_base_parametr():
            print(f"Добавлена задача: {task_name}")
            self.tasks.append(task_name)
            self._save_tasks()
            self.tasks_updated.emit(self.tasks)
        

    def _save_tasks(self):
        with open("tasks.txt", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f)
        
        

    def load_tasks(self):
        try:
            with open("tasks.txt", "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []

    @Slot(result=list)
    def getTasks(self):
        return self.tasks


class CustomTitleBar(QWidget):
    windowClose = Signal()
    windowMinimize = Signal()
    windowMaximizeRestore = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.drag_pos = QPoint()
        self.maximized = False

        self.setFixedHeight(40)
        self.setAutoFillBackground(True)
        self.top_bar = QWidget()
        self.title_label = QLabel("AtDBweb")
        
        self.title_label.setStyleSheet("""
                                    background-color: #2a1d35;
                                    color: white;
                                    padding-left: 10px;
                                    font-weight: bold;
                                    
                                """)
        
        self.title_label.setFont(QFont("Arial", 12))

        

        btn_size = 30

        self.btn_minimize = QPushButton()
        self.btn_close = QPushButton()
        self.btn_maximize = QPushButton()

        # ✅ Иконки или текст
        self.btn_minimize.setText("—")
        self.btn_close.setText("✕")
        self.btn_maximize.setText("□")

        # ✅ Улучшенные стили для кнопок
        for btn, name in zip(
            [self.btn_minimize, self.btn_maximize, self.btn_close],
            ["minimize", "maximize", "close"]
        ):
            btn.setObjectName(name)
            btn.setFixedSize(btn_size, btn_size)
            btn.setFont(QFont("Arial", 10))
            btn.setStyleSheet(f"""
                QPushButton#{name} {{
                    background-color: #3B0753;
                    color: white;
                    border: none;
                    font-size: 14px;
                    border-radius: 4px;
                }}
                QPushButton#{name}:hover {{
                    background-color: {"#ff1111" if name == "close" else "#C000EB"};
                    border-radius: 4px;
                }}
            """)

        self.btn_minimize.clicked.connect(self.windowMinimize)
        self.btn_close.clicked.connect(self.windowClose)
        self.btn_maximize.clicked.connect(self.toggle_maximize_restore)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(self.title_label)  # Заголовок слева
        layout.addStretch()  
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)
        layout.addSpacing(10)


    def toggle_maximize_restore(self):
        self.maximized = not self.maximized
        self.windowMaximizeRestore.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.main_window:
                self.drag_pos = event.globalPosition().toPoint() - self.main_window.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.main_window:
                self.main_window.move(event.globalPosition().toPoint() - self.drag_pos)
        event.accept()


class ResizableFrame(QFrame):
    def __init__(self, direction: Qt.Edge, parent=None):
        super().__init__(parent)
        self.direction = direction
        self.setCursor(self._get_cursor(direction))  # ✅ Теперь тип правильный
        self.setFixedWidth(5) if direction in (
            Qt.Edge.LeftEdge, Qt.Edge.RightEdge
        ) else self.setFixedHeight(5)

    def _get_cursor(self, edge: Qt.Edge) -> Qt.CursorShape:
        if edge == Qt.Edge.LeftEdge or edge == Qt.Edge.RightEdge:
            return Qt.CursorShape.SizeHorCursor
        elif edge == Qt.Edge.TopEdge or edge == Qt.Edge.BottomEdge:
            return Qt.CursorShape.SizeVerCursor
        elif edge == (Qt.Edge.LeftEdge | Qt.Edge.TopEdge):
            return Qt.CursorShape.SizeFDiagCursor
        elif edge == (Qt.Edge.RightEdge | Qt.Edge.TopEdge):
            return Qt.CursorShape.SizeBDiagCursor
        elif edge == (Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            return Qt.CursorShape.SizeBDiagCursor
        elif edge == (Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            return Qt.CursorShape.SizeFDiagCursor
        else:
            return Qt.CursorShape.ArrowCursor

    def mousePressEvent(self, event):
        main_window = self.parent()
        if event.button() == Qt.MouseButton.LeftButton:
            if isinstance(main_window, MainWindow):  # ✅ Проверяем тип
                main_window.window_start_resizing(self.direction)  # ✅ Теперь IDE знает, что он есть
        event.accept()

    def enterEvent(self, event):
        self.setCursor(self._get_cursor(self.direction))
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.resize(1200, 800)
        
        # Убираем стандартную рамку
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Заголовок
        self.title_bar = CustomTitleBar(self)

        # WebEngineView
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)

        # WebChannel
        self.channel = QWebChannel()
        self.browser.page().setWebChannel(self.channel)
        self.bridge = TaskBridge()
        self.channel.registerObject("bridge", self.bridge)

        # Расположение
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.browser)

        self.central_widget.setLayout(layout)

        # Связываем сигналы заголовка
        self.title_bar.windowClose.connect(self.close)
        self.title_bar.windowMinimize.connect(self.showMinimized)
        self.title_bar.windowMaximizeRestore.connect(self.toggle_maximize)

        # ✅ Добавляем рамки для изменения размера
        self.add_resize_borders()

        # WebEngineView
        self.browser.setStyleSheet("""
            background-color: white;
        """)

        self.setStyleSheet("""
                            background-color: qlineargradient(
                                    x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #2a1d35, 
                                    stop:1 #1f1524);
                            """)
        
        self._load_content()
    
    def add_resize_borders(self):
        self.resize_frames = {}

        directions = {
        "left": Qt.Edge.LeftEdge,
        "right": Qt.Edge.RightEdge,
        "top": Qt.Edge.TopEdge,
        "bottom": Qt.Edge.BottomEdge,
        "top_left": Qt.Edge.LeftEdge | Qt.Edge.TopEdge,
        "top_right": Qt.Edge.RightEdge | Qt.Edge.TopEdge,
        "bottom_left": Qt.Edge.LeftEdge | Qt.Edge.BottomEdge,
        "bottom_right": Qt.Edge.RightEdge | Qt.Edge.BottomEdge,
    }

        for name, direction in directions.items():
            frame = ResizableFrame(direction, self)
            self.resize_frames[name] = frame

    def resizeEvent(self, event):
        if self.isMaximized():
            for frame in self.resize_frames.values():
                frame.hide()
        else:
            self.resize_frames["left"].setGeometry(0, 0, 5, self.height())
            self.resize_frames["right"].setGeometry(self.width() - 5, 0, 5, self.height())
            self.resize_frames["top"].setGeometry(0, 0, self.width(), 5)
            self.resize_frames["bottom"].setGeometry(0, self.height() - 5, self.width(), 5)
            self.resize_frames["top_left"].setGeometry(0, 0, 5, 5)
            self.resize_frames["top_right"].setGeometry(self.width() - 5, 0, 5, 5)
            self.resize_frames["bottom_left"].setGeometry(0, self.height() - 5, 5, 5)
            self.resize_frames["bottom_right"].setGeometry(self.width() - 5, self.height() - 5, 5, 5)

            for frame in self.resize_frames.values():
                frame.show()  # ← ЭТО БЫЛО ПРОПУЩЕНО

        super().resizeEvent(event)

    def showEvent(self, event):
        self.resizeEvent(None)
        super().showEvent(event)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.resizeEvent(None)

    def window_start_resizing(self, edge: Qt.Edge):
        self.windowHandle().startSystemResize(edge)

    def _load_content(self):
        self.bridge.load_tasks()
        self.bridge.tasks_updated.connect(self.on_tasks_updated)
        current_dir = Path(__file__).resolve().parent
        html_path = current_dir / "resources" / "index.html"
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

    def on_tasks_updated(self, tasks):
        js_code = f"updateTaskList({json.dumps(tasks)})"
        self.browser.page().runJavaScript(js_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())