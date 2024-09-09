from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QPushButton, QInputDialog
import os
import importlib
import inspect

block_modules = {}
for file in os.listdir('blocks'):
    if file.endswith('.py') and file != '__init__.py':
        module_name = file[:-3]
        block_modules[module_name] = importlib.import_module(
            f'blocks.{module_name}')

# Collect all blocks from different modules
BLOCKS = {}
for module_name, module in block_modules.items():
    if hasattr(module, 'BLOCKS'):
        BLOCKS[module_name] = module.BLOCKS


class CodeBlock(QPushButton):
    def __init__(self, text, function, module_name, parent=None):
        super().__init__(text, parent)
        self.block_name = text  # Store the block name as a separate attribute
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
            drag.exec_(Qt.CopyAction)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton and type(self).__name__ is "CodeBlock":
            if self.prepare_input():
                if "time" in self.block_name:
                    new_block_name = self.block_name.replace(
                        "time", str(self.function_inputs[0]))
                    self.block_name = new_block_name
                    self.setText(new_block_name)

    def requires_input(self):
        signature = inspect.signature(self.function)
        return len(signature.parameters) > 0

    def prepare_input(self) -> bool:
        if self.requires_input():
            inputs = []
            signature = inspect.signature(self.function)

            # Prompt for each parameter
            for param in signature.parameters:
                value, ok = QInputDialog.getText(
                    self, 'Input', f'Enter value for {param}:')
                if ok:
                    inputs.append(int(value))

            self.function_inputs = inputs
            return True
        else:
            self.function_inputs = []
            return False
