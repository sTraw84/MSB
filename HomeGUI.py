import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import qdarkstyle
from RunScript_handler import send_securecrt_keys
import subprocess
import os

class HomeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.instructions_button = QPushButton("Instructions")
        self.instructions_button.clicked.connect(self.show_instructions)
        layout.addWidget(self.instructions_button)

        self.title_label = QLabel("WMS Script")
        self.title_label.setFont(QFont("Arial", weight=QFont.Bold))
        self.title_label.setStyleSheet("color: red;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.create_repack_button = QPushButton("Create Repack CSV")
        layout.addWidget(self.create_repack_button)

        self.create_split_button = QPushButton("Create Split CSV")
        self.create_split_button.clicked.connect(self.run_main_script)
        layout.addWidget(self.create_split_button)

        self.run_script_button = QPushButton("Run Script")
        self.run_script_button.clicked.connect(send_securecrt_keys)
        layout.addWidget(self.run_script_button)

        self.setLayout(layout)
        self.setWindowTitle("Home GUI")
        self.setGeometry(300, 300, 300, 200)

    def run_main_script(self):
        subprocess.Popen([sys.executable, "Main.py"])

    def show_instructions(self):
        instructions_file = "Instructions.txt"
        if os.path.exists(instructions_file):
            with open(instructions_file, "r") as file:
                instructions_text = file.read()
        else:
            instructions_text = "Instructions file not found."

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Instructions")
        msg.setText(instructions_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setSizeGripEnabled(True)
        msg.show()
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    ex = HomeGUI()
    ex.show()
    sys.exit(app.exec_())