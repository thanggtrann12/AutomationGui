from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QPushButton, QInputDialog, QFileDialog
import os
import importlib
import inspect


def get_all_blocks(directory='blocks'):
    block_modules = {}

    # Import all block modules
    for file in os.listdir(directory):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]
            block_modules[module_name] = importlib.import_module(
                f'{directory}.{module_name}')

    # Collect BLOCKS from each module
    blocks = {
        module_name: getattr(module, 'BLOCKS', {})
        for module_name, module in block_modules.items()
    }

    return blocks


class CodeBlock(QPushButton):
    def __init__(self, text, function, module_name, parent=None):
        super().__init__(text, parent)
        self.block_name = text
        self.function = function
        self.module_name = module_name
        self.function_inputs = []
        self.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #c0c0c0; border-radius: 5px;")
        self.setFixedSize(150, 40)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.module_name}:{self.block_name}")
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def mouseDoubleClickEvent(self, e):
        import re
        if e.button() == Qt.LeftButton and type(self).__name__ == "CodeBlock":
            if self.prepare_input():
                text = re.findall(r'\((.*?)\)', self.block_name)

                new_block_name = self.block_name
                for item in text:
                    new_block_name = new_block_name.replace(
                        f'({item})', f'({str(self.function_inputs)})')

                self.block_name = new_block_name
                self.setText(new_block_name)

    def requires_input(self):
        signature = inspect.signature(self.function)
        return len(signature.parameters) > 0

    def prepare_input(self) -> bool:
        if self.requires_input():
            inputs = []
            signature = inspect.signature(self.function)

            for param in signature.parameters:
                # Check if the parameter might represent a file or directory path
                if "path" in param or "file" in param:
                    file_path = QFileDialog.getOpenFileName(
                        self, 'Select File', '', '*.pro')[0]
                    if file_path:
                        inputs.append(file_path)
                    else:
                        return False  # User canceled the dialog
                else:
                    value, ok = QInputDialog.getText(
                        self, 'Input', f'Enter value for {param}:')
                    if ok:
                        # Handle as an integer input, modify as needed
                        inputs.append(int(value))

            self.function_inputs = inputs
            return True
        else:
            self.function_inputs = []
            return False
