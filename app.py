import sys
from PyQt5.QtWidgets import QWidget, QApplication, QShortcut
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtCore import Qt, QPoint

class PaintWidget(QWidget):
    """
    Класс PaintWidget представляет собой окно для рисования, позволяющее пользователю рисовать произвольные линии с помощью мыши
    """

    def __init__(self):
        """
        Инициализация класса PaintWidget
        Создает список линий и устанавливает флаг рисования в False
        """
        super().__init__()
        self.lines = []  # Список линий
        self.drawing = False  # Флаг для отслеживания состояния рисования
        self.undo_stack = []  # Стек для отмены действий
        self.redo_stack = []  # Стек для повтора действий

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
            self.lines.append([event.pos()])  # Начало линии
            self.drawing = True  
            self.update()  

    def mouseMoveEvent(self, event):
        """
        Обработка события движения мыши
        Добавляет текущую позицию мыши в линию, когда пользователь рисует
        """
        if self.drawing:  # Добавление текущего положения при рисовании
            self.lines[-1].append(event.pos())  # Добавление точки в линию
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Обработка события отпускания мыши
        Завершает рисование, если была отпущена левая кнопка мыши
        """
        if event.button() == Qt.LeftButton:
            self.drawing = False  
            self.undo_stack.append(self.lines.copy())  # Сохраняем текущее состояние для отмены
            self.redo_stack.clear()  # Очищаем стек повтора при новом действии

    def paintEvent(self, event):
        """
        Обработка события рисования в окне
        Отрисовка линий на основе точек
        """
        qp = QPainter(self)
        qp.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        for line in self.lines:
            for i in range(len(line) - 1):
                qp.drawLine(line[i], line[i + 1])  # Рисование линии между точками

        qp.end()

    def undo(self):
        """
        Отмена последнего действия
        """
        if self.undo_stack:
            self.redo_stack.append(self.lines.copy())  # Сохраняем текущее состояние для повтора
            self.lines = self.undo_stack.pop()  # Восстанавливаем предыдущее состояние
            self.update()  

    def redo(self):
        """
        Повтор последнего отмененного действия
        """
        if self.redo_stack:
            self.undo_stack.append(self.lines.copy())  # Сохраняем текущее состояние для отмены
            self.lines = self.redo_stack.pop()  # Восстанавливаем состояние из стека повтора
            self.update()

    def resizeEvent(self, event):
        """
        Обработка события изменения размера окна
        """
        # Изменение размера в соответствии с размером окна
        width_scale = event.size().width() / self.size().width()
        height_scale = event.size().height() / self.size().height()

        for i in range(len(self.lines)):
            self.lines[i] = [QPoint(int(p.x() * width_scale), int(p.y() * height_scale)) for p in self.lines[i]]

        super().resizeEvent(event)  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PaintWidget()
    widget.resize(800, 600)  
    widget.show()
    sys.exit(app.exec_())
