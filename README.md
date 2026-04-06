# Dynamic Result Analyzer

A simple Flask-based Python project to process university result PDFs, extract student records, and compute analytics such as top performers and SGPA distributions. The application can run locally or be deployed to platforms like Heroku (see `Procfile`).

## 📁 Project Structure

```
Dynamic Result Analyzer/
├── README.md               # this file
├── requirements.txt        # Python dependencies
├── project/
│   ├── app.py              # Flask web application (entrypoint)
│   ├── processor.py        # core processing logic (cleaning, parsing, CSV, analytics)
│   ├── data/               # (you should create this) input/output text and CSV files
│   ├── static/             # static assets (images, charts, CSS)
│   ├── templates/          # HTML templates for Flask
│   ├── uploads/            # uploaded PDFs and results
│   ├── Procfile            # for Heroku deployment
│   └── runtime.txt         # Python runtime for Heroku
└── first_year_students.txt # legacy files at root (move into data/)
```

> ⚠️ The top-level `.txt` and `.csv` files are duplicates of those under `project/data`. To keep things tidy, move all input/output files into `project/data` and update any paths in the code accordingly (defaults now point to `data/`).

## ✅ Improvements Made

- **Consolidated and documented imports** in `processor.py`.
- Added a module-level docstring and configuration constants (`DEFAULT_FILES`) for centralizing file paths.
- Removed redundant `import` statements and duplicate Flask app initializations.
- Introduced a simple CLI (`--clean`, `--first-csv`, `--second-csv`) for offline testing of processor functions.
- Centralized default file locations using `Path` objects and `DEFAULT_FILES` dict.
- Added a basic `README.md` with clear setup/usage instructions.
- Added an `if __name__ == "__main__"` block for quick command‑line runs.

## 🛠 Setup & Usage

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate    # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r project/requirements.txt
   ```

3. **Prepare data folder**:
   ```bash
   mkdir project\data
   move *.txt project\data        # move your sample text files
   move *.csv project\data        # if you already generated any
   ```
   The code now uses `project/data` by default; you can continue passing explicit paths if needed.

4. **Run the web app**:
   ```bash
   cd project
   python app.py
   ```
   Open <http://127.0.0.1:5000> in your browser. Upload a results PDF and explore the options page.

5. **CLI usage (for developers)**:
   ```bash
   python processor.py --clean path\to\result.pdf
   python processor.py --first-csv
   python processor.py --second-csv
   ```

## 🧹 Next Steps / Recommendations

- Factor repeated HTML table building into Jinja templates (e.g. `table.html`).
- Write unit tests for parsing and analytics functions using `pytest`.
- Convert the project into a proper Python package (`setup.py` / `pyproject.toml`) if sharing.
- Remove legacy files from the repository root and keep only project‑specific code under `project/`.

Documentation is always the first step toward a "proper" project – the code now has clearer structure, and the README explains how to bootstrap and run the application.

🎯 Feel free to ask for help reorganizing further or adding features!

## My First Pull Request 🚀


Added collaboration feature

Co-authored-by: DivyeshWagh <waghdivyesh4@gmail.com>
