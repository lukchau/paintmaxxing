from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QPointF
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QKeySequence,
    QImage,
    QPixmap,
    QIcon,
    QTabletEvent,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QShortcut,
    QToolBar,
    QAction,
    QInputDialog,
    QColorDialog,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
    QSlider,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QDialogButtonBox,
    QToolButton,
    QMenu,
    QWidgetAction,
)
from PyQt5.QtWidgets import QPushButton, QButtonGroup
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QPainter, QPen, QKeySequence, QImage, QPixmap, QColor, QPolygonF
import sys
import random
import os
import math

"""
Класс PaintWidget представляет собой окно для рисования, позволяющее пользователю рисовать произвольные линии с помощью мыши
"""
class PaintWidget(QMainWindow):
    """
    Инициализация класса PaintWidget
    Создает список линий и устанавливает флаг рисования в False
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paintmaxxing")
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(current_dir, "icons")

        app_icon = QIcon(os.path.join(icons_dir, "icon_256x256.png"))

        self.setWindowIcon(app_icon)

        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.lines_buffer = []
        self.drawing = False
        self.undo_stack = [[]]
        self.redo_stack = []

        self.current_pen = QPen(Qt.black, 2, Qt.SolidLine)
        self.min_thickness = 1  # Минимальная толщина пера
        self.max_thickness = 10  # Максимальная толщина пера

        self.current_tool = "Линия"  # Дифолтный инструмент

        """
        Настройка сочетаний клавиш для отмены и повтора
        """
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo)

        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redo_shortcut.activated.connect(self.redo)

        self.zoom_level = 100
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(self.zoom_level)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        self.zoom_label = QLabel(f"Зум: {self.zoom_level}%")

        self.offset = QPoint(0, 0)
        self.panning = False
        self.pan_start = QPoint(0, 0)

        self.sheet_size = QSize(
            self.width() * 2, (self.height() - self.toolbar.height()) * 2
        )
        self.original_offset = QPoint(0, 0)

        """
        Инициализация тулбара, зума и палитры
        """
        self.init_toolbar()
        self.init_zoom_control()
        self.init_palette()

    """
    Инициализация тулбара
    """
    def init_toolbar(self):
        # Создание инструментов
        self.line_tool = QAction("Линия", self)
        self.eraser_action = QAction("Ластик", self)
        self.graffiti_tool = QAction("Граффити", self)
        self.save_as_jpg_action = QAction("Сохранить как JPG", self)
        self.save_as_png_action = QAction("Сохранить как PNG", self)
        self.undo_action = QAction("Отменить", self)
        self.redo_action = QAction("Повторить", self)
        self.rectangle_tool = QAction("Прямоугольник", self)
        self.circle_tool = QAction("Круг", self)
        self.ellipse_tool = QAction("Эллипс", self)
        self.arrow_tool = QAction("Стрелка", self)

        # Добавление инструментов в тулбар
        self.toolbar.addAction(self.line_tool)
        self.toolbar.addAction(self.eraser_action)
        self.toolbar.addAction(self.graffiti_tool)
        self.toolbar.addAction(self.save_as_jpg_action)
        self.toolbar.addAction(self.save_as_png_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addAction(self.rectangle_tool)
        self.toolbar.addAction(self.circle_tool)
        self.toolbar.addAction(self.ellipse_tool)
        self.toolbar.addAction(self.arrow_tool)

        # Добавляем кнопку с выпадающим меню для настройки толщины пера
        self.thickness_menu_button = QToolButton(self)
        self.thickness_menu_button.setText("Толщина")
        self.thickness_menu_button.setPopupMode(QToolButton.InstantPopup)

        self.thickness_menu = QMenu(self)
        self.thickness_menu_button.setMenu(self.thickness_menu)

        # Создаём виджет для меню
        thickness_menu_widget = QWidget(self)
        thickness_menu_layout = QVBoxLayout(thickness_menu_widget)

        # Слайдер для минимальной толщины
        min_thickness_label = QLabel("Мин. толщина:")
        self.min_thickness_slider = QSlider(Qt.Horizontal, self)
        self.min_thickness_slider.setRange(1, 50)
        self.min_thickness_slider.setValue(1)  # По умолчанию минимальная толщина

        # Слайдер для максимальной толщины
        max_thickness_label = QLabel("Макс. толщина:")
        self.max_thickness_slider = QSlider(Qt.Horizontal, self)
        self.max_thickness_slider.setRange(1, 50)
        self.max_thickness_slider.setValue(10)  # По умолчанию максимальная толщина

        # Добавляем элементы в макет
        thickness_menu_layout.addWidget(min_thickness_label)
        thickness_menu_layout.addWidget(self.min_thickness_slider)
        thickness_menu_layout.addWidget(max_thickness_label)
        thickness_menu_layout.addWidget(self.max_thickness_slider)
        thickness_menu_widget.setLayout(thickness_menu_layout)

        # Упаковываем виджет в действие
        thickness_menu_action = QWidgetAction(self)
        thickness_menu_action.setDefaultWidget(thickness_menu_widget)
        self.thickness_menu.addAction(thickness_menu_action)

        # Добавляем кнопку меню в тулбар
        self.toolbar.addWidget(self.thickness_menu_button)

        # Добавляем кнопку вызова палитры
        self.color_picker_button = QPushButton("Выбор цвета", self)
        self.color_picker_button.clicked.connect(self.on_color_picker_button_clicked)
        self.toolbar.addWidget(self.color_picker_button)

        # Подключение сигналов
        self.line_tool.triggered.connect(self.on_line_tool_triggered)
        self.eraser_action.triggered.connect(self.on_eraser_tool_triggered)
        self.graffiti_tool.triggered.connect(self.on_graffiti_tool_triggered)
        self.save_as_jpg_action.triggered.connect(self.on_save_as_jpg_triggered)
        self.save_as_png_action.triggered.connect(self.on_save_as_png_triggered)
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.rectangle_tool.triggered.connect(lambda: self.set_shape_tool("rectangle"))
        self.circle_tool.triggered.connect(lambda: self.set_shape_tool("circle"))
        self.ellipse_tool.triggered.connect(lambda: self.set_shape_tool("ellipse"))
        self.arrow_tool.triggered.connect(lambda: self.set_shape_tool("arrow"))

        # Обработка сигналов слайдеров
        self.min_thickness_slider.valueChanged.connect(self.on_min_thickness_changed)
        self.max_thickness_slider.valueChanged.connect(self.on_max_thickness_changed)

    """
    Обработчик изменения минимальной толщины
    """
    def on_min_thickness_changed(self, value):
        print(f"Минимальная толщина изменена на: {value}")
        if value > self.max_thickness_slider.value():
            self.max_thickness_slider.setValue(value)  # Синхронизация слайдеров
        self.update_pen_thickness()  # Обновляем толщину пера

    """
    Обработчик изменения максимальной толщины
    """
    def on_max_thickness_changed(self, value):
        print(f"Максимальная толщина изменена на: {value}")
        if value < self.min_thickness_slider.value():
            self.min_thickness_slider.setValue(value)  # Синхронизация слайдеров
        self.update_pen_thickness()  # Обновляем толщину пера

    """
    Обновляет текущую толщину пера на основе слайдеров
    """
    def update_pen_thickness(self):
        self.min_thickness = self.min_thickness_slider.value()
        self.max_thickness = self.max_thickness_slider.value()
        self.current_pen.setWidth(self.max_thickness)  # Устанавливаем максимальную толщину

    """
    Обработчик для кнопки вызова палитры цветов
    """
    def on_color_picker_button_clicked(self):
        color = QColorDialog.getColor(
            initial=self.current_pen.color(), parent=self, title="Выбор цвета"
        )
        if color.isValid():
            self.current_pen.setColor(color)

    """
    Создание палитры цветов в тулбаре
    """
    def init_palette(self):
        # Список предустановленных цветов
        colors = [
            "#000000",
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#FF00FF",
            "#00FFFF",
            "#FFFFFF",
        ]

        self.palette_group = QButtonGroup(self)  # Группа кнопок
        self.palette_group.buttonClicked.connect(
            self.on_palette_color_selected)

        for color in colors:
            button = QPushButton()
            button.setFixedSize(20, 20)  # Фиксированный размер кнопки
            button.setStyleSheet(
                f"background-color: {color}; border: 1px solid #000;")
            self.palette_group.addButton(button)
            self.toolbar.addWidget(button)  # Добавляем кнопку в тулбар

    """
    Установка цвета из палитры
    """
    def on_palette_color_selected(self, button):
        color = button.styleSheet().split(
            "background-color: ")[1].split(";")[0]
        self.current_pen.setColor(QColor(color))

    """
    Инициализация управления зумом
    """
    def init_zoom_control(self):
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_slider)

        zoom_widget = QWidget()
        zoom_widget.setLayout(zoom_layout)
        zoom_widget.setFixedWidth(300)

        self.statusBar().addPermanentWidget(zoom_widget)

    """
    Обработка событий планшета
    """
    def tabletEvent(self, event: QTabletEvent):
        position = event.posF()  # Используем QPointF для работы с дробными координатами
        if event.type() == QTabletEvent.TabletPress:
            if self.current_tool == "Ластик":
                self.last_erase_position = None  # Сбрасываем предыдущую позицию
                self.erase(position)  # Начинаем стирать при нажатии
            else:
                self.start_new_line(position, event.pressure())

        elif event.type() == QTabletEvent.TabletMove:
            if self.current_tool == "Ластик":
                if self.last_erase_position:
                    # Проверяем расстояние между точками, чтобы уменьшить частоту стирания
                    dist = (
                        (position.x() - self.last_erase_position.x()) ** 2
                        + (position.y() - self.last_erase_position.y()) ** 2
                    ) ** 0.5
                    if dist < 10:  # Минимальное расстояние между точками стирания
                        return
                self.last_erase_position = position
                self.erase(position)  # Продолжаем стирать при движении
            else:
                self.add_to_line(position, event.pressure())

        elif event.type() == QTabletEvent.TabletRelease:
            if self.current_tool != "Ластик":
                self.end_current_line()  # Завершаем линию только для рисования

        event.accept()

    """
    Начало новой линии с настройкой толщины пера
    """
    def start_new_line(self, position, pressure):
        self.drawing = True
        self.current_line = []
        thickness = self.calculate_thickness(pressure)
        self.current_pen.setWidth(thickness)
        self.lines_buffer.append((self.current_line, QPen(self.current_pen)))

    """
    Добавление точки в текущую линию
    """
    def add_to_line(self, position, pressure):
        if self.drawing:
            thickness = self.calculate_thickness(pressure)
            self.current_pen.setWidth(thickness)
            self.lines_buffer[-1][0].append(position)
            self.update()

    """
    Завершение текущей линии
    """
    def end_current_line(self):
        self.drawing = False

    """
    Вычисление толщины линии на основе силы нажатия
    """
    def calculate_thickness(self, pressure):
        return int(
            self.min_thickness + (self.max_thickness -
                                  self.min_thickness) * pressure
        )

    """
    Обработка события нажатия кнопки мыши
    """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() > self.toolbar.height():
            if self.current_tool == "Ластик":
                self.erase(event.pos())
            elif self.current_tool == "Фигура":
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.drawing = True
                self.update()
            else:
                new_pen = QPen(self.current_pen.color(), self.current_pen.width(), self.current_pen.style())
                self.start_new_line(event.pos(), 1.0)
                self.lines_buffer.append(([], new_pen))
                self.drawing = True
                self.update()
        elif event.button() == Qt.RightButton:
            self.panning = True
            self.pan_start = event.pos()

    """
    Обработка движения мыши
    """
    def mouseMoveEvent(self, event):
        if self.current_tool == "Ластик" and event.y() > self.toolbar.height():
            self.erase(event.pos())
        elif self.current_tool == "Фигура" and self.drawing:
            self.end_point = event.pos()
            self.update()  # Обновляем для отображения текущей фигуры
        elif self.drawing and event.y() > self.toolbar.height():
            if self.current_tool == "Линия":
                self.lines_buffer[-1][0].append(self.adjust_mouse_position(event.pos()))
            elif self.current_tool == "Граффити":
                self.spray(self.adjust_mouse_position(event.pos()))
            self.update()
        elif self.panning:
            delta = event.pos() - self.pan_start
            self.offset += delta
            self.pan_start = event.pos()
            self.update()

    """
    Обработка события отпускания кнопки мыши
    """
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() > self.toolbar.height():
            if self.current_tool == "Ластик":
                pass
            elif self.current_tool == "Фигура":
                # Добавляем текущую фигуру в буфер
                self.lines_buffer.append(
                    ((self.start_point, self.end_point), QPen(self.current_pen), self.current_shape))
                self.drawing = False
                self.undo_stack.append(self.lines_buffer[:])
                self.redo_stack.clear()
                self.update()
            else:
                self.drawing = False
                self.undo_stack.append(self.lines_buffer[:])
                self.redo_stack.clear()
                self.update()
        elif event.button() == Qt.RightButton:
            self.panning = False

    """
    Отрисовка линий и фигур
    """
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), Qt.lightGray)
        qp.translate(self.offset)
        qp.scale(self.zoom_level / 100.0, self.zoom_level / 100.0)
        qp.fillRect(QRect(QPoint(0, 0), self.sheet_size), Qt.white)
        drawing_area = QRect(0, 0, self.sheet_size.width(), self.sheet_size.height())
        qp.setClipRect(drawing_area)

        # Отрисовка всех линий и фигур из lines_buffer
        for item in self.lines_buffer:
            if len(item) == 3:  # Это фигура
                points, pen, shape = item
                qp.setPen(pen)
                self.draw_shape(qp, points[0], points[1], shape)
            else:  # Это линия
                line, pen = item
                qp.setPen(pen)
                if line:
                    for i in range(len(line) - 1):
                        qp.drawLine(line[i], line[i + 1])

        # Временная отрисовка текущей фигуры
        if self.current_tool == "Фигура" and self.drawing:
            qp.setPen(self.current_pen)
            self.draw_shape(qp, self.start_point, self.end_point, self.current_shape)

        qp.end()

    """
    Стирает часть линии в радиусе ластика, создавая разрыв
    """
    def erase(self, position):
        eraser_radius = self.current_pen.width()  # Используем текущую толщину пера для ластика
        new_lines_buffer = []

        for line, pen in self.lines_buffer:
            new_line = []
            for i in range(len(line) - 1):
                start = line[i]
                end = line[i + 1]

                # Если сегмент пересекает радиус ластика
                if self.segment_intersects_circle(start, end, position, eraser_radius):
                    if new_line:  # Если есть незавершенная часть линии
                        new_lines_buffer.append((new_line, pen))
                    new_line = []  # Начинаем новую часть
                else:
                    new_line.append(start)

            # Добавляем последнюю точку, если она осталась
            if new_line:
                new_line.append(line[-1])
                new_lines_buffer.append((new_line, pen))

        self.lines_buffer = [
            line for line in new_lines_buffer if len(line[0]) > 1
        ]  # Убираем пустые линии
        self.update()

    """
    Проверяет, пересекает ли отрезок окружность
    """
    def segment_intersects_circle(self, start, end, center, radius):
        # Вектор от начала отрезка до конца
        ab = end - start
        ab_len_squared = ab.x() ** 2 + ab.y() ** 2
        if ab_len_squared == 0:  # Начальная и конечная точка совпадают
            return (center - start).manhattanLength() <= radius

        # Вектор от начала отрезка до центра окружности
        ac = center - start

        # Проекция центра окружности на линию отрезка
        projection_ratio = (ac.x() * ab.x() + ac.y() * ab.y()) / ab_len_squared
        projection_ratio = max(
            0, min(1, projection_ratio)
        )  # Ограничиваем в пределах отрезка
        closest_point = QPointF(
            start.x() + projection_ratio * ab.x(), start.y() + projection_ratio * ab.y()
        )

        # Проверяем расстояние от ближайшей точки до центра окружности
        return (closest_point - center).manhattanLength() <= radius

    """
    Симуляция эффекта граффити путем рисования случайных точек вокруг курсора
    """
    def spray(self, position):
        radius = 20  # Радиус разбрызгивания
        density = 150  # Плотность точек

        for _ in range(density):
            offset_x = random.randint(-radius, radius)
            offset_y = random.randint(-radius, radius)
            if offset_x**2 + offset_y**2 <= radius**2:
                self.lines_buffer[-1][0].append(
                    QPoint(position.x() + offset_x, position.y() + offset_y)
                )

    """
    Установка инструмента для рисования фигуры
    """
    def set_shape_tool(self, shape):
        self.current_shape = shape
        self.current_tool = "Фигура"

    """
    Рисование фигуры
    """
    def draw_shape(self, qp, start, end, shape):
        if shape == "rectangle":
            qp.drawRect(QRectF(start, end))
        elif shape == "circle":
            radius = min(abs(end.x() - start.x()), abs(end.y() - start.y())) / 2
            center = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            qp.drawEllipse(center, radius, radius)
        elif shape == "ellipse":
            qp.drawEllipse(QRectF(start, end))
        elif shape == "arrow":
            # Рисуем стрелку (линия с треугольником)
            qp.drawLine(start, end)
            angle = math.atan2(end.y() - start.y(), end.x() - start.x())
            arrow_size = 10
            p1 = QPointF(
                end.x() - arrow_size * math.cos(angle - math.pi / 6),
                end.y() - arrow_size * math.sin(angle - math.pi / 6)
            )
            p2 = QPointF(
                end.x() - arrow_size * math.cos(angle + math.pi / 6),
                end.y() - arrow_size * math.sin(angle + math.pi / 6)
            )
            qp.drawPolygon(QPolygonF([end, p1, p2]))

    """
    Отмена последнего действия
    """
    def undo(self):
        if self.undo_stack:
            # Сохраняем текущее состояние для повтора
            self.redo_stack.append(self.lines_buffer[:])
            # Восстанавливаем предыдущее состояние
            self.lines_buffer = self.undo_stack.pop()
            self.update()

    """
    Повтор последнего отмененного действия
    """
    def redo(self):
        if self.redo_stack:
            # Сохраняем текущее состояние для отмены
            self.undo_stack.append(self.lines_buffer[:])
            # Восстанавливаем состояние из стека повтора
            self.lines_buffer = self.redo_stack.pop()
            self.update()

    """
    Обработка события изменения размера окна
    """
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sheet_size = QSize(
            self.width() * 2, (self.height() - self.toolbar.height()) * 2
        )

    """
    Сохранение изображения в файл
    """
    def save_image(self, file_name, format):
        # Сохранить полное изображение в файл
        drawing_area = QRect(0, 0, self.sheet_size.width(),
                             self.sheet_size.height())
        image = QImage(drawing_area.size(), QImage.Format_ARGB32)
        image.fill(Qt.white)

        qp = QPainter(image)
        for line, pen in self.lines_buffer:
            qp.setPen(pen)
            for i in range(len(line) - 1):
                qp.drawLine(line[i], line[i + 1])

        qp.end()
        image.save(file_name, format)

    """
    Переключение на инструмент линии
    """
    def on_line_tool_triggered(self):
        self.current_tool = "Линия"
        self.current_pen.setColor(Qt.black)  # Восстанавливаем цвет пера в черный
        self.current_pen.setWidth(self.max_thickness)  # Восстанавливаем толщину пера

    """
    Переключение на инструмент ластика
    """
    def on_eraser_tool_triggered(self):
        self.current_tool = "Ластик"
        self.current_pen.setColor(Qt.white)  # Устанавливаем цвет ластика в белый

    """
    Переключение на инструмент граффити
    """
    def on_graffiti_tool_triggered(self):
        self.current_tool = "Граффити"
        self.current_pen = QPen(
            self.current_pen.color(), self.current_pen.width(), Qt.SolidLine
        )
        self.drawing = True
        self.update()

    """
    Обработчик для кнопки вызова палитры цветов
    """
    def on_color_menu_triggered(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_pen.setColor(color)

    """
    Диалог для настройки минимальной и максимальной толщины пера
    """
    def on_thickness_menu_triggered(self):
        thickness, ok = QInputDialog.getInt(
            self, "Толщина", "Введите толщину:")
        if ok:
            self.current_pen.setWidth(thickness)

    """
    Обработчик события сохранения изображения в формате JPG
    """
    def on_save_as_jpg_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", self.get_downloads_folder(), "JPG Файл (*.jpg)"
        )
        if file_name:
            self.save_image(file_name, "jpg")
            return True
        return False

    """
    Обработчик события сохранения изображения в формате PNG
    """
    def on_save_as_png_triggered(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", self.get_downloads_folder(), "PNG Файл (*.png)"
        )
        if file_name:
            self.save_image(file_name, "png")
            return True
        return False

    """
    Обработчик изменения уровня зума
    """
    def on_zoom_changed(self, value):
        self.zoom_level = value
        self.zoom_label.setText(f"Зум: {self.zoom_level}%")
        if self.zoom_level == 100:
            self.offset = self.original_offset
        self.update()

    """
    Выровнять позицию курсора при зуме
    """
    def adjust_mouse_position(self, pos):
        adjusted_pos = QPoint(
            int((pos.x() - self.offset.x()) / (self.zoom_level / 100.0)),
            int((pos.y() - self.offset.y()) / (self.zoom_level / 100.0)),
        )
        return adjusted_pos

    """
    Получить путь к папке "загрузки"
    """
    def get_downloads_folder(self):
        return os.path.join(os.path.expanduser("~"), "Downloads")

    """
    Обработка события закрытия окна
    """
    def closeEvent(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Сохранить")
        msg_box.setText("Вы хотите сохранить рисунок перед закрытием?")
        msg_box.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        cancel_button = msg_box.button(QMessageBox.Cancel)
        cancel_button.setText("Отмена")

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            format_msg_box = QMessageBox(self)
            format_msg_box.setWindowTitle("Выберите формат")
            format_msg_box.setText("Выберите формат для сохранения:")
            format_msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Cancel)

            save_button = format_msg_box.button(QMessageBox.Save)
            save_button.setText("Сохранить как JPG")
            cancel_button = format_msg_box.button(QMessageBox.Cancel)
            cancel_button.setText("Отмена")

            format_msg_box.addButton(
                "Сохранить как PNG", QMessageBox.AcceptRole)

            format_reply = format_msg_box.exec_()

            if format_reply == QMessageBox.Save:
                if not self.on_save_as_jpg_triggered():
                    event.ignore()
                    return
            elif format_msg_box.clickedButton().text() == "Сохранить как PNG":
                if not self.on_save_as_png_triggered():
                    event.ignore()
                    return
            else:
                event.ignore()
                return

            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(current_dir, "icons")
    app_icon = QIcon(os.path.join(icons_dir, "icon_256x256.png"))
    QApplication.setWindowIcon(app_icon)
    widget = PaintWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())
