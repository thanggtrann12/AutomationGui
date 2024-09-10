from PyQt5 import QtWidgets
import json
import os
import logging
import io

from blocks.TTFislog import clear_log, save_log, get_log
from .CodeBlock import *
from .Logging import *
from .Step import *


class CaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = io.StringIO()

    def emit(self, record):
        self.logs.write(self.format(record) + '\n')

    def get_logs(self):
        return self.logs.getvalue()


class BlockTab:
    def __init__(self, parent=None):
        self.parent = parent
        self.containers = []
        self.loaded_test = ""
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
        self.containers_layout = QtWidgets.QHBoxLayout(
            scroll_widget)  # Change to QHBoxLayout
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
        step = Step(parent=self.parent, container=container,
                    with_placeholder=with_placeholder)
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
                    "name": container.name_input.text(),
                    "steps": [
                        {"module": step.block.module_name,
                            "block": step.block.block_name}
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
        self.clear_steps()
        test_case_name = os.path.splitext(os.path.basename(file_path))[0]
        self.test_case_name_input = QLabel(test_case_name)

        # Remove the first empty container that was added by clear_steps
        if self.containers:
            self.containers[0].deleteLater()
            self.containers.pop(0)

        for container_data in import_data.get("containers", []):
            new_container = self.add_test_case()
            new_container.name_input.setText(
                container_data.get("name", "Unnamed Test Case"))
            first_step = True
            for step_data in container_data.get("steps", []):
                module_name = step_data.get("module")
                block_name = step_data.get("block")
                if module_name in BLOCKS and block_name in BLOCKS[module_name]:
                    if first_step:
                        # Replace the placeholder in the first step
                        first_step_widget = new_container.layout.itemAt(
                            1).widget()  # Changed from 0 to 1
                        first_step_widget.add_block(
                            f"{module_name}:{block_name}")
                        first_step = False
                    else:
                        step = Step(with_placeholder=False,
                                    parent=self.parent, container=new_container)
                        new_container.layout.addWidget(step)
                        step.add_block(f"{module_name}:{block_name}")
                else:
                    logging.warning(
                        f"Block '{block_name}' from module '{module_name}' not found.")

            new_container.update()
        self.loaded_test = file_path
        logging.info(f"Code imported from {file_path}")

    async def run_code(self):
        test_results = {}
        await clear_log()
        try:
            for container_index, container in enumerate(self.containers, 1):
                container_name = container.name_input.text()
                container_results = {}
                logging.info(f"Running Test Case: {container_name}")
                for step_index, step in enumerate(container.findChildren(Step), 1):
                    if step.block:
                        try:
                            logging.info(
                                f"Executing step {step_index}: {step.block.block_name}")

                            # Set up capture handler
                            capture_handler = CaptureHandler()
                            capture_handler.setFormatter(logging.Formatter(
                                '%(asctime)s - %(levelname)s - %(message)s'))
                            logging.getLogger().addHandler(capture_handler)

                            # Execute the function
                            result = await step.block.function(*step.block.function_inputs)
                            aurix_log = get_log()
                            # Get captured logs
                            step_logs = capture_handler.get_logs()
                            logging.getLogger().removeHandler(capture_handler)

                            success = result is not False
                            log_message = f"Step {step_index}: {step.block.block_name} executed successfully" if success else f"Error executing step {step_index} ({step.block.block_name}) with: {result}"

                            container_results[f"Step {step_index}"] = {
                                'success': success,
                                'log': step_logs + log_message + aurix_log
                            }

                            if success:
                                step.set_color("lightgreen")
                                logging.info(log_message)
                            else:
                                step.set_color("lightcoral")
                                logging.critical(log_message)
                                break

                        except Exception as e:
                            error_message = f"Exception occurred during step {step_index}: {e}"
                            container_results[f"Step {step_index}"] = {
                                'success': False,
                                'log': error_message + aurix_log
                            }
                            logging.error(error_message)
                            step.set_color("lightcoral")
                            break

                test_results[f"Test Case {container_index}: {container_name}"] = container_results
                logging.info(f"Finished Test Case {container_index}")
                # save_log()
                # clear_log()
            import webbrowser
            import os
            file_path = os.path.abspath(
                generate_test_results_html(test_results))

            # Open the HTML file in the default web browser
            webbrowser.open(f'file://{file_path}')

        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def add_test_case(self):
        new_container = StepContainer(parent=self.parent)
        # Set a maximum width for each container
        new_container.setMaximumWidth(200)
        # Set a minimum height for each container
        new_container.setMinimumHeight(300)
        self.containers.append(new_container)
        self.containers_layout.addWidget(new_container)
        self.containers_layout.setSpacing(10)  # Add spacing between containers
        self.add_step(new_container)
        logging.info("New test case container added")
        return new_container
