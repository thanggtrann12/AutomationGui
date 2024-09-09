import logging

# List to store log entries
log_entries = []


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


def logs_to_html(log_entries, output_file):
    """Convert log entries to HTML and save to a file."""
    html_content = """
    <html>
    <head>
        <title>Log Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1>Log Report</h1>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Message</th>
            </tr>
    """

    for entry in log_entries:
        timestamp, level, message = entry
        html_content += f"""
        <tr>
            <td>{timestamp}</td>
            <td>{level}</td>
            <td>{message}</td>
        </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(output_file, 'w') as f:
        f.write(html_content)


def setup_logging(parent):
    log_handler = QTextEditLogger(parent.console)
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(log_handler)
    logging.getLogger().setLevel(logging.INFO)


def export_logs_to_html(output_file):
    """Export captured logs to an HTML file."""
    logs_to_html(log_entries, output_file)
