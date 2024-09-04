from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from .CodeBlock import *


class Step(QWidget):
    def __init__(self, parent=None, with_placeholder=True):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setAcceptDrops(True)
        self.block = None
        self._parent = parent

        if with_placeholder:
            self.placeholder = QLabel("Drop block here")
            self.placeholder.setStyleSheet(
                "background-color: #e0e0e0; border: 1px dashed #a0a0a0; border-radius: 5px;")
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
        self._parent.block_tab.add_step()

    def add_block(self, module_and_block):
        module_name, block_name = module_and_block.split(':')
        if self.block:
            self.layout.removeWidget(self.block)
            self.block.deleteLater()
        if self.placeholder:
            self.layout.removeWidget(self.placeholder)
            self.placeholder.deleteLater()
            self.placeholder = None
        self.block = CodeBlock(
            block_name, BLOCKS[module_name][block_name], module_name)
        self.layout.addWidget(self.block)


class StepContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()  # Change back to QVBoxLayout
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
