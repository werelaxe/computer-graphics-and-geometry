from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QTimerEvent
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QPointF
import numpy as np
from math import cos, pi
import sys

from geom import Polygon

WIDTH = 1000
HEIGHT = 800


def cart2pol(cart_point: QPointF):
    x, y = cart_point.x(), cart_point.y()
    r = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return QPointF(r, phi)


def pol2cart(polar_point: QPointF):
    r, phi = polar_point.x(), polar_point.y()
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return QPointF(x, y)


def first_func(x, a, b, c):
    den = ((b + x) * (c - x) ** 2)
    if den == 0:
        return 999999
    return (a * x) / den


def second_func(phi, a, b, _):
    return a + b * cos(phi)
    # return phi


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.axis_pen = QPen(Qt.green)
        self.func_pen = QPen(Qt.red)
        self.axis_pen.setWidth(3)
        self.func_pen.setWidth(3)
        self.coords_pen = QPen(Qt.green)
        self.padding = 0
        self.panelWidth = 200
        self.tracking = False
        self.last_coords = QPoint(0, 0)
        self.initVars()
        self.initUI()

    def get_current_task(self):
        return self.TASKS[self.task_number - 1]

    def initVars(self):
        self.a = 1
        self.b = 1
        self.c = 1
        k = 5
        self.t_left_top = QPointF(-k, -k)
        self.t_right_bottom = QPointF(k, k)
        self.steps_count = 500
        self.alpha = self.t_left_top.x()
        self.beta = self.t_right_bottom.x()
        self.task_number = 1
        self.TASKS = {
            0: self.draw_first_func,
            1: self.draw_second_func,
            2: self.draw_ellipse,
            3: self.draw_polygons_residual,
        }

    def initUI(self):
        self.setGeometry(800 - WIDTH // 2, 450 - HEIGHT // 2, WIDTH, HEIGHT)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(40, 40, 40))
        self.setPalette(p)
        validator = QDoubleValidator()
        validator.setLocale(QLocale("Russia"))
        self.parameters = [QLineEdit(self) for _ in range(3)]
        offset = 120
        for i in range(len(self.parameters)):
            self.parameters[i].setGeometry(80, offset + 40 * i, 100, 30)
            self.parameters[i].setValidator(validator)
            self.parameters[i].setText("1")
            label = QLabel(self)
            label.setText("{} = ".format(chr(i + ord('a'))))
            label.setGeometry(50, offset + 40 * i, 70, 30)
            label.setStyleSheet("color: white")
        self.parameters[0].textChanged.connect(self.update_a_field)
        self.parameters[1].textChanged.connect(self.update_b_field)
        self.parameters[2].textChanged.connect(self.update_c_field)

        label = QLabel(self)
        label.setGeometry(65, 450, 60, 30)
        label.setText("alpha = ")
        label.setStyleSheet('color: white')
        self.alpha_field = QLineEdit(self)
        self.alpha_field.setGeometry(120, 450, 60, 30)
        self.alpha_field.setValidator(validator)
        self.alpha_field.setText(str(self.alpha))
        self.alpha_field.textChanged.connect(self.update_alpha_field)

        label = QLabel(self)
        label.setGeometry(65, 500, 60, 30)
        label.setText("beta = ")
        label.setStyleSheet('color: white')
        self.beta_field = QLineEdit(self)
        self.beta_field.setGeometry(120, 500, 60, 30)
        self.beta_field.setValidator(validator)
        self.beta_field.setText(str(self.beta))
        self.beta_field.textChanged.connect(self.update_beta_field)
        combo = QComboBox(self)
        combo.addItems(["Task {}".format(i) for i in range(1, len(self.TASKS) + 1)])
        combo.move(60, 15)
        combo.activated[str].connect(self.onSelect)

        self.label = QLabel(self)
        pixmap = QPixmap('formula{}.png'.format(self.task_number))
        self.label.setPixmap(pixmap)
        self.label.move((self.panelWidth - pixmap.width()) / 2, 50)
        # self.label.move(0, 100)
        self.label.setGeometry((self.panelWidth - pixmap.width()) / 2, 50, pixmap.width() + 100, pixmap.height())

        label = QLabel(self)
        label.setGeometry(40, 275, 60, 30)
        label.setText("left")
        label.setStyleSheet('color: white')
        self.left_x_text_field = QLineEdit(self)
        self.left_x_text_field.setGeometry(40, 300, 60, 30)
        self.left_x_text_field.setText(str(self.t_left_top.x()))
        self.left_x_text_field.setValidator(validator)
        self.left_x_text_field.textChanged.connect(self.update_left_x_field)

        label = QLabel(self)
        label.setGeometry(120, 275, 60, 30)
        label.setText("top")
        label.setStyleSheet('color: white')
        self.left_y_text_field = QLineEdit(self)
        self.left_y_text_field.setGeometry(120, 380, 60, 30)
        self.left_y_text_field.setText(str(self.t_left_top.y()))
        self.left_y_text_field.setValidator(validator)
        self.left_y_text_field.textChanged.connect(self.update_left_y_field)

        label = QLabel(self)
        label.setGeometry(40, 355, 60, 30)
        label.setText("right")
        label.setStyleSheet('color: white')
        self.right_x_text_field = QLineEdit(self)
        self.right_x_text_field.setGeometry(40, 380, 60, 30)
        self.right_x_text_field.setText(str(self.t_right_bottom.x()))
        self.right_x_text_field.setValidator(validator)
        self.right_x_text_field.textChanged.connect(self.update_right_x_field)

        label = QLabel(self)
        label.setGeometry(120, 355, 60, 30)
        label.setText("bottom")
        label.setStyleSheet('color: white')
        self.right_y_text_field = QLineEdit(self)
        self.right_y_text_field.setGeometry(120, 300, 60, 30)
        self.right_y_text_field.setText(str(self.t_right_bottom.y()))
        self.right_y_text_field.setValidator(validator)
        self.right_y_text_field.textChanged.connect(self.update_right_y_field)

        self.setWindowTitle('Points')
        self.show()

    def onSelect(self, text):
        self.task_number = int(text[-1])
        pixmap = QPixmap('formula{}.png'.format(self.task_number))
        self.label.setPixmap(pixmap)
        self.label.move((self.panelWidth - pixmap.width()) / 2, 50)
        self.update()

    def update_left_x_field(self):
        try:
            self.t_left_top.setX(float(self.left_x_text_field.text()))
            self.update()
        except ValueError:
            pass

    def update_left_y_field(self):
        try:
            self.t_left_top.setY(float(self.left_y_text_field.text()))
            self.update()
        except ValueError:
            pass

    def update_right_x_field(self):
        try:
            self.t_right_bottom.setX(float(self.right_x_text_field.text()))
            self.update()
        except ValueError:
            pass

    def update_right_y_field(self):
        try:
            self.t_right_bottom.setY(float(self.right_y_text_field.text()))
            self.update()
        except ValueError:
            pass

    def update_a_field(self):
        try:
            self.a = float(self.parameters[0].text())
            self.update()
        except ValueError:
            pass

    def update_b_field(self):
        try:
            self.b = float(self.parameters[0].text())
            self.update()
        except ValueError:
            pass

    def update_c_field(self):
        try:
            self.c = float(self.parameters[0].text())
            self.update()
        except ValueError:
            pass

    def update_alpha_field(self):
        try:
            self.alpha = float(self.alpha_field.text())
            self.update()
        except ValueError:
            pass

    def update_beta_field(self):
        try:
            self.beta = float(self.beta_field.text())
            self.update()
        except ValueError:
            pass

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / 400

        self.t_left_top.setX(self.t_left_top.x() + delta)
        self.t_right_bottom.setX(self.t_right_bottom.x() - delta)
        self.t_left_top.setY(self.t_left_top.y() + delta)
        self.t_right_bottom.setY(self.t_right_bottom.y() - delta)

        self.left_x_text_field.setText(str(round(self.t_left_top.x(), 2)))
        self.right_x_text_field.setText(str(round(self.t_right_bottom.x(), 2)))

        self.left_y_text_field.setText(str(round(self.t_left_top.y(), 2)))
        self.right_y_text_field.setText(str(round(self.t_right_bottom.y(), 2)))

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.tracking:
            return
        delta = event.pos() - self.last_coords
        t_delta = QPointF(delta.x() / self.get_x_scale(),
                          delta.y() / self.get_y_scale())
        t_delta = QPointF(-t_delta.x(), t_delta.y())
        self.t_left_top += t_delta
        self.t_right_bottom += t_delta
        self.left_x_text_field.setText(str(round(self.t_left_top.x(), 2)))
        self.right_x_text_field.setText(str(round(self.t_right_bottom.x(), 2)))

        self.left_y_text_field.setText(str(round(self.t_left_top.y(), 2)))
        self.right_y_text_field.setText(str(round(self.t_right_bottom.y(), 2)))
        self.last_coords = event.pos()
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.tracking = True
        self.last_coords = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.tracking = False

    def leftTop(self):
        return QPointF(self.panelWidth, self.padding)

    def rightBottom(self):
        return QPointF(self.width() - self.padding, self.height() - self.padding)

    def real_width(self):
        return self.rightBottom().x() - self.leftTop().x()

    def real_height(self):
        return self.rightBottom().y() - self.leftTop().y()

    def t_width(self):
        return self.t_right_bottom.x() - self.t_left_top.x()

    def t_height(self):
        return self.t_right_bottom.y() - self.t_left_top.y()

    def get_x_scale(self):
        return self.real_width() / self.t_width()

    def get_y_scale(self):
        return self.real_height() / self.t_height()

    def get_real_coord(self, t_coords):
        relative_t_coords = t_coords - self.t_left_top
        relative_real_coords = QPointF(relative_t_coords.x() * self.get_x_scale(),
                                       self.real_height() - relative_t_coords.y() * self.get_y_scale())
        return relative_real_coords + self.leftTop()

    def paintEvent(self, _):
        try:
            self.b = float(self.parameters[1].text())
        except ValueError:
            pass
        try:
            self.c = float(self.parameters[2].text())
        except ValueError:
            pass

        qp = QPainter()
        qp.begin(self)
        qp.setPen(Qt.black)
        qp.setBrush(Qt.black)
        qp.drawRect(self.leftTop().x(), self.leftTop().y(), self.real_width(), self.real_height())
        self.draw_net(qp)
        qp.setPen(self.func_pen)
        self.get_current_task()(qp, self.a, self.b, self.c)
        qp.end()

    def draw_net(self, qp):
        qp.setPen(self.axis_pen)
        p0 = self.get_real_coord(QPointF(self.t_left_top.x(), 0))
        p1 = self.get_real_coord(QPointF(self.t_right_bottom.x(), 0))
        p2 = self.get_real_coord(QPointF(0, self.t_left_top.y()))
        p3 = self.get_real_coord(QPointF(0, self.t_right_bottom.y()))
        if self.t_left_top.y() < 0:
            qp.drawLine(p0, p1)
        if self.t_left_top.x() < 0:
            qp.drawLine(p2, p3)
        qp.setPen(self.coords_pen)
        for i in range(int(self.t_left_top.x()), int(self.t_right_bottom.x() + 1)):
            p1 = self.get_real_coord(QPointF(i, self.t_right_bottom.y()))
            p0 = self.get_real_coord(QPointF(i, self.t_left_top.y()))
            if p0.x() > self.leftTop().x():
                qp.drawLine(p0, p1)
        for i in range(int(self.t_left_top.y()), int(self.t_right_bottom.y() + 1)):
            p1 = self.get_real_coord(QPointF(self.t_right_bottom.x(), i))
            p0 = self.get_real_coord(QPointF(self.t_left_top.x(), i))
            qp.drawLine(p0, p1)

    def draw_first_func(self, qp, *params):
        # step_size = (self.t_right_bottom.x() - self.t_left_top.x()) / (self.steps_count - 1)
        step_size = (self.beta - self.alpha) / (self.steps_count - 1)
        t_x_0 = self.t_left_top.x()
        t_y_0 = first_func(t_x_0, *params)
        start_point = QPointF(t_x_0, t_y_0)
        prev_point = self.get_real_coord(start_point)
        for i in range(1, self.steps_count):
            t_x = i * step_size + self.t_left_top.x()
            t_y = first_func(t_x, *params)
            c_point = QPointF(t_x, t_y)
            current_point = self.get_real_coord(c_point)
            if abs(current_point.y() - prev_point.y()) < self.real_height() * 2:
                qp.drawLine(prev_point, current_point)
            prev_point = current_point

    def draw_second_func(self, qp, *params):
        prev_point = pol2cart(QPointF(second_func(0, *params), 0))
        step_size = (self.beta - self.alpha) / (self.steps_count - 1)
        for i in range(1, self.steps_count):
            phi = i * step_size
            r = second_func(phi, *params)
            new_point = pol2cart(QPointF(r, phi))
            qp.drawLine(
                self.get_real_coord(prev_point),
                self.get_real_coord(new_point),
            )
            prev_point = new_point

    def draw_ellipse(self, qp: QPainter, *params):
        a = self.a
        b = self.b
        x0 = int(self.leftTop().x() + (self.width() - self.leftTop().x()) // 2)
        y0 = self.height() // 2
        r = self.c * self.get_x_scale()
        x = x0 - r
        y = y0
        counter = 0
        pixel_size = 10
        while x < x0:
            qp.drawRect(x - pixel_size // 2, y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(2 * x0 - x - pixel_size // 2, 2 * y0 - y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(x - pixel_size // 2, 2 * y0 - y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(2 * x0 - x - pixel_size // 2, y - pixel_size // 2, pixel_size, pixel_size)
            xs = [0, 1]
            ys = [0, -1]
            min_point = 0, 0
            min_len = 9999999
            for dx in xs:
                for dy in ys:
                    if not dx and not dy:
                        continue
                    new_x = x + dx * pixel_size
                    new_y = y + dy * pixel_size
                    ln = abs((new_x - x0) ** 2 * a + (new_y - y0) ** 2 * b - r ** 2)
                    if ln < min_len:
                        min_len = ln
                        min_point = new_x, new_y
            x, y = min_point
            x, y = int(x), int(y)
            qp.drawRect(x - pixel_size // 2, y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(2 * x0 - x - pixel_size // 2, 2 * y0 - y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(x - pixel_size // 2, 2 * y0 - y - pixel_size // 2, pixel_size, pixel_size)
            qp.drawRect(2 * x0 - x - pixel_size // 2, y - pixel_size // 2, pixel_size, pixel_size)
            counter += 1

    def draw_polygon(self, qp: QPainter, polygon: Polygon):
        for i in range(-1, len(polygon.pure_points) - 1):
            qp.drawLine(
                self.get_real_coord(QPointF(*polygon.pure_points[i].coords)),
                self.get_real_coord(QPointF(*polygon.pure_points[i + 1].coords))
            )

    def draw_polygons_residual(self, qp: QPainter, *params):
        p1 = Polygon([-4, -3, -2, -1, -4, 2, -2, 4, 1, 3, 4, 2, 3, -1, 1, -3])
        p2 = Polygon([-2, -4, -3, 0, 0, 4, 2, 1, 3, -4])
        if self.a == 1:
            self.draw_polygon(qp, p1)

        if self.b == 1:
            blue_pen = QPen(Qt.blue)
            blue_pen.setWidth(3)
            qp.setPen(blue_pen)
            self.draw_polygon(qp, p2)

        if self.c != 1:
            yellow_pen = QPen(Qt.yellow)
            yellow_pen.setWidth(3)
            qp.setPen(yellow_pen)
            for p in p1 - p2:
                self.draw_polygon(qp, p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
