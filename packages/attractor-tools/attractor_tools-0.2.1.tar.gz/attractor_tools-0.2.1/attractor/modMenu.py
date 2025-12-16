from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit, QCheckBox, QHBoxLayout
from PyQt6.QtGui import QKeySequence, QShortcut
from .colormap import ColorMap
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import QRegularExpression, QTimer
if 0 != 0: from .frame import SimonFrame

class SideWindow(QWidget):
    def __init__(self, frame: "SimonFrame"):
        super().__init__()
        self.frame = frame
        self.setWindowTitle("Mod Menu")
        self.setGeometry(100, 100, 300, 200)  # x, y, width, height
        self.setFixedSize(300, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.initUi()
        self.signals()
        self.keyboardShortcuts()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initUi(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        # Ui Elements
        self.a = QLineEdit("a")
        self.b = QLineEdit("b")
        self.iterations = QLineEdit("iterations")
        self.resolution = QLineEdit("resolution")
        self.percentile = QLineEdit("percentile")
        self.colormap = QComboBox()
        self.colormap.addItems(ColorMap.colormaps())
        self.colormap.setCurrentText(self.frame.colors.name)
        self.inverted = QCheckBox("")

        # Labels
        label_a = QLabel("a: ")
        label_b = QLabel("b: ")
        label_iterations = QLabel("iterations: ")
        label_resolution = QLabel("resolution: ")
        label_colormap = QLabel("colormap: ")
        label_percentile = QLabel("percentile: ")

        w = 80
        label_a.setFixedWidth(w)
        label_b.setFixedWidth(w)
        label_iterations.setFixedWidth(w)
        label_resolution.setFixedWidth(w)
        label_colormap.setFixedWidth(w)
        label_percentile.setFixedWidth(w)

        # Layout Structure
        layout_colormap = QHBoxLayout()
        layout_colormap.addWidget(label_colormap)
        layout_colormap.addWidget(self.colormap)
        layout_colormap.addWidget(self.inverted)

        a_layout = QHBoxLayout()
        a_layout.addWidget(label_a)
        a_layout.addWidget(self.a)

        b_layout = QHBoxLayout()
        b_layout.addWidget(label_b)
        b_layout.addWidget(self.b)

        iterations_layout = QHBoxLayout()
        iterations_layout.addWidget(label_iterations)
        iterations_layout.addWidget(self.iterations)

        res_layout = QHBoxLayout()
        res_layout.addWidget(label_resolution)
        res_layout.addWidget(self.resolution)

        percentile_layout = QHBoxLayout()
        percentile_layout.addWidget(label_percentile)
        percentile_layout.addWidget(self.percentile)
        
        # Add Elements to Ui
        mainLayout.addLayout(a_layout)
        mainLayout.addLayout(b_layout)
        mainLayout.addLayout(iterations_layout)
        mainLayout.addLayout(percentile_layout)
        mainLayout.addLayout(res_layout)
        mainLayout.addLayout(layout_colormap)

        # LineEdit Validators
        float_regex = QRegularExpression(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
        validator = QRegularExpressionValidator(float_regex)
        self.a.setValidator(validator)
        self.b.setValidator(validator)
        self.percentile.setValidator(validator)

        int_validator = QIntValidator()
        self.iterations.setValidator(int_validator)
        self.resolution.setValidator(int_validator)
        QTimer.singleShot(100, lambda: self.a.clearFocus())

    def signals(self):
        self.a.editingFinished.connect(lambda: self.update_frame())
        self.b.editingFinished.connect(lambda: self.update_frame())
        self.iterations.editingFinished.connect(lambda: self.update_frame())
        self.colormap.currentTextChanged.connect(lambda: self.update_frame())
        self.inverted.checkStateChanged.connect(lambda: self.update_frame())
        self.resolution.editingFinished.connect(lambda: self.update_frame())
        self.percentile.editingFinished.connect(lambda: self.update_frame())

    def save_frame(self):
        n = self.frame.n
        self.frame.n = 10_000_000 if self.frame.n < 10_000_000 else self.frame.n
        self.frame.save_with_dialogue()
        self.frame.n = n

    def arrow_keys(self, key: str):
        delta = 0.01
        match key:
            case "up":
                self.frame.a += delta
            case "down":
                self.frame.a -= delta
            case "left":
                self.frame.b -= delta
            case "right":
                self.frame.b += delta
        self.frame.render()

    def next_colormap(self, direction: bool):
        index = self.colormap.currentIndex()
        max_index = self.colormap.count()

        if direction:
            index += 1
        else:
            index -= 1

        if index >= max_index:
            index = 0

        if index < 0:
            index = max_index - 1

        self.colormap.setCurrentIndex(index)
    
    def highResolutionRender(self):
        # render once in high resolution
        tmp_n = self.frame.n
        tmp_res = self.frame.resolution

        self.frame.n = 10_000_000
        self.frame.resolution = 1500
        self.frame.render()

        self.frame.n = tmp_n
        self.frame.resolution = tmp_res

    def update_inverted(self):
        self.inverted.setChecked(not self.inverted.isChecked())
        self.frame.add_colors()

    def keyboardShortcuts(self):
        # Ctrl+S
        QShortcut(QKeySequence("Ctrl+S"), self, member=lambda: self.save_frame())
        # Arrow keys
        QShortcut(QKeySequence(Qt.Key.Key_Q), self, member=lambda: self.close())
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, member=lambda: self.arrow_keys("up"))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, member=lambda: self.arrow_keys("down"))
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, member=lambda: self.arrow_keys("left"))

        QShortcut(QKeySequence(Qt.Key.Key_Right), self, member=lambda: self.arrow_keys("right"))

        QShortcut(QKeySequence(Qt.Key.Key_PageUp), self, member=lambda: self.next_colormap(True))
        QShortcut(QKeySequence(Qt.Key.Key_PageDown), self, member=lambda: self.next_colormap(False))

        QShortcut(QKeySequence(Qt.Key.Key_F1), self, member=lambda: self.highResolutionRender())
        QShortcut(QKeySequence(Qt.Key.Key_I), self, member=lambda: self.update_inverted())

    def update_frame(self):
        try:
            self.frame.n = int(self.iterations.text())
            self.frame.a = float(self.a.text())
            self.frame.b = float(self.b.text())
            self.frame.colors = ColorMap(self.colormap.currentText(), inverted=self.inverted.isChecked())
            self.frame.resolution = int(self.resolution.text())
            self.frame.percentile = float(self.percentile.text())
        except ValueError:
            return
        self.frame.render()

    def updateUi(self):
        self.a.setText(str(self.frame.a))
        self.b.setText(str(self.frame.b))
        self.iterations.setText(str(self.frame.n))
        self.colormap.setCurrentText(self.frame.colors.name)
        self.inverted.setChecked(self.frame.colors.inverted)
        self.resolution.setText(str(self.frame.resolution))
        self.percentile.setText(f"{self.frame.percentile:.2f}")