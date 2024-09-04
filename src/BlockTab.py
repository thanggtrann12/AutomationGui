from PyQt5 import QtWidgets
import json
import os  # Import os as it's used in the code

from .CodeBlock import *
from .Logging import *
from .Step import *


class BlockTab:
    def __init__(self, parent=None):
        self.parent = parent
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

        self.steps_container = StepContainer(parent=self.parent)
        self.steps_layout = self.steps_container.layout
        self.parent.block_edit_area.setWidget(self.steps_container)
        self.steps = []
        self.add_step()

    def refresh_testcase_list(self):
        self.parent.testcase_list.clear()
        testcases = [file[:-5].capitalize().replace("_", " ")
                     for file in os.listdir('testcases') if file.endswith('.json')]
        self.parent.testcase_list.addItems(testcases)

    def add_step(self, with_placeholder=True):
        step = Step(with_placeholder=with_placeholder, parent=self.parent)
        self.steps.append(step)
        self.steps_layout.addWidget(step)
        self.steps_container.update()

    def clear_steps(self):
        for step in self.steps:
            self.steps_layout.removeWidget(step)
            step.deleteLater()
        self.steps.clear()
        self.add_step()
        self.steps_container.update()

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
            "step": {
                i: {"module": step.block.module_name,
                    "block": step.block.block_name}
                for i, step in enumerate(self.steps, start=1) if step.block
            }
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

        first_step = True
        for _, step_data in import_data.get("step", {}).items():
            module_name = step_data.get("module")
            block_name = step_data.get("block")
            if module_name in BLOCKS and block_name in BLOCKS[module_name]:
                if first_step:
                    self.steps[0].add_block(f"{module_name}:{block_name}")
                    first_step = False
                else:
                    self.add_step(with_placeholder=False)
                    self.steps[-1].add_block(f"{module_name}:{block_name}")
            else:
                logging.warning(
                    f"Block '{block_name}' from module '{module_name}' not found.")

        self.steps_container.update()
        logging.info(f"Code imported from {file_path}")

    def run_code(self):
        try:
            for i, step in enumerate(self.steps, 1):
                if step.block:
                    try:
                        logging.info(
                            f"Executing step {i}: {step.block.block_name}")
                        step.block.function()
                    except Exception as e:
                        logging.error(
                            f"Error executing step {i} ({step.block.block_name}): {e}")
                        break
            else:
                logging.info("All steps executed successfully")
                output_file = 'log/log_report.html'
                export_logs_to_html(output_file)
        except Exception as e:
            pass
