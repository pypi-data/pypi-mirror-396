# OVM-ERD

**Generate automated Entity-Relationship Diagrams (ERDs), SQL queries, and validation reports from your dbt repository.**

---

## 📌 Overview

`ovm-erd` is a Python package designed to simplify the visualization and validation of Data Vault (DV) structured databases using dbt repositories. Automatically generate ER diagrams in multiple formats (Graphviz, Mermaid, Draw.io), produce SQL queries, and validate your database metadata.

---

## ✨ Features

- **Automated ER Diagrams:** Generate clear diagrams in:
  - ✅ **Graphviz** (PNG format)
  - ✅ **Mermaid** (Markdown)
  - ✅ **Draw.io** (`.drawio.xml` and PNG formats)

- **SQL Generation:** Automatically build SQL queries based on your repository metadata.

- **Metadata Validation:** Verify your data vault entities and relationships with HTML validation reports.

- **Easy-to-use CLI:** Simple commands to automate common tasks.

---

## 🚀 Installation

OVM-ERD requires Graphviz to be installed locally. See https://graphviz.org/ for details.

Install via pip:

```bash
pip install ovm-erd
```

---

## 📚 Usage

### CLI

**Generate ER diagrams:**
```bash
ovm-erd generate [graphviz|mermaid|drawio]
```

**Generate ER diagrams with specific paths:**
```bash
ovm-erd generate graphviz --path /your/output/path
```

**Generate diagrams distinctly for each ensemble/tag:**
```bash
ovm-erd generate drawio --distinct
```

**Generate SQL queries for a specific ensemble:**
```bash
ovm-erd sql --ensemble your_ensemble_name
```

**Validate metadata and generate HTML report:**
```bash
ovm-erd validate
```

**Specify custom paths for validation reports:**
```bash
ovm-erd validate --path /your/report/path
```

### Python API

Use the package directly in Python:

```python
from ovm_erd.repository_reader import build_metadata_dict
from ovm_erd.erd_graphviz import generate_graphviz

repository_path = "your/dbt/repo"
output_path = "output/graphviz"

metadata = build_metadata_dict(repository_path=repository_path)
generate_graphviz(metadata, output_dir=output_path)
```

You can specify paths dynamically by assigning them to variables, enhancing flexibility:

```python
custom_repo_path = "/path/to/dbt/repository"
custom_output_path = "/path/to/output"

metadata = build_metadata_dict(repository_path=custom_repo_path)
generate_graphviz(metadata, output_dir=custom_output_path)
```



## 🎨 ERD Color Coding

- **Hub:** Light Blue (`#D6EAF8`)
- **Satellite:** Light Yellow (`#FFFACD`)
- **Link:** Light Red (`#F5B7B1`)

---

### Run tests:
```bash
pytest tests/
```


## Example output Graphviz

![example output](ovm_erd/output/erd_example.png)

---

## 📄 License

GPL © Ferry Ouwerkerk / Data-Project BV

