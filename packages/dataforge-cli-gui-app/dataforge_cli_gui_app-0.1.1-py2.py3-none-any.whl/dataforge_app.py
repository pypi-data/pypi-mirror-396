import sys
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import yaml
import argparse 
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QTabWidget, QLabel, QFileDialog, QMessageBox, 
    QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard
import pathlib
import os

# --- CORE LOGIC FUNCTIONS ---
# (These remain the same)
def parse_sentence_to_dict(sentence: str) -> dict:
    # ... (content remains the same) ...
    data = {}
    pairs = sentence.split(',')
    
    for pair in pairs:
        try:
            key, value = pair.split(' is ', 1)
            key = key.strip()
            value = value.strip()
            
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass

            data[key] = value
            
        except ValueError:
            continue
            
    return data

def convert_dict_to_xml(data: dict) -> str:
    # ... (content remains the same) ...
    root = ET.Element("DataForgeEntry") 
    
    for key, value in data.items():
        child = ET.SubElement(root, key.replace(' ', '_')) 
        child.text = str(value)
    
    raw_xml_string = ET.tostring(root, encoding='utf-8')
    reparsed_xml = minidom.parseString(raw_xml_string)
    pretty_xml = reparsed_xml.toprettyxml(indent="  ")
    
    return pretty_xml.replace('<?xml version="1.0" ?>\n', '', 1)

def run_simple_query(data_dict: dict, query: str) -> any:
    # ... (content remains the same) ...
    try:
        if ' = ?' in query:
            key = query.replace(' = ?', '').strip()
            return data_dict.get(key)
        
        elif ' > ' in query:
            key, value_str = query.split(' > ', 1)
            key = key.strip()
            
            try:
                target_value = float(value_str.strip())
            except ValueError:
                return f"Error: Cannot compare non-numeric value '{value_str.strip()}'."
            
            data_value = data_dict.get(key)
            if isinstance(data_value, (int, float)):
                if data_value > target_value:
                    return f"Condition True: {key} ({data_value}) is greater than {target_value}."
                else:
                    return f"Condition False: {key} ({data_value}) is NOT greater than {target_value}."
            else:
                return f"Key '{key}' not found or is not a number in the data."
        
        else:
            return f"Unsupported query format: '{query}'\nSupported formats: 'Key = ?' or 'Key > Value'."
            
    except Exception as e:
        return f"An error occurred during query execution:\n{e}"

# --- DOCUMENTATION WINDOW (NEW CLASS) ---

class DocsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataForge Documentation")
        self.setGeometry(100, 100, 550, 650) # Smaller, dedicated window
        
        layout = QVBoxLayout(self)
        
        # Use a QTextEdit to display nicely formatted documentation
        self.docs_view = QTextEdit()
        self.docs_view.setReadOnly(True)
        self.docs_view.setText(self._get_docs_content())
        
        layout.addWidget(self.docs_view)
        
    def _get_docs_content(self):
        """Returns the Markdown/HTML formatted documentation content."""
        
        # Using basic HTML/CSS for simple formatting that PyQt6's QTextEdit supports
        return f"""
        <html>
        <head>
            <style>
                h2 {{ color: #0066cc; border-bottom: 2px solid #ccc; padding-bottom: 5px; }}
                h3 {{ color: #333333; }}
                code {{ background-color: #eee; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
                p {{ margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>DataForge Documentation</h1>
            <p>Welcome to DataForge! This tool allows you to quickly convert structured text into standard data formats (JSON, YAML, XML) and query those files.</p>

            <h2>1. DataFy Tab (Conversion)</h2>
            <p>Convert human-readable sentences into structured data.</p>
            
            <h3>Sentence Structure</h3>
            <p>Use the format <code>KEY is VALUE</code>, with each key/value pair separated by a comma (<code>,</code>). Spaces around <code>is</code> and <code>,</code> don't matter.</p>
            <ul>
                <li><b>Example:</b> <code>Name is Rudra, Age is 10, City is Atlanta</code></li>
            </ul>
            <p>DataForge will automatically try to guess the data type:</p>
            <ul>
                <li>If the value is a whole number (e.g., <code>10</code>), it becomes an Integer.</li>
                <li>If the value has a decimal (e.g., <code>49.99</code>), it becomes a Float (decimal number).</li>
                <li>Everything else is treated as a String (text).</li>
            </ul>

            <h2>2. QueriFy Tab (Querying)</h2>
            <p>Access data in JSON, YAML, or XML files using simple 'questions'.</p>

            <h3>Simple Query Structure: Fetch Value</h3>
            <p>Use this structure to find the value associated with a specific key.</p>
            <ul>
                <li><b>Structure:</b> <code>Key Name = ?</code></li>
                <li><b>Example:</b> <code>Name = ?</code> (If the data contains <code>"Name": "Rudra"</code>, the output will be <code>Rudra</code>)</li>
            </ul>

            <h3>Complex Query Structure: Condition Check</h3>
            <p>Use this structure to check if a numeric value meets a certain condition (greater than).</p>
            <ul>
                <li><b>Structure:</b> <code>Numeric Key > Value</code></li>
                <li><b>Example:</b> <code>Age > 5</code> (If the data contains <code>"Age": 10</code>, the output will be <code>Condition True...</code>)</li>
                <li><i>Note:</i> Only the <b>greater than</b> (<code>></code>) comparison is supported currently.</li>
            </ul>
            
            <h3>Command Line Interface (CLI)</h3>
            <p>You can also use DataForge from the terminal (<code>dataforge_app.py</code>) using the <code>convert</code> and <code>query</code> commands. Use <code>--help</code> for usage instructions.</p>
            
        </body>
        </html>
        """

# --- PYQT6 GUI SETUP ---

class DataForgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataForge: Data Converter & Query Tool")
        self.setGeometry(100, 100, 1000, 700) 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.datafy_tab = QWidget()
        self.tabs.addTab(self.datafy_tab, "DataFy (Convert)")
        self._setup_datafy_tab()
        
        self.queryfy_tab = QWidget()
        self.tabs.addTab(self.queryfy_tab, "QueriFy (Query)")
        self._setup_queryfy_tab() 

        # --- OPEN THE DOCUMENTATION WINDOW AUTOMATICALLY (NEW) ---
        self.docs_window = DocsWindow()
        self.docs_window.show()


    # ... (All other methods like _setup_datafy_tab, _setup_queryfy_tab, 
    #       convert_data, run_query_action, etc., remain exactly the same) ...
    #       We omit them here for brevity, but they must be present in your file.

    def _setup_datafy_tab(self):
        # ... (content remains the same) ...
        datafy_layout = QVBoxLayout(self.datafy_tab)
        input_label = QLabel("Enter structured sentence (e.g., Name is Bob, Age is 32):")
        datafy_layout.addWidget(input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste or type your data here...")
        self.input_text.setFixedHeight(100)
        datafy_layout.addWidget(self.input_text)
        self.convert_button = QPushButton("Convert Data")
        self.convert_button.clicked.connect(self.convert_data)
        datafy_layout.addWidget(self.convert_button)
        output_layout = QHBoxLayout()
        self.json_output = self._create_output_area("JSON", "json")
        self.yaml_output = self._create_output_area("YAML", "yaml")
        self.xml_output = self._create_output_area("XML", "xml")
        output_layout.addWidget(self.json_output)
        output_layout.addWidget(self.yaml_output)
        output_layout.addWidget(self.xml_output)
        datafy_layout.addLayout(output_layout)

    def _create_output_area(self, title, extension):
        # ... (content remains the same) ...
        container = QWidget()
        layout = QVBoxLayout(container)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True) 
        layout.addWidget(text_edit)
        if title == "JSON": self.json_text_edit = text_edit
        elif title == "YAML": self.yaml_text_edit = text_edit
        elif title == "XML": self.xml_text_edit = text_edit
        button_layout = QHBoxLayout()
        copy_button = QPushButton(f"Copy {title}")
        download_button = QPushButton(f"Download {title}")
        copy_button.clicked.connect(lambda: self.copy_output(text_edit.toPlainText()))
        download_button.clicked.connect(lambda: self.download_output(text_edit.toPlainText(), extension))
        button_layout.addWidget(copy_button)
        button_layout.addWidget(download_button)
        layout.addLayout(button_layout)
        return container
    
    def _setup_queryfy_tab(self):
        # ... (content remains the same) ...
        queryfy_layout = QVBoxLayout(self.queryfy_tab)
        input_controls = QHBoxLayout()
        self.load_file_button = QPushButton("Load Data File...")
        self.load_file_button.clicked.connect(self.load_data_from_file)
        input_controls.addWidget(self.load_file_button)
        input_controls.addWidget(QLabel("Format:"))
        self.query_format_combo = QComboBox()
        self.query_format_combo.addItems(["JSON", "YAML", "XML"])
        input_controls.addWidget(self.query_format_combo)
        input_controls.addStretch(1)
        queryfy_layout.addLayout(input_controls)
        self.query_input_text = QTextEdit()
        self.query_input_text.setPlaceholderText("Paste your JSON, YAML, or XML data here, or load a file.")
        self.query_input_text.setFixedHeight(250)
        queryfy_layout.addWidget(self.query_input_text)
        query_section_layout = QHBoxLayout()
        query_section_layout.addWidget(QLabel("Query:"))
        self.query_line_edit = QTextEdit()
        self.query_line_edit.setPlaceholderText("Type your query (e.g., Rudra = ? or Age > 5)")
        self.query_line_edit.setFixedHeight(40) 
        query_section_layout.addWidget(self.query_line_edit)
        self.run_query_button = QPushButton("Run Query")
        self.run_query_button.clicked.connect(self.run_query_action)
        query_section_layout.addWidget(self.run_query_button)
        queryfy_layout.addLayout(query_section_layout)
        queryfy_layout.addWidget(QLabel("Query Result:"))
        self.query_output_text = QTextEdit()
        self.query_output_text.setReadOnly(True)
        queryfy_layout.addWidget(self.query_output_text)
        queryfy_layout.addStretch(1)

    # --- Data Action Methods (omitted for brevity, keep them in your file) ---
    def load_data_from_file(self):
        # ... (content remains the same) ...
        filter_str = "Data Files (*.json *.yaml *.xml);;JSON Files (*.json);;YAML Files (*.yaml);;XML Files (*.xml);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Data File for Querying", "", filter_str)
        if file_path:
            file_path_obj = pathlib.Path(file_path)
            extension = file_path_obj.suffix.lower()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.query_input_text.setText(content)
                format_index = self.query_format_combo.findText(extension[1:].upper())
                if format_index >= 0:
                    self.query_format_combo.setCurrentIndex(format_index)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Could not load file:\n{e}")

    def copy_output(self, text_to_copy):
        # ... (content remains the same) ...
        if not text_to_copy.strip():
            QMessageBox.warning(self, "Copy Failed", "The output box is empty.")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def download_output(self, data_content, file_extension):
        # ... (content remains the same) ...
        if not data_content.strip():
            QMessageBox.warning(self, "Download Failed", "There is no content to save.")
            return
        filter_str = f"{file_extension.upper()} Files (*.{file_extension});;All Files (*)"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Data File", f"dataforge_output.{file_extension}", filter_str)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data_content)
                QMessageBox.information(self, "Success!", f"Data saved successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")

    def convert_data(self):
        # ... (content remains the same) ...
        input_text = self.input_text.toPlainText()
        data_dict = parse_sentence_to_dict(input_text)
        try:
            json_str = json.dumps(data_dict, indent=2)
            self.json_text_edit.setText(json_str)
        except Exception as e:
            self.json_text_edit.setText(f"JSON Error: {e}")
        try:
            yaml_str = yaml.dump(data_dict, indent=2, sort_keys=False)
            self.yaml_text_edit.setText(yaml_str)
        except NameError:
            self.yaml_text_edit.setText("YAML not available. Run 'pip install PyYAML'")
        except Exception as e:
            self.yaml_text_edit.setText(f"YAML Error: {e}")
        try:
            xml_str = convert_dict_to_xml(data_dict)
            self.xml_text_edit.setText(xml_str)
        except Exception as e:
            self.xml_text_edit.setText(f"XML Error: {e}")

    def run_query_action(self):
        # ... (content remains the same) ...
        data_text = self.query_input_text.toPlainText().strip()
        query_text = self.query_line_edit.toPlainText().strip()
        format_type = self.query_format_combo.currentText()
        if not data_text or not query_text:
            QMessageBox.warning(self, "Input Missing", "Please provide data and a query.")
            return
        data_dict = {}
        try:
            if format_type == "JSON":
                data_dict = json.loads(data_text)
            elif format_type == "YAML":
                data_dict = yaml.safe_load(data_text)
            elif format_type == "XML":
                root = ET.fromstring(data_text)
                data_dict = {elem.tag: elem.text for elem in root}
        except Exception as e:
            self.query_output_text.setText(f"ERROR converting {format_type} to data:\n{e}")
            return
        result = run_simple_query(data_dict, query_text)
        if result is not None:
            if isinstance(result, (dict, list)):
                display_output = json.dumps(result, indent=2)
            else:
                display_output = str(result)
            self.query_output_text.setText(display_output)
        else:
            self.query_output_text.setText("Query resulted in no match (None).")


# --- CLI FUNCTIONS ---
# (These remain the same)
def cli_convert(sentence: str, output_format: str, output_file: str = None):
    # ... (content remains the same) ...
    data_dict = parse_sentence_to_dict(sentence)
    output_str = ""
    if output_format == "json":
        output_str = json.dumps(data_dict, indent=2)
    elif output_format == "yaml":
        try:
            output_str = yaml.dump(data_dict, indent=2, sort_keys=False)
        except NameError:
            print("YAML library not found. Please install PyYAML.")
            sys.exit(1)
    elif output_format == "xml":
        output_str = convert_dict_to_xml(data_dict)
    else:
        print(f"Error: Unsupported format {output_format}")
        sys.exit(1)
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"Data successfully converted and saved to: {output_file}")
        except Exception as e:
            print(f"Error saving file {output_file}: {e}")
            sys.exit(1)
    else:
        print(output_str)

def cli_query(input_file: str, file_format: str, query: str, output_file: str = None):
    # ... (content remains the same) ...
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        sys.exit(1)
    data_text = ""
    with open(input_file, 'r', encoding='utf-8') as f:
        data_text = f.read()
    data_dict = {}
    try:
        if file_format == "json":
            data_dict = json.loads(data_text)
        elif file_format == "yaml":
            data_dict = yaml.safe_load(data_text)
        elif file_format == "xml":
            root = ET.fromstring(data_text)
            data_dict = {elem.tag: elem.text for elem in root}
        else:
            print(f"Error: Unsupported input format {file_format}")
            sys.exit(1)
    except Exception as e:
        print(f"Error parsing {file_format} data: {e}")
        sys.exit(1)
    result = run_simple_query(data_dict, query)
    if isinstance(result, (dict, list)):
        result_output = json.dumps(result, indent=2)
    else:
        result_output = str(result)
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_output)
            print(f"Query result successfully saved to: {output_file}")
        except Exception as e:
            print(f"Error saving output file {output_file}: {e}")
            sys.exit(1)
    else:
        print(result_output)

# --- MAIN EXECUTION BLOCK ---

def main():
    """The main entry point, decides between GUI and CLI mode."""
    
    # If no arguments are provided, or only '-g' or '--gui' is present, launch the GUI.
    if len(sys.argv) == 1 or '-g' in sys.argv or '--gui' in sys.argv:
        app = QApplication(sys.argv)
        window = DataForgeApp()
        window.show()
        sys.exit(app.exec())
    
    # Otherwise, parse arguments for CLI mode.
    parser = argparse.ArgumentParser(
        description="DataForge CLI: Convert structured sentences to data formats or query files.",
        epilog="Use 'python3 dataforge_app.py' with no arguments to launch the GUI."
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # CONVERT Subcommand (DataFy CLI)
    convert_parser = subparsers.add_parser("convert", help="Convert a structured sentence to JSON, YAML, or XML.")
    convert_parser.add_argument("sentence", type=str, help="The structured sentence (e.g., 'Name is Rudra, Age is 10').")
    convert_parser.add_argument("-f", "--format", choices=["json", "yaml", "xml"], required=True, help="Output data format.")
    convert_parser.add_argument("-o", "--output", type=str, help="Optional output file path. If omitted, output is printed to console.")

    # QUERY Subcommand (QueriFy CLI)
    query_parser = subparsers.add_parser("query", help="Query a data file (JSON, YAML, or XML).")
    query_parser.add_argument("-i", "--input", type=str, required=True, help="Input file path (JSON, YAML, or XML).")
    query_parser.add_argument("-q", "--query", type=str, required=True, help="The simple query (e.g., 'Name = ?' or 'Age > 5').")
    query_parser.add_argument("-t", "--type", choices=["json", "yaml", "xml"], required=True, help="Input file type.")
    query_parser.add_argument("-o", "--output", type=str, help="Optional output file path. If omitted, output is printed to console.")

    args = parser.parse_args()
    
    if args.command == "convert":
        cli_convert(args.sentence, args.format, args.output)
    elif args.command == "query":
        cli_query(args.input, args.type, args.query, args.output)

if __name__ == "__main__":
    main()
