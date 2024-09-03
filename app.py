import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QMimeData, QRect, QSize, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDrag, QPainter, QPen, QBrush, QPolygonF
import json
import importlib
import logging
import math
from PyQt5.QtWidgets import QTextEdit, QSplitter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import all block modules
block_modules = {}
for file in os.listdir('blocks'):
    if file.endswith('.py') and file != '__init__.py':
        module_name = file[:-3]
        block_modules[module_name] = importlib.import_module(f'blocks.{module_name}')

# Collect all blocks from different modules
BLOCKS = {}
for module_name, module in block_modules.items():
    if hasattr(module, 'BLOCKS'):
        BLOCKS[module_name] = module.BLOCKS

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = 5  # Fixed spacing of 20 pixels

        for item in self.itemList:
            nextX = x + item.sizeHint().width() + spacing
            if nextX - spacing > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spacing
                nextX = x + item.sizeHint().width() + spacing
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

class CodeBlock(QtWidgets.QPushButton):
    def __init__(self, text, function, module_name, parent=None):
        super().__init__(text, parent)
        self.block_name = text  # Store the block name as a separate attribute
        self.function = function
        self.module_name = module_name
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #c0c0c0; border-radius: 5px;")
        self.setFixedSize(150, 40)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.module_name}:{self.block_name}")  # Use block_name instead of text()
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)

class Step(QtWidgets.QWidget):
    def __init__(self, parent=None, with_placeholder=True):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.setAcceptDrops(True)
        self.block = None

        if with_placeholder:
            self.placeholder = QtWidgets.QLabel("Drop block here")
            self.placeholder.setStyleSheet("background-color: #e0e0e0; border: 1px dashed #a0a0a0; border-radius: 5px;")
            self.placeholder.setAlignment(Qt.AlignCenter)
            self.placeholder.setFixedSize(150, 40)
            self.layout.addWidget(self.placeholder)
        else:
            self.placeholder = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        module_and_block = event.mimeData().text()
        self.add_block(module_and_block)
        event.acceptProposedAction()
        # Find the TunableClone instance and call add_step
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, AutomationGUI):
                parent.add_step()
                break
            parent = parent.parent()

    def add_block(self, module_and_block):
        module_name, block_name = module_and_block.split(':')
        if self.block:
            self.layout.removeWidget(self.block)
            self.block.deleteLater()
        if self.placeholder:
            self.layout.removeWidget(self.placeholder)
            self.placeholder.deleteLater()
            self.placeholder = None
        self.block = CodeBlock(block_name, BLOCKS[module_name][block_name], module_name)
        self.layout.addWidget(self.block)

class StepContainer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()  # Change back to QVBoxLayout
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.gray, 2, Qt.SolidLine)
        painter.setPen(pen)

        for i in range(self.layout.count() - 1):
            widget1 = self.layout.itemAt(i).widget()
            widget2 = self.layout.itemAt(i + 1).widget()

            start = widget1.mapTo(self, widget1.rect().center())
            end = widget2.mapTo(self, widget2.rect().center())

            painter.drawLine(start, end)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()  # Ensure lines are redrawn when the container is resized

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class AutomationGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/main.ui', self)

        # Create a tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create tabs
        self.block_tab = QtWidgets.QWidget()
        self.config_tab = QtWidgets.QWidget()
        self.report_tab = QtWidgets.QWidget()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.block_tab, "Blocks")
        self.tab_widget.addTab(self.config_tab, "Configuration")
        self.tab_widget.addTab(self.report_tab, "Report")

        # Set up the block tab
        self.setup_block_tab()

        # Set up the configuration tab
        self.setup_config_tab()

        # Set up the report tab
        self.setup_report_tab()

        # Set up logging to the console
        self.setup_logging()

    def setup_logging(self):
        log_handler = QTextEditLogger(self.console)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)

    def setup_block_tab(self):
        layout = QtWidgets.QVBoxLayout(self.block_tab)

        # Create a splitter for the main layout
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Create a widget for the left side (existing content)
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        # Top: Available blocks (1/3 of the height)
        top_widget = QtWidgets.QWidget()
        top_layout = QtWidgets.QVBoxLayout(top_widget)
        top_widget.setLayout(top_layout)

        top_layout.addWidget(QtWidgets.QLabel("Available Blocks:"))

        blocks_layout = QtWidgets.QHBoxLayout()
        for module_name, module_blocks in BLOCKS.items():
            group_box = QtWidgets.QGroupBox(module_name)
            group_layout = QtWidgets.QVBoxLayout()
            for block_name, function in module_blocks.items():
                block = CodeBlock(block_name, function, module_name)
                group_layout.addWidget(block)
            group_box.setLayout(group_layout)
            blocks_layout.addWidget(group_box)

        blocks_widget = QtWidgets.QWidget()
        blocks_widget.setLayout(blocks_layout)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(blocks_widget)
        top_layout.addWidget(scroll_area)

        # Bottom: Steps and Test Case Name
        bottom_widget = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QVBoxLayout(bottom_widget)

        # Add Test Case Name input
        test_case_layout = QtWidgets.QHBoxLayout()
        test_case_layout.addWidget(QtWidgets.QLabel("Test Case Name:"))
        self.test_case_name_input = QtWidgets.QLineEdit()
        test_case_layout.addWidget(self.test_case_name_input)
        bottom_layout.addLayout(test_case_layout)

        self.steps_container = StepContainer()
        self.steps_layout = self.steps_container.layout

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.steps_container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        bottom_layout.addWidget(scroll_area)

        button_layout = QtWidgets.QHBoxLayout()
        export_button = QtWidgets.QPushButton("Export")
        export_button.clicked.connect(self.export_code)
        button_layout.addWidget(export_button)

        import_button = QtWidgets.QPushButton("Import")
        import_button.clicked.connect(self.import_code)
        button_layout.addWidget(import_button)

        run_button = QtWidgets.QPushButton("Run")
        run_button.clicked.connect(self.run_code)
        button_layout.addWidget(run_button)

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self.clear_steps)
        button_layout.addWidget(clear_button)

        bottom_layout.addLayout(button_layout)

        left_layout.addWidget(top_widget)
        left_layout.addWidget(bottom_widget, 2)

        # Add the left widget to the splitter
        splitter.addWidget(left_widget)

        # Create and add the console widget to the splitter
        self.console = QTextEdit()
        splitter.addWidget(self.console)

        self.steps = []
        self.add_step()  # Add initial step

    def setup_config_tab(self):
        layout = QtWidgets.QVBoxLayout(self.config_tab)
        layout.addWidget(QtWidgets.QLabel("Configuration Tab"))
        # Add configuration widgets here

    def setup_report_tab(self):
        layout = QtWidgets.QVBoxLayout(self.report_tab)
        layout.addWidget(QtWidgets.QLabel("Report Tab"))
        # Add report widgets here

    def add_step(self, with_placeholder=True):
        step = Step(with_placeholder=with_placeholder)
        self.steps.append(step)
        self.steps_layout.addWidget(step)
        self.steps_container.update()

    def clear_steps(self):
        for step in self.steps:
            self.steps_layout.removeWidget(step)
            step.deleteLater()
        self.steps.clear()
        self.add_step()  # Add initial step
        self.steps_container.update()

    def export_code(self):
        test_case_name = self.test_case_name_input.text().strip()
        if not test_case_name:
            QtWidgets.QMessageBox.warning(self, "Export Error", "Please enter a test case name.")
            return

        export_data = {"step": {i: {"module": step.block.module_name, "block": step.block.block_name} 
                                for i, step in enumerate(self.steps, start=1) if step.block}}

        file_path = self.save_test_case(test_case_name, export_data)
        if file_path:
            logging.info(f"Code exported to {file_path}")
            QtWidgets.QMessageBox.information(self, "Export Successful", f"Test case exported to {file_path}")

    def save_test_case(self, test_case_name, export_data):
        os.makedirs("testcase", exist_ok=True)
        file_path = os.path.join("testcase", f"{test_case_name}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)
            return file_path
        except IOError as e:
            logging.error(f"Error saving test case: {e}")
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to save test case: {e}")
            return None

    def import_code(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Test Case", "testcase", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    import_data = json.load(f)
                self.load_test_case(file_path, import_data)
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Error importing test case: {e}")
                QtWidgets.QMessageBox.critical(self, "Import Error", f"Failed to import test case: {e}")

    def load_test_case(self, file_path, import_data):
        self.clear_steps()
        test_case_name = os.path.splitext(os.path.basename(file_path))[0]
        self.test_case_name_input.setText(test_case_name)

        first_step = True
        for _, step_data in import_data["step"].items():
            module_name = step_data.get("module")
            block_name = step_data.get("block")
            if module_name in BLOCKS and block_name in BLOCKS[module_name]:
                if first_step:
                    # Replace the placeholder with the first step
                    self.steps[0].add_block(f"{module_name}:{block_name}")
                    first_step = False
                else:
                    self.add_step(with_placeholder=False)
                    self.steps[-1].add_block(f"{module_name}:{block_name}")
            else:
                logging.warning(f"Block '{block_name}' from module '{module_name}' not found in available blocks.")

        self.steps_container.update()
        logging.info(f"Code imported from {file_path}")

    def run_code(self):
        for i, step in enumerate(self.steps, 1):
            if step.block:
                try:
                    logging.info(f"Executing step {i}: {step.block.block_name}")
                    step.block.function()
                except Exception as e:
                    error_msg = f"Error executing step {i} ({step.block.block_name}): {e}"
                    logging.error(error_msg)
                    QtWidgets.QMessageBox.critical(self, "Execution Error", error_msg)
                    break
        else:
            logging.info("All steps executed successfully")
            QtWidgets.QMessageBox.information(self, "Execution Complete", "All steps executed successfully.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AutomationGUI()
    window.show()
    sys.exit(app.exec_())
