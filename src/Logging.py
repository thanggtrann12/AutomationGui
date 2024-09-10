import logging
import os
import time

# List to store log entries
log_entries = []

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()
        log_entries.append((
            record.asctime,
            record.levelname,
            record.message
        ))


def setup_logging(parent):
    log_handler = QTextEditLogger(parent.console)
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(log_handler)
    logging.getLogger().setLevel(logging.INFO)


def test_results_to_html(test_results, output_file):
    """Convert test results to HTML and save to a file."""
    all_tests_success = True  # Track if all test cases pass

    # Start building the HTML content
    html_content = """
    <html>
    <head>
        <title>Test Case Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .test-case { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }
            .test-case h2 { background-color: #f4f4f4; padding: 10px; margin-top: 0; cursor: pointer; }
            .test-case h2::before { content: '+ '; }
            .test-case.open h2::before { content: '- '; }
            .steps { display: none; }
            .test-case.open .steps { display: block; }
            .step { margin-left: 20px; }
            .step h3 { margin-bottom: 5px; }
            .log { margin-left: 40px; font-family: monospace; white-space: pre-wrap; }
            .success { color: green; }
            .failure { color: red; }
        </style>
        <script>
            function toggleTestCase(element) {
                element.closest('.test-case').classList.toggle('open');
            }
        </script>
    </head>
    <body>
    """

    # Check if all test cases pass
    for test_case, steps in test_results.items():
        all_steps_success = all(step['success'] for step in steps.values())
        if not all_steps_success:
            all_tests_success = False  # If any test fails, mark overall failure

    # Final pass or fail status for the entire test suite
    final_status = "PASS" if all_tests_success else "FAIL"
    status_class = "success" if all_tests_success else "failure"
    html_content += f'<h1 class="{status_class}">Test Case Results - {final_status}</h1>'

    # Iterate through test results to generate individual test case sections
    for test_case, steps in test_results.items():
        all_steps_success = all(step['success'] for step in steps.values())
        status_class = "success" if all_steps_success else "failure"
        html_content += f'''
        <div class="test-case">
            <h2 onclick="toggleTestCase(this)" class="{status_class}">
                {test_case} - {"Success" if all_steps_success else "Failure"}
            </h2>
            <div class="steps">
        '''
        for step, result in steps.items():
            status = "success" if result['success'] else "failure"
            # Escape special characters in logs
            log_content = result['log'].replace('&', '&amp;').replace('<', '&lt;').replace(
                '>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
            html_content += f'''
            <div class="step">
                <h3>{step}</h3>
                <div class="log">{log_content}</div>
                <p class="{status}">Result: {"Success" if result['success'] else "Failure"}</p>
            </div>
            '''
        html_content += '</div></div>'

    # Close the HTML body
    html_content += """
    </body>
    </html>
    """
    # Write HTML content to the file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)


def generate_test_results_html(test_results):
    """Generate HTML file for test results."""
    os.makedirs("test_results", exist_ok=True)
    file_path = os.path.join(
        "test_results", f"test_results_{int(time.time())}.html")
    test_results_to_html(test_results, file_path)
    logging.info(f"Test results saved to {file_path}")
    return file_path
