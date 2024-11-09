import sys
import random
from PyQt5.QtWidgets import QMainWindow, QApplication, QShortcut, QMenuBar, QAction
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
            self.lines_buffer.append([event.pos()])  # Начало линии
            self.drawing = True  
            self.update()  

    def mouseMoveEvent(self, event):
        """
        Обработка события движения мыши
        Добавляет текущую позицию мыши в линию, когда пользователь рисует
        """
        if self.drawing:
            if self.current_tool == "Линия":
                self.lines_buffer[-1].append(event.pos())  # Добавление точки в линию
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
        qp.setPen(self.current_pen)

        for line in self.lines_buffer:
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
                self.lines_buffer[-1].append(QPoint(position.x() + offset_x, position.y() + offset_y))

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
            [QPoint(int(p.x() * width_scale), int(p.y() * height_scale)) for p in line]
            for line in self.lines_buffer
        ]

        super().resizeEvent(event)


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
        # TODO: добавить сохранение и загрузку
        self.tools_menu = self.addMenu("Инструменты")
        self.eraser_menu = self.addMenu("Ластик")
        self.figures_menu = self.addMenu("Фигуры")
        # TODO: добавить фигуры (круг, квадрат, треугольник)
        self.color_menu = self.addMenu("Цвет")
        # TODO: добавить выбор цвета
        self.thickness_menu = self.addMenu("Толщина")
        # TODO: добавить выбор толщины

        self.line_tool = LineTool(self)
        self.graffiti_tool = GraffitiTool(self)

        self.tools_menu.addAction(self.line_tool)
        self.tools_menu.addAction(self.graffiti_tool)

        self.line_tool.triggered.connect(self.on_line_tool_triggered)
        self.graffiti_tool.triggered.connect(self.on_graffiti_tool_triggered)

    def on_line_tool_triggered(self):
        self.parent().current_tool = "Линия"
        self.parent().current_pen = QPen(Qt.black, 2, Qt.SolidLine)  

    def on_graffiti_tool_triggered(self):
        self.parent().current_tool = "Граффити"
        self.parent().drawing = True 
        self.parent().update() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PaintWidget()
    widget.resize(800, 600)  
    widget.show()
    sys.exit(app.exec_())