"""
Web interface for the Dynamic Result Analyzer.

The Flask application exposes endpoints to upload a result PDF and
select analyses such as top students, subject toppers, and SGPA charts.
The heavy lifting is delegated to functions in ``processor.py``.
"""

from flask import Flask, render_template, request, render_template_string
from pathlib import Path

# import only what we need and pull DEFAULT_FILES for path management
from processor import (
    clean_pdf,
    separate_students,
    generate_first_year_csv,
    generate_second_year_csv,
    generate_all_first_year_csv,
    get_top5_students,
    get_top5_students_second_year,
    get_top5_students_sem1_second_year,
    get_top5_students_sem2_second_year,
    get_top5_students_sem3_second_year,
    get_top5_students_sem4_second_year,
    get_top5_students_sgpa_wise_sem1,
    get_top5_students_sgpa_wise_sem2,
    get_subject_toppers,
    get_subject_toppers_2,
    get_subject_summary,
    get_subject_summary_2,
    get_sgpa_chart,
    get_sgpa_chart_sem2,
    DEFAULT_FILES,
)

# base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"  # matching DEFAULT_FILES locations

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Upload form




@app.route('/upload', methods=['POST'])
def upload_file():
    pdf_file = request.files.get('pdf')
    if not pdf_file:
        return "❌ No PDF uploaded!", 400

    # Step 1: Clean PDF
    clean_pdf(pdf_file)

    # Step 2: Separate students into text files under data dir
    separate_students(str(DEFAULT_FILES["output"]))

    # Step 3: Generate the required CSVs; pass explicit paths so the
    # functions don't rely on current working directory.
    generate_first_year_csv(
        str(DEFAULT_FILES["first_year_students"]),
        str(DEFAULT_FILES["first_year_csv"]),
    )
    generate_second_year_csv(
        str(DEFAULT_FILES["second_year_students"]),
        str(DEFAULT_FILES["second_year_csv"]),
    )
    generate_all_first_year_csv(
        str(DEFAULT_FILES["first_year_students"]),
        str(DEFAULT_FILES["first_year_all_csv"]),
    )

    # After CSV is ready, show options page
    return render_template('options.html')  # New page with radio buttons
    
@app.route('/options')
def options():
    return render_template('options.html')  # The page you just shared




@app.route('/process_option', methods=['POST'])
def process_option():
    selected_option = request.form.get('option')

    def parse_top5(data_list):
        rows = []
        for item in data_list:
            try:
                rank, rest = item.split(". ", 1)
                name, prn_score = rest.split(" | ", 1)
                prn, score_text = prn_score.split(" | ")
                score = score_text.replace('CGPA: ', '').replace('SGPA 1: ', '').replace('SGPA 2: ', '').replace('SGPA 3: ', '').replace('SGPA 4: ', '')
                rows.append([rank, name, prn, score])
            except Exception:
                continue
        return rows

    def parse_subject_toppers(data_list):
        rows = []
        for item in data_list:
            try:
                sub_code, name, prn, marks_text = [s.strip() for s in item.split("|")]
                marks = marks_text.replace('Marks: ', '')
                rows.append([sub_code, name, prn, marks])
            except Exception:
                continue
        return rows

    # TOP 5 CGPA Options
    if selected_option in ["top5", "top5_2"]:
        title = "Top 5 Students As Per CGPA"
        data_list = get_top5_students() if selected_option == "top5" else get_top5_students_second_year()
        tables = [{
            "headers": ["Rank", "Name", "PRN", "CGPA"],
            "rows": parse_top5(data_list)
        }]
        return render_template('result_table.html', title=title, tables=tables)

    # TOP 5 SGPA Combined Options
    elif selected_option == "top5_sgpa_1_2":
        tables = [
            {
                "subtitle": "📘 Semester 1 - Top 5 Students",
                "color": "#0078d7",
                "headers": ["Rank", "Name", "PRN", "SGPA"],
                "rows": parse_top5(get_top5_students_sem1_second_year())
            },
            {
                "subtitle": "📗 Semester 2 - Top 5 Students",
                "color": "#28a745",
                "headers": ["Rank", "Name", "PRN", "SGPA"],
                "rows": parse_top5(get_top5_students_sem2_second_year())
            }
        ]
        return render_template('result_table.html', title="🏆 Top 5 Students of Second Year 🏆", tables=tables)

    elif selected_option == "top5_sgpa_3_4":
        tables = [
            {
                "subtitle": "📘 Semester 3 - Top 5 Students",
                "color": "#0078d7",
                "headers": ["Rank", "Name", "PRN", "SGPA"],
                "rows": parse_top5(get_top5_students_sem3_second_year())
            },
            {
                "subtitle": "📗 Semester 4 - Top 5 Students",
                "color": "#28a745",
                "headers": ["Rank", "Name", "PRN", "SGPA"],
                "rows": parse_top5(get_top5_students_sem4_second_year())
            }
        ]
        return render_template('result_table.html', title="🏆 Top 5 Students of Second Year (Semester 3 & 4) 🏆", tables=tables)

    # TOP 5 SGPA Individual Options
    elif selected_option in ["top5_sgpa1", "top5_sgpa2"]:
        sem = "SEM 1" if selected_option == "top5_sgpa1" else "SEM 2"
        data_list = get_top5_students_sgpa_wise_sem1() if selected_option == "top5_sgpa1" else get_top5_students_sgpa_wise_sem2()
        tables = [{
            "headers": ["Rank", "Name", "PRN", "SGPA"],
            "rows": parse_top5(data_list)
        }]
        return render_template('result_table.html', title=f"Top 5 Students As Per SGPA {sem}", tables=tables)

    # SUBJECT TOPPERS
    elif selected_option in ["subject_topper", "subject_topper_2"]:
        data_list = get_subject_toppers() if selected_option == "subject_topper" else get_subject_toppers_2()
        tables = [{
            "headers": ["Subject Code", "Name", "PRN", "Marks"],
            "rows": parse_subject_toppers(data_list)
        }]
        return render_template('result_table.html', title="Subject Toppers", tables=tables)

    # SUBJECT SUMMARIES
    elif selected_option in ["subject_summary", "subject_summary_2"]:
        summary = get_subject_summary() if selected_option == "subject_summary" else get_subject_summary_2()
        if "Error" in summary:
            return render_template('result_summary.html', title="📘 Subject-wise Pass/Fail Summary", error=summary["Error"])
        return render_template('result_summary.html', title="📘 Subject-wise Pass/Fail Summary", summary=summary)

    # SGPA CHARTS
    elif selected_option.startswith("sgpa_chart"):
        if selected_option == "sgpa_chart":
            chart_path, percentages = get_sgpa_chart()
            title = "📊 SGPA (Sem 1) Result Distribution"
        elif selected_option == "sgpa_chart_sem2":
            chart_path, percentages = get_sgpa_chart_sem2()
            title = "📊 SGPA (Sem 2) Result Distribution"
        elif selected_option == "sgpa_chart_sem1_y2":
            chart_path, percentages = get_sgpa_chart_sem1_y2()
            title = "📊 SGPA (Sem 1) Result Distribution"
        elif selected_option == "sgpa_chart_sem2_y2":
            chart_path, percentages = get_sgpa_chart_sem2_y2()
            title = "📊 SGPA (Sem 2) Result Distribution"
        elif selected_option == "sgpa_chart_sem3_y2":
            chart_path, percentages = get_sgpa_chart_sem3_y2()
            title = "📊 SGPA (Sem 3) Result Distribution"
        elif selected_option == "sgpa_chart_sem4_y2":
            chart_path, percentages = get_sgpa_chart_sem4_y2()
            title = "📊 SGPA (Sem 4) Result Distribution"
        else:
            return "❌ Invalid chart option!", 400
        
        return render_template('result_chart.html', title=title, chart_path=chart_path, percentages=percentages)

    return "❌ Invalid option selected!", 400


    

if __name__ == '__main__':
    app.run(debug=True)
