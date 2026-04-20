# Dynamic Result Analyzer 📊

A modern, Flask-based Python web application designed to process university result PDFs, extract student records, and generate powerful analytics such as top performers, subject-wise summaries, and SGPA distribution charts. 

## ✨ Features

- **Automated PDF Parsing:** Upload university result PDFs and automatically extract student marks, grades, and SGPAs/CGPAs using `pdfplumber`.
- **Top Performer Analytics:** Dynamically generate "Top 5" lists based on overall CGPA or specific semester SGPAs.
- **Subject-Wise Summaries:** Calculate pass/fail percentages and identify toppers for every subject.
- **Visual Dashboards:** Automatically generate colorful SGPA distribution bar charts using `matplotlib`.
- **Premium UI:** Features a modern, responsive **glassmorphism** design built with Jinja templates and vanilla CSS.

## 📁 Project Structure

```text
Dynamic Result Analyzer/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── project/
    ├── app.py              # Flask web application routing (entry point)
    ├── processor.py        # Core processing engine (PDF parsing, CSV generation, data logic)
    ├── data/               # Auto-generated input/output text and CSV files
    ├── static/             # Static assets (generated charts, stylesheets)
    ├── templates/          # Jinja HTML templates (glassmorphism UI)
    └── uploads/            # Temporary storage for uploaded PDFs
```

## 🚀 Recent Architectural Upgrades

The codebase has recently undergone a massive professional refactor:
1. **DRY Principle Enforcement:** Over 1,100 lines of duplicate logic in `processor.py` were consolidated into 4 powerful, generic, and parameter-driven functions.
2. **Robust Error Handling:** Replaced dangerous bare exceptions with targeted exception handling (`ValueError`, `FileNotFoundError`) to ensure bugs are reported correctly instead of silently swallowed.
3. **Template Engine Migration:** Removed hundreds of lines of hardcoded HTML strings from the Python backend, migrating all UI components to dedicated `Jinja2` templates.
4. **UI/UX Overhaul:** Introduced a dark-themed, glassmorphic aesthetic with micro-animations and Google's `Inter` typography.

## 🛠 Setup & Usage

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Navigate into the `project` directory and start the Flask development server:
```bash
cd project
python app.py
```

### 5. Access the Web Interface
Open your web browser and navigate to:
**http://127.0.0.1:5000**

From the home page, upload your university result PDF. The backend will parse the document, generate structured CSV data, and redirect you to the analytics dashboard where you can explore the results!

## 📜 License & Contributions
Feel free to fork this repository, submit Pull Requests, or open Issues for any bugs or feature requests!
