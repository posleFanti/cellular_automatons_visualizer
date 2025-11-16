from matplotlib.backend_bases import button_press_handler
import numpy as np
import math
import random as rnd
import matplotlib.pyplot as plt
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QMainWindow,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# TODO: добавить случайное начальное положение, стандартные значения в QLineEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация одномерных КА")
        self.setGeometry(100, 100, 1200, 750)

        # Создаём центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Создаём Matplotlib Figure
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumWidth(500)
        left_layout.addWidget(self.canvas, stretch=2)
        left_layout.setStretchFactor(left_layout, 2)

        # Панель инструментов
        self.toolbar = NavigationToolbar(self.canvas, self)
        left_layout.addWidget(self.toolbar)

        layout.addWidget(left_widget)

        # Форма пользовательского ввода
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        form_widget.setMaximumWidth(400)

        self.rule_input = QLineEdit()
        self.N_input = QLineEdit()
        self.x0_input = QTextEdit()
        self.gens_input = QLineEdit()
        self.grid_cb = QCheckBox("Сетка")
        self.button_group = QButtonGroup()
        self.custom_x_rb = QRadioButton("Задать свое начальное положение")
        self.random_x_rb = QRadioButton("Случайное начальное положение")
        self.one_x_rb = QRadioButton("Начальное положение с единицей на N/2")
        self.button = QPushButton("Обновить график")

        self.custom_x_rb.setChecked(True)

        form_layout.addRow(QLabel("Правило КА:"), self.rule_input)
        form_layout.addRow(QLabel("N (длина):"), self.N_input)
        form_layout.addRow(QLabel("x_0 (длина N):"), self.x0_input)
        form_layout.addRow(QLabel("Число итераций:"), self.gens_input)

        form_layout.addRow(self.grid_cb)
        form_layout.addRow(self.custom_x_rb)
        form_layout.addRow(self.random_x_rb)
        form_layout.addRow(self.one_x_rb)
        form_layout.addRow(self.button)

        self.button_group.addButton(self.custom_x_rb)
        self.button_group.addButton(self.random_x_rb)
        self.button_group.addButton(self.one_x_rb)

        self.button.clicked.connect(self.updatePlot)

        for widget in [self.rule_input, self.N_input, self.x0_input, self.gens_input]:
            widget.setMinimumWidth(150)

        self.x0_input.setMaximumHeight(60)

        layout.addWidget(form_widget)

    def updatePlot(self):
        try:
            self.fig.clear()
            self.getStartParams()
            self.history = self.calcHistory(self.x0)
            self.plot_CA()
            self.plot_hamming_dist()
            self.plot_density()
            self.plot_entropy()
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(e)

    def plot_CA(self):
        ax = self.fig.add_subplot(221)
        ax.matshow(np.array(self.history), cmap="binary", aspect="equal", zorder=1)
        ax.set_title("Визуализация ЭКА")
        ax.set_xlabel("Индекс клетки")
        ax.set_ylabel("Шаг")
        ax.set_xticks(np.arange(-0.5, self.N, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.gens, 1), minor=True)
        if self.grid_cb.isChecked():
            ax.grid(
                which="minor", color="black", linestyle="-", linewidth=0.5, zorder=0
            )

    def plot_hamming_dist(self):
        ax = self.fig.add_subplot(222)
        dists = []
        for i in range(len(self.history) - 1):
            dists.append(calcHammingDist(self.history[i], self.history[i + 1], self.N))
        ax.set_title("Расстояние Хэмминга")
        ax.plot(dists)

    def plot_density(self):
        ax = self.fig.add_subplot(223)
        densities = []
        for x in self.history:
            densities.append(calc_density(x))
        ax.set_title("Плотность")
        ax.plot(densities)

    def plot_entropy(self):
        ax = self.fig.add_subplot(224)
        entropies = []
        for x in self.history:
            entropies.append(calc_entropy(x))
        ax.set_title("Энтропия Шеннона")
        ax.plot(entropies)

    def calcHistory(self, arr):
        history = []
        for _ in range(self.gens):
            n = len(arr)
            new_arr = [0] * n
            for i in range(n):
                p = arr[(i - 1) % n]
                q = arr[i]
                r = arr[(i + 1) % n]
                new_arr[i] = moveCA(p, q, r, self.rule)
            history.append(arr)
            arr = new_arr
        return history

    def getStartParams(self):
        ca = self.rule_input.text()
        if len(ca) != 8:
            raise ValueError("Длина вектора КА должна быть равна 8")
        self.rule = [int(j) for j in ca]
        checkBinary(self.rule)

        self.N = int(self.N_input.text())

        if self.custom_x_rb.isChecked():
            input_vec = self.x0_input.toPlainText()
            if len(input_vec) != self.N:
                raise ValueError("Длина вектора x_0 != N")
            self.x0 = [int(j) for j in input_vec]
            checkBinary(self.x0)
        elif self.one_x_rb.isChecked():
            self.x0 = self.set_arr_with_one()
        else:
            self.x0 = [rnd.randint(0, 1) for _ in range(self.N)]

        self.gens = int(self.gens_input.text())

    def set_arr_with_one(self):
        arr = [0] * self.N
        arr[self.N // 2] = 1
        return arr


def moveCA(p, q, r, v):
    ind = 4 * p + 2 * q + r
    return v[ind]


def checkBinary(vec):
    for i in vec:
        if i not in [0, 1]:
            raise ValueError("Вектор должен быть двоичным")


def calcHammingDist(a, b, n):
    dist = 0
    for i in range(n):
        dist += (a[i] - b[i]) % 2
    return dist


def calc_density(a):
    dens = 0
    for i in a:
        dens += i
    return dens / len(a)


def calc_entropy(a):
    r = calc_density(a)
    return r * math.log2(r) - (1 - r) * math.log2(1 - r) if 0 < r < 1 else 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
