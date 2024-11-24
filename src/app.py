import sys
import random
from PyQt5.QtWidgets import QMainWindow, QApplication, QShortcut, QToolBar, QAction, QInputDialog, QColorDialog, QFileDialog, QVBoxLayout, QWidget, QLabel, QSpinBox, QHBoxLayout
from PyQt5.QtGui import QPainter, QPen, QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

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

        self.setWindowTitle("Paintmaxxing")
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

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

        self.zoom_level = 100
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setRange(10, 500)
        self.zoom_spinbox.setValue(self.zoom_level)
        self.zoom_spinbox.valueChanged.connect(self.on_zoom_changed)

        self.offset = QPoint(0, 0)
        self.panning = False
        self.pan_start = QPoint(0, 0)

        self.sheet_size = QSize(self.width() * 2, (self.height() - self.toolbar.height()) * 2)
        self.original_offset = QPoint(0, 0)

        self.init_toolbar()
        self.init_zoom_control()

    def init_toolbar(self):
        self.line_tool = QAction("Линия", self)
        self.graffiti_tool = QAction("Граффити", self)
        self.color_action = QAction("Цвет", self)
        self.thickness_action = QAction("Толщина", self)
        self.save_as_jpg_action = QAction("Сохранить как JPG", self)
        self.save_as_png_action = QAction("Сохранить как PNG", self)
        self.undo_action = QAction("Отменить", self)
        self.redo_action = QAction("Повторить", self)

        self.toolbar.addAction(self.line_tool)
        self.toolbar.addAction(self.graffiti_tool)
        self.toolbar.addAction(self.color_action)
        self.toolbar.addAction(self.thickness_action)
        self.toolbar.addAction(self.save_as_jpg_action)
        self.toolbar.addAction(self.save_as_png_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)

        self.line_tool.triggered.connect(self.on_line_tool_triggered)
        self.graffiti_tool.triggered.connect(self.on_graffiti_tool_triggered)
        self.color_action.triggered.connect(self.on_color_menu_triggered)
        self.thickness_action.triggered.connect(self.on_thickness_menu_triggered)
        self.save_as_jpg_action.triggered.connect(self.on_save_as_jpg_triggered)
        self.save_as_png_action.triggered.connect(self.on_save_as_png_triggered)
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)

    def init_zoom_control(self):
        zoom_label = QLabel("Зум:")
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_spinbox)

        zoom_widget = QWidget()
        zoom_widget.setLayout(zoom_layout)
        zoom_widget.setFixedWidth(150)

        self.statusBar().addPermanentWidget(zoom_widget)

    def mousePressEvent(self, event):
        """
        Обработка события нажатия левой кнопки мыши
        Начинает новую линию, если нажата левая кнопка мыши
        """
        if event.button() == Qt.LeftButton and event.y() > self.toolbar.height():
            # Новый QPen с текущими настройками
            new_pen = QPen(self.current_pen.color(), self.current_pen.width(), self.current_pen.style())
            self.lines_buffer.append(([], new_pen))  # Новая линия
            self.drawing = True
            self.update()
        elif event.button() == Qt.RightButton:
            self.panning = True
            self.pan_start = event.pos()

    def mouseMoveEvent(self, event):
        """
        Обработка события движения мыши
        Добавляет текущую позицию мыши в линию, когда пользователь рисует
        """
        if self.drawing and event.y() > self.toolbar.height():
            if self.current_tool == "Линия":
                self.lines_buffer[-1][0].append(self.adjust_mouse_position(event.pos()))  # Добавление точки в линию
            elif self.current_tool == "Граффити":
                self.spray(self.adjust_mouse_position(event.pos()))
            self.update()
        elif self.panning:
            delta = event.pos() - self.pan_start
            self.offset += delta
            self.pan_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Обработка события отпускания мыши
        Завершает рисование, если была отпущена левая кнопка мыши
        """
        if event.button() == Qt.LeftButton and event.y() > self.toolbar.height():
            self.drawing = False
            self.undo_stack.append(self.lines_buffer[:])  # Сохраняем текущее состояние для отмены
            self.redo_stack.clear()  # Очищаем стек повтора при новом действии
        elif event.button() == Qt.RightButton:
            self.panning = False

    def paintEvent(self, event):
        """
        Обработка события рисования в окне
        Отрисовка линий на основе точек
        """
        qp = QPainter(self)
        qp.fillRect(self.rect(), Qt.lightGray)  # Заполнить фон серым цветом
        qp.translate(self.offset)
        qp.scale(self.zoom_level / 100.0, self.zoom_level / 100.0)
        qp.fillRect(QRect(QPoint(0, 0), self.sheet_size), Qt.white)  # Заполнить лист белым цветом
        drawing_area = QRect(0, 0, self.sheet_size.width(), self.sheet_size.height())
        qp.setClipRect(drawing_area)
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
        super().resizeEvent(event)
        self.sheet_size = QSize(self.width() * 2, (self.height() - self.toolbar.height()) * 2)

    def save_image(self, file_name, format):
        # Сохранить полное изображение в файл
        drawing_area = QRect(0, 0, self.sheet_size.width(), self.sheet_size.height())
        image = QImage(drawing_area.size(), QImage.Format_ARGB32)
        image.fill(Qt.white)

        qp = QPainter(image)
        for line, pen in self.lines_buffer:
            qp.setPen(pen)
            for i in range(len(line) - 1):
                qp.drawLine(line[i], line[i + 1])

        qp.end()
        image.save(file_name, format)

    def on_line_tool_triggered(self):
        self.current_tool = "Линия"
        self.current_pen = QPen(self.current_pen.color(), self.current_pen.width(), Qt.SolidLine)

    def on_graffiti_tool_triggered(self):
        self.current_tool = "Граффити"
        self.current_pen = QPen(self.current_pen.color(), self.current_pen.width(), Qt.SolidLine)
        self.drawing = True
        self.update()

    def on_color_menu_triggered(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_pen.setColor(color)

    def on_thickness_menu_triggered(self):
        thickness, ok = QInputDialog.getInt(self, "Толщина", "Введите толщину:")
        if ok:
            self.current_pen.setWidth(thickness)

    def on_save_as_jpg_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "JPG Файл (*.jpg)")
        if file_name:
            self.save_image(file_name, "jpg")

    def on_save_as_png_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "PNG Файл (*.png)")
        if file_name:
            self.save_image(file_name, "png")

    def on_zoom_changed(self, value):
        self.zoom_level = value
        if self.zoom_level == 100:
            self.offset = self.original_offset
        self.update()

    def adjust_mouse_position(self, pos):
        """
        Выровнять позицию курсора при зуме
        """
        adjusted_pos = QPoint(
            int((pos.x() - self.offset.x()) / (self.zoom_level / 100.0)),
            int((pos.y() - self.offset.y()) / (self.zoom_level / 100.0))
        )
        return adjusted_pos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PaintWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())
