from PyQt5.QtWidgets import QPushButton, QMainWindow, QTextEdit, QComboBox, QApplication, QMessageBox, QScrollArea, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QEventLoop
from PyQt5 import uic
import asyncio
import sys
from asyncqt import QEventLoop
import logging
# import from scr
from src.Logging import *
from src.BlockTab import BlockTab
# end


class AutomationGUI(QMainWindow):
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
        self.reload_btn = self.findChild(QPushButton, "reload_btn")

        self.console = self.findChild(QTextEdit, "log_console")
        self.testcase_list = self.findChild(QComboBox, "testcase_list")
        self.block_tab.setup_block_tab()

        self.export_btn.clicked.connect(self.block_tab.export_code)
        self.import_btn.clicked.connect(self.block_tab.import_code)
        self.remove_btn.clicked.connect(self.block_tab.remove_code)
        self.run_btn.clicked.connect(self.wrap_async(self.block_tab.run_code))
        self.reload_btn.clicked.connect(self.reload_window)
        self.clear_btn.clicked.connect(self.block_tab.clear_steps)
        self.test_case_name_input = QLineEdit()
        self.block_layout = self.findChild(
            QHBoxLayout, "block_layout")
        self.block_edit_area = self.findChild(
            QScrollArea, "block_edit_area")
        self.add_test_case_btn = self.findChild(
            QPushButton, "add_test_case_btn")
        self.add_test_case_btn.clicked.connect(self.block_tab.add_test_case)

    def reload_window(self):
        self.close()
        self.__init__()
        self.show()

    def wrap_async(self, coro):
        return lambda: asyncio.create_task(coro())

    def closeEvent(self, event):
        """Handle the close event of the window."""
        reply = QMessageBox.question(self, 'Exit Confirmation',
                                     'Are you sure you want to exit?',
                                     QMessageBox.Yes |
                                     QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            #     import psutil
            #     terminated = False
            #     logging.info("Cleaning up before exit...")
            #     name = "csm.exe"
            #     for proc in psutil.process_iter(['pid', 'name']):
            #         if proc.info['name'].lower() == name.lower():
            #             try:
            #                 proc.terminate()
            #                 proc.wait(timeout=3)
            #                 logging.info(
            #                     f"Terminated process {proc.info['name']} with PID {proc.info['pid']}")
            #                 terminated = True
            #             except psutil.NoSuchProcess:
            #                 logging.critical(
            #                     f"Process {proc.info['name']} with PID {proc.info['pid']} does not exist")
            #             except psutil.AccessDenied:
            #                 logging.critical(
            #                     f"Access denied to terminate process {proc.info['name']} with PID {proc.info['pid']}")
            #             except psutil.TimeoutExpired:
            #                 logging.critical(
            #                     f"Timeout expired while waiting for process {proc.info['name']} with PID {proc.info['pid']} to terminate")

            #     if not terminated:
            #         logging.info(f"No process found with the name {name}")

            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationGUI()
    window.show()

    # Run the PyQt5 event loop and asyncio event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        # Start the PyQt5 event loop
        loop.run_forever()
