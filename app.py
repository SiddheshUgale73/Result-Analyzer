from flask import Flask, render_template, request
from processor import *

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
    clean_pdf(pdf_file)  # We don’t need return messages

    # Step 2: Separate students
    separate_students("output.txt")  # Silent

    # Step 3: Generate CSV for first-year pass students
    generate_first_year_csv("first_year_students.txt", "first_year_subject_totals.csv")  # Silent

    # Step 3: Generate CSV for second-year pass students
    generate_second_year_csv("second_year_students.txt", "second_year_subject_totals.csv")

    # Step 3: Generate CSV for first-year all students
    generate_all_first_year_csv("first_year_students.txt", "first_year_all_subject_totals.csv")  # Silent

    # After CSV is ready, show options page
    return render_template('options.html')  # New page with radio buttons
    
@app.route('/options')
def options():
    return render_template('options.html')  # The page you just shared




@app.route('/process_option', methods=['POST'])
def process_option():
    selected_option = request.form.get('option')
    
    table_html = ""
    
    if selected_option == "top5":
        top5_list = get_top5_students()  # List of strings like "1. Name | PRN | CGPA"
        
        # Build HTML table
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'> Top 5 Student As Per CGPA </h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 60%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>CGPA</th>
                </tr>
        """
        for item in top5_list:
            rank, rest = item.split(". ", 1)
            name, prn_cgpa = rest.split(" | ", 1)
            prn, cgpa_text = prn_cgpa.split(" | ")
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{cgpa_text.replace('CGPA: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"
    
    elif selected_option == "top5_2":
        top5_list = get_top5_students_second_year()  # List of strings like "1. Name | PRN | CGPA"
        
        # Build HTML table
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'> Top 5 Student As Per CGPA </h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 60%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>CGPA</th>
                </tr>
        """
        for item in top5_list:
            rank, rest = item.split(". ", 1)
            name, prn_cgpa = rest.split(" | ", 1)
            prn, cgpa_text = prn_cgpa.split(" | ")
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{cgpa_text.replace('CGPA: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"
    
    elif selected_option == "top5_sgpa_1_2":
        # Get Top 5 lists separately for Sem 1 and Sem 2
        top5_sem1 = get_top5_students_sem1_second_year()  # List like ["1. Name | PRN | CGPA: 6.45", ...]
        top5_sem2 = get_top5_students_sem2_second_year()  # List like ["1. Name | PRN | CGPA: 6.14", ...]

        # Base HTML
        table_html = """
        <h2 style='display:flex;justify-content:center;font-size:38px;margin-top:30px;'>
            🏆 Top 5 Students of Second Year 🏆
        </h2>
        """

        # 🔹 Function to build a styled table (reusable)
        def build_table(top5_list, sem_title, color):
            html = f"""
            <h3 style='display:flex;justify-content:center;margin-top:40px;
                    font-size:28px;color:{color};'>{sem_title}</h3>
            <div style='display:flex;justify-content:center;margin-top:20px;margin-bottom:60px;'>
                <table style='border-collapse:collapse;width:65%;background:rgba(255,255,255,0.95);
                            box-shadow:0 8px 20px rgba(0,0,0,0.2);border-radius:12px;'>
                    <tr style='background:{color};color:white;'>
                        <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                        <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                        <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                        <th style='padding:12px;border:1px solid #ddd;'>CGPA</th>
                    </tr>
            """
            for item in top5_list:
                rank, rest = item.split(". ", 1)
                name, prn_cgpa = rest.split(" | ", 1)
                prn, cgpa_text = prn_cgpa.split(" | ")
                html += f"""
                    <tr style='text-align:center;'>
                        <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                        <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                        <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                        <td style='padding:10px;border:1px solid #ddd;'>{cgpa_text.replace('CGPA: ', '')}</td>
                    </tr>
                """
            html += "</table></div>"
            return html

        # 🔹 Add both semester tables one below the other
        table_html += build_table(top5_sem1, "📘 Semester 1 - Top 5 Students", "#0078d7")
        table_html += build_table(top5_sem2, "📗 Semester 2 - Top 5 Students", "#28a745")

    elif selected_option == "top5_sgpa_3_4":
        # Get Top 5 lists for Sem 3 and Sem 4
        top5_sem3 = get_top5_students_sem3_second_year()  # Example: ["1. Name | PRN | CGPA: 7.33", ...]
        top5_sem4 = get_top5_students_sem4_second_year()  # Example: ["1. Name | PRN | CGPA: 6.94", ...]

        # Base HTML title
        table_html = """
        <h2 style='display:flex;justify-content:center;font-size:38px;margin-top:30px;'>
            🏆 Top 5 Students of Second Year (Semester 3 & 4) 🏆
        </h2>
        """

        # 🔹 Reusable function for building each table
        def build_table(top5_list, sem_title, color):
            html = f"""
            <h3 style='display:flex;justify-content:center;margin-top:40px;
                    font-size:28px;color:{color};'>{sem_title}</h3>
            <div style='display:flex;justify-content:center;margin-top:20px;margin-bottom:60px;'>
                <table style='border-collapse:collapse;width:65%;background:rgba(255,255,255,0.95);
                            box-shadow:0 8px 20px rgba(0,0,0,0.2);border-radius:12px;'>
                    <tr style='background:{color};color:white;'>
                        <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                        <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                        <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                        <th style='padding:12px;border:1px solid #ddd;'>CGPA</th>
                    </tr>
            """
            for item in top5_list:
                try:
                    rank, rest = item.split(". ", 1)
                    name, prn_cgpa = rest.split(" | ", 1)
                    prn, cgpa_text = prn_cgpa.split(" | ")
                    html += f"""
                        <tr style='text-align:center;'>
                            <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                            <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                            <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                            <td style='padding:10px;border:1px solid #ddd;'>{cgpa_text.replace('CGPA: ', '')}</td>
                        </tr>
                    """
                except:
                    continue
            html += "</table></div>"
            return html

        # 🔹 Add both semester tables one below the other
        table_html += build_table(top5_sem3, "📘 Semester 3 - Top 5 Students", "#0078d7")
        table_html += build_table(top5_sem4, "📗 Semester 4 - Top 5 Students", "#28a745")


    elif selected_option == "top5_sgpa1":
        top5_sgpa_list = get_top5_students_sgpa_wise_sem1()

        # Build HTML table for SGPA toppers
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'> Top 5 Student As Per SGPA SEM 1</h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 60%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>SGPA</th>
                </tr>
        """
        for item in top5_sgpa_list:
            rank, rest = item.split(". ", 1)
            name, prn_sgpa = rest.split(" | ", 1)
            prn, sgpa_text = prn_sgpa.split(" | ")
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{sgpa_text.replace('SGPA: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"

    elif selected_option == "top5_sgpa2":
        top5_sgpa_list = get_top5_students_sgpa_wise_sem2()

        # Build HTML table for SGPA toppers
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'> Top 5 Student As Per SGPA SEM 2  </h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 60%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Rank</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>SGPA</th>
                </tr>
        """
        for item in top5_sgpa_list:
            rank, rest = item.split(". ", 1)
            name, prn_sgpa = rest.split(" | ", 1)
            prn, sgpa_text = prn_sgpa.split(" | ")
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{rank}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{sgpa_text.replace('SGPA: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"

    elif selected_option == "subject_topper":
        subject_toppers = get_subject_toppers()  # Returns list of "SubjectCode | Name | PRN | Marks"
        
        # Build HTML table
        table_html = """
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 70%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Subject Code</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Marks</th>
                </tr>
        """
        for item in subject_toppers:
            sub_code, name, prn, marks_text = [s.strip() for s in item.split("|")]
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{sub_code}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{marks_text.replace('Marks: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"

    elif selected_option == "subject_topper_2":
        subject_toppers = get_subject_toppers_2()  # Returns list of "SubjectCode | Name | PRN | Marks"
        
        # Build HTML table
        table_html = """
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 70%; background: rgba(255,255,255,0.95); 
                          box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Subject Code</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Name</th>
                    <th style='padding:12px;border:1px solid #ddd;'>PRN</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Marks</th>
                </tr>
        """
        for item in subject_toppers:
            sub_code, name, prn, marks_text = [s.strip() for s in item.split("|")]
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{sub_code}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{name}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{prn}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{marks_text.replace('Marks: ', '')}</td>
                </tr>
            """
        table_html += "</table></div>"


    elif selected_option == "sgpa_chart":
        chart_path, percentages = get_sgpa_chart()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 1) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)

    elif selected_option == "sgpa_chart_sem2":
        chart_path, percentages = get_sgpa_chart_sem2()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 2) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart2.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)
    
    elif selected_option == "subject_summary":
        summary = get_subject_summary()

        if "Error" in summary:
            return f"<h3 style='color:red;text-align:center;'>{summary['Error']}</h3>"

        # Build summary table
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'>📘 Subject-wise Pass/Fail Summary</h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 80%; background: rgba(255,255,255,0.95); 
                        box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Subject Code</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Pass Count</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Fail Count</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Pass %</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Fail %</th>
                </tr>
        """

        for subject, stats in summary.items():
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{subject}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Pass']}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Fail']}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Pass%']}%</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Fail%']}%</td>
                </tr>
            """

        table_html += "</table></div>"

        # Back button
        table_html += """
        <div style='text-align:center;margin-top:30px;'>
            <a href='/options' style='text-decoration:none;'>
                <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                            cursor:pointer;'>⬅ Back</button>
            </a>
        </div>
        """

        return table_html

    elif selected_option == "subject_summary_2":
        summary = get_subject_summary_2()

        if "Error" in summary:
            return f"<h3 style='color:red;text-align:center;'>{summary['Error']}</h3>"

        # Build summary table
        table_html = """
        <h6 style='display:flex;justify-content:center;font-size: 40px;'>📘 Subject-wise Pass/Fail Summary</h6>
        <div style='display:flex;justify-content:center;margin-top:50px;'>
            <table style='border-collapse: collapse; width: 80%; background: rgba(255,255,255,0.95); 
                        box-shadow: 0 8px 20px rgba(0,0,0,0.2); border-radius: 12px;'>
                <tr style='background:#0078d7; color:white;'>
                    <th style='padding:12px;border:1px solid #ddd;'>Subject Code</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Pass Count</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Fail Count</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Pass %</th>
                    <th style='padding:12px;border:1px solid #ddd;'>Fail %</th>
                </tr>
        """

        for subject, stats in summary.items():
            table_html += f"""
                <tr style='text-align:center;'>
                    <td style='padding:10px;border:1px solid #ddd;'>{subject}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Pass']}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Fail']}</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Pass%']}%</td>
                    <td style='padding:10px;border:1px solid #ddd;'>{stats['Fail%']}%</td>
                </tr>
            """

        table_html += "</table></div>"

        # Back button
        table_html += """
        <div style='text-align:center;margin-top:30px;'>
            <a href='/options' style='text-decoration:none;'>
                <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                            cursor:pointer;'>⬅ Back</button>
            </a>
        </div>
        """

        return table_html
    
    elif selected_option == "sgpa_chart_sem1_y2":
        chart_path, percentages = get_sgpa_chart_sem1_y2()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 1) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart_sem1_y2.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)

    elif selected_option == "sgpa_chart_sem2_y2":
        chart_path, percentages = get_sgpa_chart_sem2_y2()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 2) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart_sem2_y2.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)
    
    elif selected_option == "sgpa_chart_sem3_y2":
        chart_path, percentages = get_sgpa_chart_sem3_y2()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 3) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart_sem3_y2.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)
    
    elif selected_option == "sgpa_chart_sem4_y2":
        chart_path, percentages = get_sgpa_chart_sem4_y2()
        
        html_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SGPA Chart Dashboard</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    text-align: center;
                    padding: 40px;
                }
                img {
                    width: 80%;
                    max-width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }
                table {
                    margin: 0 auto;
                    border-collapse: collapse;
                    background: #fff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                th, td {
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                th {
                    background: #0078d7;
                    color: white;
                }
                h2 {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <h2>📊 SGPA (Sem 4) Result Distribution</h2>
            {% if chart_path %}
                <img src="{{ url_for('static', filename='sgpa_chart_sem4_y2.png') }}" alt="SGPA Chart">
            {% else %}
                <p style="color:red;">Error: Could not generate chart.</p>
            {% endif %}

            {% if percentages %}
            <table>
                <tr><th>Category</th><th>Percentage (%)</th></tr>
                {% for category, percent in percentages.items() %}
                    <tr><td>{{ category }}</td><td>{{ percent }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
                <p style="color:red;">No data available to display.</p>
            {% endif %}

            <div style='text-align:center;margin-top:30px;'>
                <a href='/options' style='text-decoration:none;'>
                    <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                                cursor:pointer;'>⬅ Back</button>
                </a>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_page, chart_path=chart_path, percentages=percentages)

    else:
        return "❌ Invalid option selected!"

    # Add Back button
    table_html += """
    <div style='text-align:center;margin-top:30px;'>
        <a href='/options' style='text-decoration:none;'>
            <button style='background:#0078d7;color:white;padding:10px 20px;border:none;border-radius:6px;
                           cursor:pointer;'>⬅ Back</button>
        </a>
    </div>
    """

    return table_html


    

if __name__ == '__main__':
    app.run(debug=True)
