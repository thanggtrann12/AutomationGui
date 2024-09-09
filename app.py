import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTextEdit, QPushButton, QComboBox
import asyncio
from asyncqt import QEventLoop

# import from scr
from src.Logging import *
from src.BlockTab import BlockTab
# end


class AutomationGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/main.ui', self)
        current_geometry = self.geometry()
        self.setGeometry(100, 30, current_geometry.width(),
                         current_geometry.height())
        self.block_tab = BlockTab(parent=self)
        self.init_ui()
        setup_logging(self)

    def init_ui(self):
        self.import_btn = self.findChild(QPushButton, "import_btn")
        self.export_btn = self.findChild(QPushButton, "export_btn")
        self.run_btn = self.findChild(QPushButton, "run_btn")
        self.clear_btn = self.findChild(QPushButton, "clear_btn")
        self.remove_btn = self.findChild(QPushButton, "remove_btn")

        self.console = self.findChild(QTextEdit, "log_console")
        self.testcase_list = self.findChild(QComboBox, "testcase_list")
        self.block_tab.setup_block_tab()

        self.export_btn.clicked.connect(self.block_tab.export_code)
        self.import_btn.clicked.connect(self.block_tab.import_code)
        self.remove_btn.clicked.connect(self.block_tab.remove_code)
        self.run_btn.clicked.connect(self.wrap_async(self.block_tab.run_code))
        self.clear_btn.clicked.connect(self.block_tab.clear_steps)
        self.test_case_name_input = QtWidgets.QLineEdit()
        self.block_layout = self.findChild(
            QtWidgets.QHBoxLayout, "block_layout")

        self.block_edit_area = self.findChild(
            QtWidgets.QScrollArea, "block_edit_area")

        self.add_test_case_btn = self.findChild(QPushButton, "add_test_case_btn")
        self.add_test_case_btn.clicked.connect(self.block_tab.add_test_case)

    def wrap_async(self, coro):
        return lambda: asyncio.create_task(coro())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AutomationGUI()
    window.show()

    # Run the PyQt5 event loop and asyncio event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        # Start the PyQt5 event loop
        loop.run_forever()
