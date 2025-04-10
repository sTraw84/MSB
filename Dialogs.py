from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton

class ListDialog(QDialog):
    def __init__(self, title, existing_list=None):
        super().__init__()
        self.list_data = existing_list if existing_list else []
        self.initUI(title)

    def initUI(self, title):
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)
        if self.list_data:
            self.text_edit.setPlainText("\n".join(self.list_data))
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton('OK', self)
        cancel_button = QPushButton('Cancel', self)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        self.layout.addLayout(buttons_layout)

    def accept(self):
        self.list_data = self.text_edit.toPlainText().splitlines()
        super().accept()