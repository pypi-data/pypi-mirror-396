# USA Data Analytics Final Project Scaffold

The purpose of this project was to demonstrate the ability to create a full data analytics project from start to finish.

This repository is the scaffolding for the python package usadata. It includes:
- a data cleaning pipeline
- an analysis pipeline
- a Streamlit prototype app
- a Quarto site for documentation and reporting

The link to the repository is [HERE](https://github.com/JNSREB2023/USAData).
Link to website [HERE](https://jnsreb2023.github.io/USAData/).

## Dependencies
- Python 3.8+
- The required packages can be installed via pip:

```bash
uv pip install -r requirements.txt
```

## Quick start

```bash
uv sync
uv run pytest
```

## Streamlit App

- Launch the app UI with:

```bash
uv run streamlit run src/final_project_demo/streamlit_app.py
```

## Testing Package locally

run the following command to install the package in editable mode:

```bash
uv pip install -e .
``` 

Then you can import the package in your python scripts or notebooks:

```python
import usadata as uda

# Example usage
# This will return the USA data as a pandas DataFrame
data = uda.USData()
```

