import numpy as np
import matplotlib.pyplot as plt
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFormLayout,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# TODO: добавить расстояния, анализ


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация одномерных КА")
        self.setGeometry(100, 100, 1000, 600)

        # Создаём центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Создаём Matplotlib Figure
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        left_layout.addWidget(self.canvas, stretch=3)

        # Панель инструментов
        self.toolbar = NavigationToolbar(self.canvas, self)
        left_layout.addWidget(self.toolbar)

        layout.addWidget(left_widget)

        # Форма пользовательского ввода
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.rule_input = QLineEdit()
        self.N_input = QLineEdit()
        self.x0_input = QLineEdit()
        self.gens_input = QLineEdit()
        self.grid_check_box = QCheckBox()

        form_layout.addRow(QLabel("Правило КА:"), self.rule_input)
        form_layout.addRow(QLabel("N (длина):"), self.N_input)
        form_layout.addRow(QLabel("x_0 (длина N):"), self.x0_input)
        form_layout.addRow(QLabel("Число итераций:"), self.gens_input)

        self.button = QPushButton("Обновить график")
        form_layout.addRow(self.grid_check_box, QLabel("Сетка"))
        form_layout.addRow(self.button)
        self.button.clicked.connect(self.updatePlot)

        layout.addWidget(form_widget, stretch=1)

    def updatePlot(self):
        try:
            self.getStartParams()
            self.history = self.calcHistory(self.x0)
            self.plot()
        except Exception as e:
            print(e)

    def plot(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.matshow(np.array(self.history), cmap="binary", aspect="equal", zorder=1)
        ax.set_title("Одномерный клеточный автомат")
        ax.set_xlabel("Индекс клетки")
        ax.set_ylabel("Шаг")
        ax.set_xticks(np.arange(-0.5, self.N, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.gens, 1), minor=True)
        if self.grid_check_box.isChecked():
            ax.grid(
                which="minor", color="black", linestyle="-", linewidth=0.5, zorder=0
            )
        self.fig.tight_layout()
        self.canvas.draw()

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

        input_vec = self.x0_input.text()
        if len(input_vec) != self.N:
            raise ValueError("Длина вектора x_0 != N")
        self.x0 = [int(j) for j in input_vec]
        checkBinary(self.x0)

        self.gens = int(self.gens_input.text())


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
