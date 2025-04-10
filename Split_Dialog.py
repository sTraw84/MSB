import tempfile
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QMessageBox, QFileDialog, QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QInputDialog
from PyQt5.QtCore import Qt
import CSV_Writer  # Updated import statement to match the file name
import CSV_Loader  # Import the new CSV_Loader module
from Dialogs import ListDialog  # Updated import statement to match the file name

class SplitDialog(QDialog):
    def __init__(self):
        try:
            super().__init__()
            self.initUI()
            self.temp_csv_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
            self.csv_headers = ["NUMBER", "PROMPT", "KEY", "DATA", "MARKER"]
            self.row_counter = 1
            self.total_builds = 0  # Initialize total builds counter
            CSV_Writer.write_csv_headers(self.temp_csv_file, self.csv_headers)
            self.child_part_counter = 0
            self.c40_list = []
            self.master_sn_list = []
            self.child_sn_list = []
            self.lpn_changed = False  # Track if the LPN has been changed
        except Exception as e:
            print(f"Error initializing SplitDialog: {e}")

    def initUI(self):
        try:
            self.setWindowTitle('Split Questions')
            self.setFixedSize(496, 500)
            self.main_layout = QVBoxLayout(self)

            # Create horizontal layout for error box and counter box
            self.top_layout = QHBoxLayout()
            self.status_label = QLabel(self)
            self.top_layout.addWidget(self.status_label)

            # Add counter label
            self.counter_label = QLabel('Total Builds: 0', self)
            self.counter_label.setAlignment(Qt.AlignRight)
            self.top_layout.addWidget(self.counter_label)

            # Add the top layout to the main layout
            self.main_layout.addLayout(self.top_layout)

            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_content = QWidget(self.scroll_area)
            self.scroll_layout = QVBoxLayout(self.scroll_content)
            self.scroll_area.setWidget(self.scroll_content)
            self.main_layout.addWidget(self.scroll_area)
            self.from_lpn_layout = QHBoxLayout()
            self.from_lpn_label = QLabel('From LPN:', self)
            self.from_lpn_textbox = QLineEdit(self)
            self.from_lpn_layout.addWidget(self.from_lpn_label)
            self.from_lpn_layout.addWidget(self.from_lpn_textbox)
            self.scroll_layout.addLayout(self.from_lpn_layout)
            question1_layout = QHBoxLayout()
            question1_label = QLabel('Do you need master parts packed onto a C40?', self)
            self.question1_checkbox = QCheckBox(self)
            self.question1_checkbox.stateChanged.connect(self.toggle_part_number)
            question1_layout.addWidget(question1_label)
            question1_layout.addWidget(self.question1_checkbox)
            self.scroll_layout.addLayout(question1_layout)
            self.master_part_layout = QHBoxLayout()
            self.master_part_label = QLabel('Master Part:', self)
            self.master_part_textbox = QLineEdit(self)
            self.master_sn_list_button = QPushButton('Master SN List', self)
            self.master_sn_list_button.setFixedWidth(self.master_sn_list_button.sizeHint().width())
            self.master_sn_list_button.clicked.connect(self.open_master_sn_list_dialog)
            self.master_part_layout.addWidget(self.master_part_label)
            self.master_part_layout.addWidget(self.master_part_textbox)
            self.master_part_layout.addWidget(self.master_sn_list_button)
            self.master_part_label.hide()
            self.master_part_textbox.hide()
            self.master_sn_list_button.hide()
            self.scroll_layout.addLayout(self.master_part_layout)
            question2_layout = QHBoxLayout()
            question2_label = QLabel('How many child parts per C40?', self)
            add_button = QPushButton('+', self)
            remove_button = QPushButton('-', self)
            add_button.setFixedWidth(20)
            remove_button.setFixedWidth(20)
            add_button.clicked.connect(self.add_child_part)
            remove_button.clicked.connect(self.remove_child_part)
            add_child_sns_button = QPushButton("Add Child SN's", self)
            add_child_sns_button.setFixedWidth(add_child_sns_button.sizeHint().width())
            add_child_sns_button.clicked.connect(self.prompt_child_sns)
            question2_layout.addWidget(question2_label)
            question2_layout.addWidget(add_button)
            question2_layout.addWidget(remove_button)
            question2_layout.addWidget(add_child_sns_button)
            self.scroll_layout.addLayout(question2_layout)
            self.child_parts_layout = QVBoxLayout()
            self.scroll_layout.addLayout(self.child_parts_layout)
            question3_layout = QHBoxLayout()
            question3_label = QLabel("How many C40's are built this way?", self)
            self.question3_textbox = QLineEdit(self)
            self.add_c40_list_button = QPushButton('C40 List', self)
            self.add_c40_list_button.clicked.connect(self.open_c40_list_dialog)
            question3_layout.addWidget(question3_label)
            question3_layout.addWidget(self.question3_textbox)
            question3_layout.addWidget(self.add_c40_list_button)
            self.scroll_layout.addLayout(question3_layout)
            self.scroll_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
            buttons_layout = QHBoxLayout()
            add_to_csv_button = QPushButton('Add to CSV', self)
            load_csv_button = QPushButton('Load CSV', self)  # Add Load CSV button
            save_csv_button = QPushButton('Save CSV', self)
            preview_csv_button = QPushButton('Preview CSV', self)
            clear_fields_button = QPushButton('Clear Inputs', self)  # Changed button text
            start_over_button = QPushButton('New CSV', self)  # Changed button text
            add_to_csv_button.clicked.connect(self.on_next_build)
            load_csv_button.clicked.connect(self.load_csv)  # Connect Load CSV button to load_csv method
            save_csv_button.clicked.connect(self.on_finish_csv)
            preview_csv_button.clicked.connect(self.preview_csv)
            clear_fields_button.clicked.connect(self.clear_data_fields)
            start_over_button.clicked.connect(self.start_over)
            buttons_layout.addWidget(add_to_csv_button)
            buttons_layout.addWidget(load_csv_button)  # Add Load CSV button to layout
            buttons_layout.addWidget(save_csv_button)
            buttons_layout.addWidget(preview_csv_button)
            buttons_layout.addWidget(clear_fields_button)
            buttons_layout.addWidget(start_over_button)
            self.main_layout.addLayout(buttons_layout)
            self.scroll_layout.setSpacing(5)
            self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        except Exception as e:
            print(f"Error initializing UI in SplitDialog: {e}")

    def load_csv(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_name:
                self.temp_csv_file = CSV_Loader.load_and_verify_csv(file_name)  # Load and verify CSV, update temp CSV file
                self.status_label.setText('<span style="color: green;">CSV loaded successfully.</span>')
        except Exception as e:
            self.status_label.setText(f'<span style="color: red;">Error loading CSV: {e}</span>')
            print(f"Error loading CSV: {e}")

    def open_c40_list_dialog(self):
        try:
            dialog = ListDialog("C40 List", existing_list=self.c40_list)
            if dialog.exec_():
                self.c40_list = dialog.list_data
        except Exception as e:
            print(f"Error opening C40 list dialog: {e}")

    def open_master_sn_list_dialog(self):
        try:
            dialog = ListDialog("Master SN List", existing_list=self.master_sn_list)
            if dialog.exec_():
                self.master_sn_list = dialog.list_data
        except Exception as e:
            print(f"Error opening master SN list dialog: {e}")

    def prompt_child_sns(self):
        try:
            num_sns, ok = QInputDialog.getInt(self, 'Input', 'How many child parts lines have SNs?')
            if ok:
                self.add_child_sns(num_sns)
        except Exception as e:
            print(f"Error prompting for child SNs: {e}")

    def add_child_sns(self, num_sns):
        try:
            for i in range(self.child_parts_layout.count()):
                child_part_layout = self.child_parts_layout.itemAt(i).layout()
                for j in reversed(range(child_part_layout.count())):
                    widget = child_part_layout.itemAt(j).widget()
                    if isinstance(widget, QPushButton) and widget.text() == 'SNs':
                        widget.deleteLater()
            self.child_sn_list = [None] * self.child_part_counter
            for i in range(min(num_sns, self.child_part_counter)):
                self.child_sn_list[i] = []
                child_part_layout = self.child_parts_layout.itemAt(i).layout()
                sn_button = QPushButton('SNs', self)
                sn_button.clicked.connect(lambda _, idx=i: self.open_child_sn_list_dialog(idx))
                child_part_layout.addWidget(sn_button)
        except Exception as e:
            print(f"Error adding child SNs: {e}")

    def open_child_sn_list_dialog(self, index):
        try:
            dialog = ListDialog(f"Child Part {index+1} SN List", existing_list=self.child_sn_list[index])
            if dialog.exec_():
                self.child_sn_list[index] = dialog.list_data
        except Exception as e:
            print(f"Error opening child SN list dialog: {e}")

    def toggle_part_number(self, state):
        try:
            visible = state == Qt.Checked
            self.master_part_label.setVisible(visible)
            self.master_part_textbox.setVisible(visible)
            self.master_sn_list_button.setVisible(visible)
        except Exception as e:
            print(f"Error toggling part number visibility: {e}")

    def add_child_part(self):
        try:
            self.child_part_counter += 1
            self.child_sn_list.append(None)
            child_part_layout = QHBoxLayout()
            child_part_label = QLabel(f'Child Part {self.child_part_counter}:', self)
            child_part_textbox = QLineEdit(self)
            qty_label = QLabel('QTY:', self)
            qty_textbox = QLineEdit(self)
            qty_textbox.setFixedWidth(50)
            child_part_layout.addWidget(child_part_label)
            child_part_layout.addWidget(child_part_textbox)
            child_part_layout.addWidget(qty_label)
            child_part_layout.addWidget(qty_textbox)
            self.child_parts_layout.addLayout(child_part_layout)
        except Exception as e:
            print(f"Error adding child part: {e}")

    def remove_child_part(self):
        try:
            if self.child_part_counter > 0:
                self.child_sn_list.pop()
                item = self.child_parts_layout.takeAt(self.child_part_counter - 1)
                if item:
                    while item.layout().count():
                        widget = item.layout().takeAt(0).widget()
                        if widget:
                            widget.deleteLater()
                    self.child_part_counter -= 1
        except Exception as e:
            print(f"Error removing child part: {e}")

    def enable_lpn_editing(self):
        try:
            self.lpn_changed = True  # Set flag to indicate LPN has been changed
            self.from_lpn_textbox.setReadOnly(False)
            self.from_lpn_textbox.setFocus()
        except Exception as e:
            print(f"Error enabling LPN editing: {e}")

    def append_uparrow(self):
        try:
            with open(self.temp_csv_file.name, 'a', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow([self.row_counter, "UPARROW", "UPARROW", "", ""])
                self.row_counter += 1
        except Exception as e:
            print(f"Error appending UPARROW: {e}")

    def on_next_build(self):
        try:
            num_builds = int(self.question3_textbox.text())
            if len(self.c40_list) != num_builds or (self.question1_checkbox.isChecked() and len(self.master_sn_list) != num_builds):
                self.status_label.setText('<span style="color: red;">C40, SN, and/or build quantity do not match.</span>')
                return
            for i in range(len(self.child_sn_list)):
                if self.child_sn_list[i] is not None:
                    qty = int(self.child_parts_layout.itemAt(i).layout().itemAt(3).widget().text())
                    expected_sns_count = qty * num_builds
                    if len(self.child_sn_list[i]) != expected_sns_count:
                        self.status_label.setText(f'<span style="color: red;">Child Part {i+1} SNs quantity does not match the expected count of {expected_sns_count}.</span>')
                        return
            if not self.from_lpn_textbox.text().strip() or (self.question1_checkbox.isChecked() and not self.master_part_textbox.text().strip()):
                self.status_label.setText('<span style="color: red;">Missing Data!</span>')
                return
            for j in range(self.child_parts_layout.count()):
                child_part_layout = self.child_parts_layout.itemAt(j).layout()
                if not child_part_layout.itemAt(1).widget().text().strip() or not child_part_layout.itemAt(3).widget().text().strip():
                    self.status_label.setText('<span style="color: red;">Missing Data!</span>')
                    return
            if self.lpn_changed:
                self.append_uparrow()  # Add an additional UPARROW before the From LPN prompt
                self.lpn_changed = False  # Reset flag after adding UPARROW
            self.row_counter = CSV_Writer.append_to_csv(self.temp_csv_file, self.row_counter, self.c40_list, self.master_sn_list, self.child_sn_list, self.from_lpn_textbox, self.master_part_textbox, self.question1_checkbox, self.child_parts_layout, num_builds)
            self.total_builds += num_builds  # Update total builds counter
            self.status_label.setText('<span style="color: green;">{} New builds added to CSV. Total builds: {}</span>'.format(num_builds, self.total_builds))
            self.counter_label.setText('Total Builds: {}'.format(self.total_builds))  # Update counter label
            self.from_lpn_textbox.setReadOnly(True)
            self.show_change_button()
            self.clear_data_fields_except_lpn_and_status()
        except ValueError:
            self.status_label.setText('<span style="color: red;">Invalid number entered.</span>')
        except Exception as e:
            print(f"Error on next build: {e}")

    def clear_data_fields_except_lpn_and_status(self):
        try:
            self.question1_checkbox.setChecked(False)
            self.master_part_textbox.clear()
            while self.child_part_counter > 0:
                self.remove_child_part()
            self.question3_textbox.clear()
            self.c40_list = []
            self.master_sn_list = []
        except Exception as e:
            print(f"Error clearing data fields except LPN and status: {e}")

    def show_change_button(self):
        try:
            if hasattr(self, 'change_lpn_button'):
                self.change_lpn_button.setParent(None)
            self.change_lpn_button = QPushButton('Change', self)
            self.change_lpn_button.clicked.connect(self.enable_lpn_editing)
            self.from_lpn_layout.addWidget(self.change_lpn_button)
        except Exception as e:
            print(f"Error showing change button: {e}")

    def clear_layout(self, layout):
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except Exception as e:
            print(f"Error clearing layout: {e}")

    def clear_data_fields(self):
        try:
            self.from_lpn_textbox.clear()
            self.question1_checkbox.setChecked(False)
            self.master_part_textbox.clear()
            while self.child_part_counter > 0:
                self.remove_child_part()
            self.question3_textbox.clear()
            self.status_label.clear()
        except Exception as e:
            print(f"Error clearing data fields: {e}")

    def start_over(self):
        try:
            reply = QMessageBox.question(self, 'Warning', 'This will delete all unsaved CSV data and will start over. Do you want to proceed?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.clear_data_fields()
                self.close()
                new_dialog = SplitDialog()
                new_dialog.exec_()
        except Exception as e:
            print(f"Error starting over: {e}")

    def preview_csv(self):
        try:
            csv_data = CSV_Writer.read_csv(self.temp_csv_file)
            dialog = QDialog(self)
            dialog.setWindowTitle('Preview CSV')
            dialog.setFixedSize(600, 400)
            layout = QVBoxLayout(dialog)
            table = QTableWidget(dialog)
            table.setRowCount(len(csv_data))
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["PROMPT", "KEY", "DATA"])
            for row_idx, row_data in enumerate(csv_data): # Start from row 0 to include headers
                for col_idx, col_data in enumerate(row_data[1:4]):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(col_data))
            layout.addWidget(table)
            ok_button = QPushButton('OK', dialog)
            ok_button.clicked.connect(dialog.accept)
            layout.addWidget(ok_button)
            dialog.exec_()
        except Exception as e:
            print(f"Error previewing CSV: {e}")

    def on_finish_csv(self):
        try:
            CSV_Writer.append_finished(self.temp_csv_file, self.row_counter)
            self.row_counter += 1
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV As", "", "CSV (MS-DOS) (*.csv);;All Files (*)", options=options)
            if file_name:
                if not file_name.endswith('.csv'):
                    file_name += '.csv'
                CSV_Writer.save_csv(file_name, self.temp_csv_file, self.csv_headers)
                
                # Prompt the user with the dialog after saving
                msg_box = QMessageBox()
                msg_box.setWindowTitle('CSV Saved')
                msg_box.setText('Would you like to start a new CSV or continue adding to the existing one?')
                new_csv_button = msg_box.addButton('New CSV', QMessageBox.ActionRole)
                continue_button = msg_box.addButton('Continue', QMessageBox.ActionRole)
                msg_box.exec_()
                
                if msg_box.clickedButton() == new_csv_button:
                    self.clear_data_fields()
                    self.close()
                    new_dialog = SplitDialog()
                    new_dialog.exec_()
                elif msg_box.clickedButton() == continue_button:
                    # Remove the "FINISHED" row
                    with open(self.temp_csv_file.name, 'r') as file:
                        lines = file.readlines()
                    with open(self.temp_csv_file.name, 'w') as file:
                        for line in lines:
                            if "FINISHED" not in line:
                                file.write(line)
        except Exception as e:
            print(f"Error finishing CSV: {e}")