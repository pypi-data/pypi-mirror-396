**dictlistlib** is a powerful query utility designed for working with Python dictionaries and lists. It enables developers to validate and verify results using flexible query mechanisms such as simple wildcard characters, regular expressions, custom keywords, and SQL‑like select statements. By combining familiar querying techniques with Python’s native data structures, dictlistlib streamlines data exploration and manipulation, reducing the need for repetitive boilerplate code. Its intuitive design makes it easy to filter, search, and transform collections with precision, while maintaining readability and efficiency. With dictlistlib, developers gain a versatile tool that enhances productivity and supports cleaner, more maintainable workflows.

---

## ⚙️ Installation  

You can install the **dictlistlib** package directly from PyPI using `pip`:  

```bash
pip install dictlistlib
```  

### ✅ Requirements  
- Python 3.9 or higher  
- Internet connection to fetch dependencies from PyPI

---

## 📦 Dependencies  

This project relies on the following Python packages to ensure smooth functionality and integration:  

- [**compare_version**](https://pypi.org/project/compare_versions/) – Utility for comparing and validating version strings.  
- [**PyYAML**](https://pypi.org/project/PyYAML/) – YAML parser and emitter for Python, enabling structured configuration management.  
- [**python-dateutil**](https://pypi.org/project/python-dateutil/) – Powerful extensions to Python’s `datetime` module for parsing, formatting, and manipulating dates.  


---

## ✨ Features  

- 🔹 **Wildcard Support** – Query data using simple wildcard characters (`?`, `*`, `[]`, `[!]`) for flexible matching.  
- 🔹 **Regex Integration** – Harness the power of regular expressions for advanced pattern searching and validation.  
- 🔹 **Custom Keywords** – Define and use your own keywords to tailor queries to specific project needs.  
- 🔹 **SQL‑like Select Statements** – Perform intuitive, SQL‑style queries directly on Python dictionaries and lists.  
- 🔹 **GUI Application Support** – Includes graphical interface capabilities for interactive querying and visualization.  

---

## 🚀 Usage  

After installation, you can explore the available options by running:  

```bash
(venv) $ dictlistlib --help
```

### Command-Line Options  

- `-h, --help`  
  Display the help message and exit.  

- `--gui`  
  Launch the **dictlistlib** GUI application for interactive querying.  

- `-f FILENAME, --filename FILENAME`  
  Specify the input file (JSON, YAML, or CSV).  

- `-e {csv,json,yaml,yml}, --filetype {csv,json,yaml,yml}`  
  Define the file type explicitly (CSV, JSON, YAML, or YML).  

- `-l LOOKUP, --lookup LOOKUP`  
  Provide lookup criteria for searching within lists or dictionaries.  

- `-s SELECT_STATEMENT, --select SELECT_STATEMENT`  
  Use SQL‑like select statements to enhance complex search criteria.  

- `-t, --tabular`  
  Display results in a tabular format for readability.  

- `-d, --dependency`  
  Show Python package dependencies required by dictlistlib.  

- `-u {base,csv,json,yaml}, --tutorial {base,csv,json,yaml}`  
  Access built‑in tutorials (base, CSV, JSON, or YAML).  

---

## 🚀 Getting Started  

### 🛠️ Development Example  

```python
# Sample test data
lst_of_dict = [
    {"title": "ABC Widget", "name": "abc", "width": 500},
    {"title": "DEF Widget", "name": "def", "width": 300},
    {"title": "MNP Widget", "name": "mnp", "width": 455},
    {"title": "XYZ Widget", "name": "xyz", "width": 600}
]

from dictlistlib import DLQuery

# Initialize query object
query_obj = DLQuery(lst_of_dict)

# Find any title starting with A or X
query_obj.find(lookup="title=_wildcard([AX]*)")
# Output: ['ABC Widget', 'XYZ Widget']

# Find titles starting with A or X AND select title, width where width < 550
query_obj.find(
    lookup="title=_wildcard([AX]*)",
    select="SELECT title, width WHERE width lt 550"
)
# Output: [{'title': 'ABC Widget', 'width': 500}]
```

### 📂 Querying from Files  

```python
# JSON file
from dictlistlib import create_from_json_file
query_obj = create_from_json_file('/path/sample.json')
query_obj.find(lookup="title=_wildcard([AX]*)")

# JSON string
from dictlistlib import create_from_json_data

# YAML file
from dictlistlib import create_from_yaml_file

# YAML string
from dictlistlib import create_from_yaml_data

# CSV file
from dictlistlib import create_from_csv_file

# CSV string
from dictlistlib import create_from_csv_data
```

---

### 💻 Console Command Line  

You can run **dictlistlib** directly from the terminal, either as a standalone command or via Python module invocation.  

#### 🔹 Launch the Application  

```bash
# Using console command line
$ dictlistlib --gui  

# Using Python module invocation
$ python -m dictlistlib --gui  
```  

#### 🔹 Search JSON, YAML, or CSV Files  

```bash
# Assuming /path/sample.json has the same structure as lst_of_dict
$ dictlistlib --filename=/path/sample.json --lookup="title=_wildcard([AX]*)"
['ABC Widget', 'XYZ Widget']

# Apply SQL-like select statement for advanced filtering
$ dictlistlib --filename=/path/sample.json \
    --lookup="title=_wildcard([AX]*)" \
    --select="SELECT title, width WHERE width lt 550"
[{'title': 'ABC Widget', 'width': 500}]

# The same syntax applies for YAML (.yaml/.yml) or CSV files
```

---

## 🐞 Bugs & Feature Requests  

If you encounter a bug or have a feature request, please submit it through the official [GitHub Issue Tracker](https://github.com/Geeks-Trident-LLC/dictlistlib/issues). This helps us track, prioritize, and resolve issues efficiently while keeping all feedback in one place.

---

## 🛣️ Roadmap

We’re actively evolving **dictlistlib** to deliver more power and flexibility. Upcoming milestones include:

- **🐼 Pandas Integration** - Extend functionality by integrating with the Pandas library, enabling advanced data manipulation, analysis, and seamless interoperability with DataFrames.

- **🗄️ Simple SQL Support** - Add lightweight SQL‑like querying for improved usability and performance, making complex filtering and joins more intuitive.

- **🧪 Testing & Feedback** - Expand automated test coverage and invite community feedback to ensure reliability, correctness, and continuous improvement.

- **🤝 Collaboration** - Encourage contributions, discussions, and shared development efforts to grow the library together with the open‑source community.

---
## 📜 License  

This project is licensed under the **BSD 3‑Clause License**.  
You can review the full license text here:  
- [BSD 3‑Clause License](https://github.com/Geeks-Trident-LLC/dictlistlib/blob/develop/LICENSE)  

### 🔍 What the BSD 3‑Clause License Means  
- ✅ **Freedom to Use** – You may use this library in both open‑source and proprietary projects.  
- ✅ **Freedom to Modify** – You can adapt, extend, or customize the code to fit your needs.  
- ✅ **Freedom to Distribute** – Redistribution of source or binary forms is permitted, with or without modification.  
- ⚠️ **Conditions** – You must retain the copyright notice, license text, and disclaimers in redistributions.  
- ❌ **Restrictions** – You cannot use the names of the project or its contributors to endorse or promote derived products without prior permission.  

### ⚡ Why BSD 3‑Clause?  
The BSD 3‑Clause License strikes a balance between openness and protection. It allows broad usage and collaboration while ensuring proper attribution and preventing misuse of contributor names for marketing or endorsement.  

---

## ⚠️ Disclaimer  

This package is currently in **pre‑beta development**. Features, APIs, and dependencies may change before the official 1.x release. While it is functional, please use it with caution in production environments and expect ongoing updates as the project matures.  

---  