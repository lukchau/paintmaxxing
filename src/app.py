import sys
import random
from PyQt5.QtWidgets import QMainWindow, QApplication, QShortcut, QMenuBar, QAction, QInputDialog, QColorDialog, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtCore import Qt, QPoint


class PaintWidget(QMainWindow):
    """
    Класс PaintWidget представляет собой окно для рисования, позволяющее пользователю рисовать произвольные линии с помощью мыши
    """

    def __init__(self):
        """
        Инициализация класса PaintWidget
        Создает список линий и устанавливает флаг рисования в False
        """
        super().__init__()
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        self.lines_buffer = []  
        self.drawing = False  
        self.undo_stack = [[]]
        self.redo_stack = []  

        self.current_pen = QPen(Qt.black, 2, Qt.SolidLine)
        self.current_tool = "Линия"  # Дифолтный инструмент

        # Настройка сочетаний клавиш для отмены и повтора
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo)

        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redo_shortcut.activated.connect(self.redo)

    def mousePressEvent(self, event):
        """
        Обработка события нажатия левой кнопки мыши
        Начинает новую линию, если нажата левая кнопка мыши
        """
        if event.button() == Qt.LeftButton:
            # Новый QPen с текущими настройками
            new_pen = QPen(self.current_pen.color(), self.current_pen.width(), self.current_pen.style())
            self.lines_buffer.append(([], new_pen))  # Новая линия 
            self.drawing = True  
            self.update()  

    def mouseMoveEvent(self, event):
        """
        Обработка события движения мыши
        Добавляет текущую позицию мыши в линию, когда пользователь рисует
        """
        if self.drawing:
            if self.current_tool == "Линия":
                self.lines_buffer[-1][0].append(event.pos())  # Добавление точки в линию
            elif self.current_tool == "Граффити":
                self.spray(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Обработка события отпускания мыши
        Завершает рисование, если была отпущена левая кнопка мыши
        """
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.undo_stack.append(self.lines_buffer[:])  # Сохраняем текущее состояние для отмены
            self.redo_stack.clear()  # Очищаем стек повтора при новом действии

    def paintEvent(self, event):
        """
        Обработка события рисования в окне
        Отрисовка линий на основе точек
        """
        qp = QPainter(self)
        for line, pen in self.lines_buffer:
            qp.setPen(pen)  # Текущие настройки
            for i in range(len(line) - 1):
                qp.drawLine(line[i], line[i + 1])  # Рисование линии между точками

        qp.end()

        
    def spray(self, position):
        """
        Симуляция эффекта граффити путем рисования случайных точек вокруг курсора
        """
        radius = 20  # Радиус разбрызгивания
        density = 150  # Плотность точек

        for _ in range(density):
            offset_x = random.randint(-radius, radius)
            offset_y = random.randint(-radius, radius)
            if offset_x**2 + offset_y**2 <= radius**2:
                self.lines_buffer[-1][0].append(QPoint(position.x() + offset_x, position.y() + offset_y))

    def undo(self):
        """
        Отмена последнего действия
        """ 
        if self.undo_stack:
            self.redo_stack.append(self.lines_buffer[:])  # Сохраняем текущее состояние для повтора
            self.lines_buffer = self.undo_stack.pop()  # Восстанавливаем предыдущее состояние
            self.update()  

    def redo(self):
        """
        Повтор последнего отмененного действия
        """
        if self.redo_stack:
            self.undo_stack.append(self.lines_buffer[:])  # Сохраняем текущее состояние для отмены
            self.lines_buffer = self.redo_stack.pop()  # Восстанавливаем состояние из стека повтора
            self.update()

    def resizeEvent(self, event):
        """
        Обработка события изменения размера окна
        """
        # Изменение размера в соответствии с размером окна
        width_scale = event.size().width() / self.size().width()
        height_scale = event.size().height() / self.size().height()

        self.lines_buffer = [
            ([QPoint(int(p.x() * width_scale), int(p.y() * height_scale)) for p in line[0]], line[1])
            for line in self.lines_buffer
        ]

        super().resizeEvent(event)
    
    def save_image(self, file_name, format, exclude_menu=False):
        if exclude_menu:
            drawing_area = self.geometry()
            drawing_area.setTop(drawing_area.top() + self.menubar.height())  

            image = self.grab(drawing_area)
        else:
            image = self.grab(Qt.CopyAllAttributes)  

        image.save(file_name, format)


class ToolAction(QAction):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.name = name

class LineTool(ToolAction):
    def __init__(self, parent=None):
        super().__init__("Линия", parent)

class GraffitiTool(ToolAction):
    def __init__(self, parent=None):
        super().__init__("Граффити", parent)

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_menu = self.addMenu("Файл")
        self.save_as_menu = self.file_menu.addMenu("Сохранить как")
        self.save_as_jpg_action = QAction("JPG", self)
        self.save_as_png_action = QAction("PNG", self)
        self.save_as_menu.addAction(self.save_as_jpg_action)
        self.save_as_menu.addAction(self.save_as_png_action)

        self.tools_menu = self.addMenu("Инструменты")
        self.eraser_menu = self.addMenu("Ластик")
        self.figures_menu = self.addMenu("Фигуры")
        # TODO: добавить фигуры (круг, квадрат, треугольник)
        self.color_thickness_menu = self.addMenu("Цвет и Толщина")
        # TODO: добавить выбор цвета и толщины

        self.line_tool = LineTool(self)
        self.graffiti_tool = GraffitiTool(self)

        self.tools_menu.addAction(self.line_tool)
        self.tools_menu.addAction(self.graffiti_tool)

        self.line_tool.triggered.connect(self.on_line_tool_triggered)
        self.graffiti_tool.triggered.connect(self.on_graffiti_tool_triggered)

        self.color_action = QAction("Цвет", self)
        self.color_action.triggered.connect(self.on_color_menu_triggered)
        self.color_thickness_menu.addAction(self.color_action)

        self.thickness_action = QAction("Толщина", self)
        self.thickness_action.triggered.connect(self.on_thickness_menu_triggered)
        self.color_thickness_menu.addAction(self.thickness_action)

        self.save_as_jpg_action.triggered.connect(self.on_save_as_jpg_triggered)
        self.save_as_png_action.triggered.connect(self.on_save_as_png_triggered)


    def on_line_tool_triggered(self):
        self.parent().current_tool = "Линия"
        self.parent().current_pen = QPen(self.parent().current_pen.color(), self.parent().current_pen.width(), Qt.SolidLine) 

    def on_graffiti_tool_triggered(self):
        self.parent().current_tool = "Граффити"
        self.parent().current_pen = QPen(self.parent().current_pen.color(), self.parent().current_pen.width(), Qt.SolidLine)
        self.parent().drawing = True 
        self.parent().update() 
    
    def on_color_menu_triggered(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent().current_pen.setColor(color)

    def on_thickness_menu_triggered(self):
        thickness, ok = QInputDialog.getInt(self, "Толщина", "Введите толщину:")
        if ok:
            self.parent().current_pen.setWidth(thickness)

    def on_save_as_jpg_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "JPG Файл (*.jpg)")
        if file_name:
            self.parent().save_image(file_name, "jpg", exclude_menu=True)

    def on_save_as_png_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "PNG Файл (*.png)")
        if file_name:
            self.parent().save_image(file_name, "png", exclude_menu=True)

    def on_file_menu_triggered(self):
        self.save_as_menu.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PaintWidget()
    widget.resize(800, 600)  
    widget.show()
    sys.exit(app.exec_())