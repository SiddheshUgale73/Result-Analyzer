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

    # Step 3: Generate CSV for first-year students
    generate_first_year_csv("first_year_students.txt", "first_year_subject_totals.csv")  # Silent

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
