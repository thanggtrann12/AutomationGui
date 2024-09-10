from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QApplication, QLineEdit
from PyQt5.QtCore import Qt
from .CodeBlock import *


class Step(QWidget):
    def __init__(self, parent=None, container=None, with_placeholder=True):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setAcceptDrops(True)
        self.block = None
        self._parent = parent
        self.container = container

        if with_placeholder:
            self.placeholder = QLabel("Drop block here")
            self.placeholder.setStyleSheet(
                "background-color: #e0e0e0; border: 1px dashed #a0a0a0; border-radius: 5px;")
            self.placeholder.setAlignment(Qt.AlignLeft)
            self.placeholder.setFixedHeight(30)
            self.layout.addWidget(self.placeholder)
        else:
            self.placeholder = None

    def set_color(self, color: str):
        """Set background color of the step."""
        self.block.setStyleSheet(f"background-color: {color};")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        source = event.source()
        if isinstance(source, CodeBlock) or (source is None and event.mimeData().hasText()):
            # New block being dropped
            module_and_block = event.mimeData().text()
            self.add_block(module_and_block)
            event.acceptProposedAction()
            if self.container:
                self._parent.block_tab.add_step(self.container)
        elif source != self and isinstance(source, Step):
            # Existing step being moved
            source_container = source.container
            target_container = self.container

            target_index = target_container.layout.indexOf(self)

            if source_container == target_container:
                # Move within the same container
                source_container.layout.insertWidget(target_index, source)
            else:
                # Move between containers
                source_container.layout.removeWidget(source)
                target_container.layout.insertWidget(target_index, source)
                source.container = target_container

        event.acceptProposedAction()

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
            block_name, get_all_blocks()[module_name][block_name], module_name)
        self.layout.addWidget(self.block)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"{self.block.module_name}:{self.block.block_name}")
        drag.setMimeData(mime_data)

        drag.exec_(Qt.MoveAction)


class StepContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.setAcceptDrops(True)
        self.name_input = QLineEdit("New Test Case")
        self.name_input.setAlignment(Qt.AlignCenter)
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(
            "background-color: #e0e0e0; border: 1px dashed #a0a0a0; border-radius: 5px; font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.name_input)

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if isinstance(source, CodeBlock) or (source is None and event.mimeData().hasText()):
            # New block being dropped into container
            new_step = Step(parent=self.parent(), container=self)
            self.layout.addWidget(new_step)
            new_step.dropEvent(event)
        elif isinstance(source, Step):
            source_container = source.container
            if source_container != self:
                # Move between containers
                source_container.layout.removeWidget(source)
                self.layout.addWidget(source)
                source.container = self
            else:
                # Move to the end of the same container
                self.layout.removeWidget(source)
                self.layout.addWidget(source)
        event.acceptProposedAction()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
