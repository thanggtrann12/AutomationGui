from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QPushButton
import os
import importlib

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
        self.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #c0c0c0; border-radius: 5px;")
        self.setFixedSize(150, 40)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            # Use block_name instead of text()
            mime.setText(f"{self.module_name}:{self.block_name}")
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)
