from PyQt5 import QtWidgets
import json
import os  # Import os as it's used in the code

from .CodeBlock import *
from .Logging import *
from .Step import *
import asyncio


class BlockTab:
    def __init__(self, parent=None):
        self.parent = parent
        self.containers = []
        self.refresh_testcase_list()

    def setup_block_tab(self):
        for module_name, module_blocks in BLOCKS.items():
            group_box = QtWidgets.QGroupBox(module_name)
            group_layout = QtWidgets.QVBoxLayout()
            for block_name, function in module_blocks.items():
                block = CodeBlock(block_name, function, module_name)
                group_layout.addWidget(block)
            group_box.setLayout(group_layout)
            self.parent.block_layout.addWidget(group_box)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        self.containers_layout = QtWidgets.QHBoxLayout(scroll_widget)  # Change to QHBoxLayout
        scroll_area.setWidget(scroll_widget)
        self.parent.block_edit_area.setWidget(scroll_area)

        self.add_test_case()  # Add the first container

    def refresh_testcase_list(self):
        self.parent.testcase_list.clear()
        testcases = [file[:-5].capitalize().replace("_", " ")
                     for file in os.listdir('testcases') if file.endswith('.json')]
        self.parent.testcase_list.addItems(testcases)

    def add_step(self, container=None, with_placeholder=True):
        if container is None:
            container = self.containers[-1] if self.containers else self.add_test_case()
        step = Step(parent=self.parent, container=container, with_placeholder=with_placeholder)
        container.layout.addWidget(step)
        container.update()

    def clear_steps(self):
        for container in self.containers:
            container.deleteLater()
        self.containers.clear()
        self.containers_layout.update()
        logging.info("Cleared all test cases and steps")
        self.add_test_case()  # Add a new empty container after clearing

    def remove_code(self):
        testcase_name = self.parent.testcase_list.currentText().lower().replace(" ", "_")
        file_path = os.path.join("testcases", f"{testcase_name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File {file_path} has been deleted")
            self.refresh_testcase_list()
        else:
            logging.info(f"File {file_path} does not exist")

    def export_code(self):
        test_case_name, ok = QtWidgets.QInputDialog.getText(
            self.parent, "Input Test Name", "Enter your testcase name:"
        )
        if not ok or not test_case_name:
            logging.warning(
                "Export Error. Please enter a valid test case name.")
            return

        export_data = {
            "containers": [
                {
                    "steps": [
                        {"module": step.block.module_name, "block": step.block.block_name}
                        for step in container.findChildren(Step) if step.block
                    ]
                }
                for container in self.containers
            ]
        }

        file_path = self.save_test_case(
            test_case_name.replace(" ", "_").lower(), export_data)
        if file_path:
            logging.info(f"Code exported to {file_path}")
            self.refresh_testcase_list()

    def save_test_case(self, test_case_name, export_data):
        os.makedirs("testcases", exist_ok=True)
        file_path = os.path.join("testcases", f"{test_case_name}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)
            return file_path
        except IOError as e:
            logging.error(f"Error saving test case: {e}")
            return None

    def import_code(self):
        testcase_name = self.parent.testcase_list.currentText().lower()
        file_path = os.path.join("testcases", f"{testcase_name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    import_data = json.load(f)
                self.load_test_case(file_path, import_data)
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Error importing test case: {e}")
        else:
            logging.error(f"File not found: {file_path}")

    def load_test_case(self, file_path, import_data):
        self.clear_steps()  # This will now clear all containers and add a new empty one
        test_case_name = os.path.splitext(os.path.basename(file_path))[0]
        self.test_case_name_input = QLabel(test_case_name)

        # Remove the first empty container that was added by clear_steps
        if self.containers:
            self.containers[0].deleteLater()
            self.containers.pop(0)

        for container_data in import_data.get("containers", []):
            new_container = self.add_test_case()
            first_step = True
            for step_data in container_data.get("steps", []):
                module_name = step_data.get("module")
                block_name = step_data.get("block")
                if module_name in BLOCKS and block_name in BLOCKS[module_name]:
                    if first_step:
                        # Replace the placeholder in the first step
                        first_step_widget = new_container.layout.itemAt(0).widget()
                        first_step_widget.add_block(f"{module_name}:{block_name}")
                        first_step = False
                    else:
                        step = Step(with_placeholder=False, parent=self.parent, container=new_container)
                        new_container.layout.addWidget(step)
                        step.add_block(f"{module_name}:{block_name}")
                else:
                    logging.warning(f"Block '{block_name}' from module '{module_name}' not found.")

            new_container.update()

        logging.info(f"Code imported from {file_path}")

    async def run_code(self):
        try:
            for container_index, container in enumerate(self.containers, 1):
                logging.info(f"Running Test Case {container_index}")
                for step_index, step in enumerate(container.findChildren(Step), 1):
                    if step.block:
                        try:
                            logging.info(f"Executing step {step_index}: {step.block.block_name}")
                            result = await step.block.function(*step.block.function_inputs)

                            if result:
                                step.set_color("lightgreen")
                                logging.info(f"Step {step_index}: {step.block.block_name} executed successfully")
                            else:
                                step.set_color("lightcoral")
                                logging.critical(f"Error executing step {step_index} ({step.block.block_name}) with: {result}")
                                break  # Stop executing this container if a step fails

                        except Exception as e:
                            logging.error(f"Exception occurred during step {step_index}: {e}")
                            step.set_color("lightcoral")
                            break  # Stop executing this container if an exception occurs

                logging.info(f"Finished Test Case {container_index}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def add_test_case(self):
        new_container = StepContainer(parent=self.parent)
        new_container.setMaximumWidth(200)  # Set a maximum width for each container
        new_container.setMinimumHeight(300)  # Set a minimum height for each container
        self.containers.append(new_container)
        self.containers_layout.addWidget(new_container)
        self.containers_layout.setSpacing(10)  # Add spacing between containers
        self.add_step(new_container)
        logging.info("New test case container added")
        return new_container