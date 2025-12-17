# DataForge

A versatile Python utility providing both a Graphical User Interface (GUI) and a Command Line Interface (CLI) for data conversion and simple querying of JSON, YAML, and XML files.

## Features

* **DataFy:** Convert simple, structured sentences into valid JSON, YAML, and XML.
* **QueriFy:** Query the contents of JSON, YAML, or XML files using simple, human-readable questions.
* **GUI:** Modern, PyQt6-based interface with automatic documentation.
* **CLI:** Seamless integration via `pipx` for use in scripts and automation.

---

## 🚀 Installation

DataForge is best installed using `pipx`, which installs it into an isolated environment and makes the `dataforge` command easily accessible in your terminal.

**Prerequisites:** You must have Python 3.8+, venv, and `pipx` installed.

```bash
pipx install dataforge_cli-gui_app
```

---

## Usage

### 1. GUI Mode
Simply run the command with no arguments to launch the application and documentation window:
```bash
dataforge
```

### 2. CLI Mode: Convert (DataFy)
Convert a structured sentence into a data format and output it to the console or a file.
**Syntax:** `dataforge convert "SENTENCE" --format [json|yaml|xml] [-o OUTPUT_FILE]`
```bash

# Example: Convert to JSON and print to console
dataforge convert "User is Rudra, Location is Home, Age is 10" -f json

# Example: Convert to XML and save to a file
dataforge convert "Project is DataForge, Status is Completed" --format xml -o project.xml
```

### 3. CLI Mode: Query (QueriFy)
Query data from a file using simple questions.
**Syntax:** `dataforge query -i INPUT_FILE -t [json|yaml|xml] -q "QUERY" [-o OUTPUT_FILE]`
| Query Type  | Structure             | Example    | Description                                                          |
| ----------- | --------------------- | ---------- | -------------------------------------------------------------------- |
| Fetch Value | "Key Name = ?"        | "Name = ?" | Returns the value associated with the key.                           |
| Condition   | "Numeric Key > Value" | "Age > 18" | Checks if a key's numeric value is greater than the specified value. |

```
# Example: Query a YAML file for a specific value
dataforge query -i config.yaml -t yaml -q "version = ?"

# Example: Query a JSON file for a condition check
dataforge query -i data.json -t json -q "score > 90"
```
---

## LICENSE
DataForge is released under the MIT License.
