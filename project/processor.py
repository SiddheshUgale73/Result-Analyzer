"""
dynamic_result_analyzer.processor
===============================

Core processing logic for cleaning PDF result sheets, parsing student
records, generating CSVs, and computing analytics such as toppers and
SGPA distributions.
"""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict

import pdfplumber
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# configuration constants --------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"      # recommended location for text/csv files

DEFAULT_FILES = {
    "output": DATA_DIR / "output.txt",
    "first_year_students": DATA_DIR / "first_year_students.txt",
    "second_year_students": DATA_DIR / "second_year_students.txt",
    "first_year_csv": DATA_DIR / "first_year_subject_totals.csv",
    "second_year_csv": DATA_DIR / "second_year_subject_totals.csv",
    "first_year_all_csv": DATA_DIR / "first_year_all_subject_totals.csv",
}

# Ensure data dir exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_pdf(pdf_file):
    """
    Extract text from PDF while skipping headers, footers, and unwanted keywords.
    """
    remove_keywords = [
        "SAVITRIBAI PHULE PUNE UNIVERSITY",
        "FORMERLY UNIVERSITY OF PUNE",
        "MASTER OF COMPUTER APPLICATIONS",
        "College Ledger",
        "PunCode :",
        "INT EXT TW",
        "Min ",
        "Max ",
        "~~~~~~",
        "MEDIUM OF INSTRUCTION",
        "continued....",
        "PUNE-411 007",
        "MANAGEMENT STUDIES & RESEARCH, NASHIK"
    ]

    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            # Skip first page
            for page in pdf.pages[1:]:
                page_text = page.extract_text()
                if page_text:
                    for line in page_text.splitlines():
                        line_strip = line.strip()
                        if re.match(r"^Page\s+\d+", line_strip):
                            continue
                        if re.match(r"^[.]{5,}$", line_strip):
                            continue
                        if any(keyword in line for keyword in remove_keywords):
                            continue
                        if line_strip == "":
                            continue
                        text += line_strip + "\n"

        with open(DEFAULT_FILES["output"], "w", encoding="utf-8") as f:
            f.write(text)

        return "✅ PDF converted successfully"
    except Exception as e:
        return f"❌ Error cleaning PDF: {e}"


def separate_students(input_file=DEFAULT_FILES["output"]):
    """
    Separate students into first-year and second-year text files.
    """
    try:
        first_year_records = []
        second_year_records = []

        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_record = []
        previous_line = ""

        for line in lines:
            line_strip = line.strip()

            if line_strip.startswith("PRN:"):
                if current_record:
                    record_text = "".join(current_record)
                    if "First Year" in previous_line:
                        first_year_records.append(record_text)
                    elif "SGPA :" in previous_line:
                        second_year_records.append(record_text)
                current_record = [line]
            else:
                current_record.append(line)

            if line_strip != "":
                previous_line = line_strip

        # Last record
        if current_record:
            record_text = "".join(current_record)
            if "First Year" in previous_line:
                first_year_records.append(record_text)
            elif "SGPA :" in previous_line:
                second_year_records.append(record_text)

        with open(DEFAULT_FILES["first_year_students"], "w", encoding="utf-8") as f:
            f.write("\n".join(first_year_records))

        with open(DEFAULT_FILES["second_year_students"], "w", encoding="utf-8") as f:
            f.write("\n".join(second_year_records))

        return f"✅ Students separated successfully!"
    except FileNotFoundError:
        return f"❌ Error: {input_file} not found"
    except Exception as e:
        return f"❌ Error separating students: {e}"


def generate_first_year_csv(input_file=DEFAULT_FILES["first_year_students"], output_file=DEFAULT_FILES["first_year_csv"]):
    """
    Generate CSV for first-year students skipping incomplete records.
    """
    try:
        fy_students = []
        all_subjects = set()

        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        students = content.split("PRN:")
        students = [s.strip() for s in students if s.strip()]

        for s in students:
            record = "PRN:" + s

            prn_match = re.search(r"PRN:\s*(\d+)", record)
            prn = prn_match.group(1) if prn_match else ""

            seat_match = re.search(r"SEAT NO.:\s*(\d+)", record)
            seat_no = seat_match.group(1) if seat_match else ""

            name_match = re.search(r"NAME:\s*(.+?)\s*Mother", record, re.DOTALL)
            name = name_match.group(1).replace("\n", " ").strip() if name_match else ""

            mother_match = re.search(r"Mother(?:'s)? Name\s*[:-]?\s*(.+)", record, re.DOTALL)
            mother_name = mother_match.group(1).split("\n")[0].lstrip("-: ").strip() if mother_match else ""

            sgpa1_match = re.search(r"First Semester SGPA\s*:\s*([0-9.]+|---)", record)
            sgpa2_match = re.search(r"Second Semester SGPA\s*:\s*([0-9.]+|---)", record)

            sgpa1 = sgpa1_match.group(1) if sgpa1_match else "---"
            sgpa2 = sgpa2_match.group(1) if sgpa2_match else "---"

            if "---" in (sgpa1, sgpa2):
                continue

            try:
                cgpa = round((float(sgpa1) + float(sgpa2)) / 2, 2)
            except ValueError:
                continue

            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+", re.MULTILINE
            )

            subjects = {}
            for match in subject_pattern.finditer(record):
                sub_code, total, grade = match.groups()
                subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                all_subjects.add(sub_code)

            fy_students.append({
                "PRN": prn, "Seat No.": seat_no, "Name": name, "Mother's Name": mother_name,
                "SGPA 1": sgpa1, "SGPA 2": sgpa2, "CGPA": cgpa, "Subjects": subjects
            })

        base_headers = ["PRN", "Seat No.", "Name", "Mother's Name", "SGPA 1", "SGPA 2", "CGPA"]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()
        for sub in subject_headers:
            headers.extend([f"{sub}_TOTAL", f"{sub}_GRADE"])

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for st in fy_students:
                row = [st["PRN"], st["Seat No."], st["Name"], st["Mother's Name"], st["SGPA 1"], st["SGPA 2"], st["CGPA"]]
                for sub in subject_headers:
                    if sub in st["Subjects"]:
                        row.extend([st["Subjects"][sub]["TOTAL"], st["Subjects"][sub]["GRADE"]])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)
        return "✅ First year CSV generated"
    except FileNotFoundError:
        return f"❌ Error: {input_file} not found"
    except Exception as e:
        return f"❌ Error generating CSV: {e}"


def generate_second_year_csv(input_file=DEFAULT_FILES["second_year_students"], output_file=DEFAULT_FILES["second_year_csv"]):
    """
    Generate CSV for second-year students including Sem 1-4.
    """
    try:
        all_subjects = set()
        students = []

        with open(input_file, "r", encoding="utf-8") as f:
            data = f.read()

        records = data.split("PRN:")
        records = [r.strip() for r in records if r.strip()]

        for rec in records:
            rec = "PRN:" + rec

            prn = re.search(r"PRN:\s*(\d+)", rec)
            seat = re.search(r"SEAT NO.:\s*(\d+)", rec)
            name = re.search(r"NAME:\s*([A-Z\s]+)", rec)
            mother = re.search(r"Mother'?s Name\s*[:-]?\s*([A-Z\s]+)", rec)

            prn = prn.group(1) if prn else ""
            seat_no = seat.group(1) if seat else ""
            name_val = name.group(1).strip() if name else ""
            mother_val = mother.group(1).strip() if mother else ""

            sgpa = {}
            for sem in range(1, 5):
                match = re.search(rf"{['First','Second','Third','Fourth'][sem-1]} Semester SGPA\s*:\s*([0-9.]+|---)", rec)
                sgpa[str(sem)] = match.group(1) if match else "---"

            cgpa = re.search(r"C\.G\.P\.A\.\s*:\s*([0-9.]+)", rec)
            cgpa = cgpa.group(1) if cgpa else "---"

            sem_sections = re.findall(r"SEMESTER:\s*\d(.*?)(?=SEMESTER:|C\.G\.P\.A)", rec, re.DOTALL)
            sem_text = "\n".join(sem_sections)

            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+", re.MULTILINE
            )

            subjects = {}
            for m in subject_pattern.finditer(sem_text):
                sub_code, total, grade = m.groups()
                if total.isdigit() and grade.isalpha():
                    subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                    all_subjects.add(sub_code)

            students.append({
                "PRN": prn, "Seat No.": seat_no, "Name": name_val, "Mother's Name": mother_val,
                "SGPA 1": sgpa["1"], "SGPA 2": sgpa["2"], "SGPA 3": sgpa["3"], "SGPA 4": sgpa["4"],
                "CGPA": cgpa, "Subjects": subjects
            })

        base_headers = ["PRN", "Seat No.", "Name", "Mother's Name", "SGPA 1", "SGPA 2", "SGPA 3", "SGPA 4", "CGPA"]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()

        for sub in subject_headers:
            headers.extend([f"{sub}_TOTAL", f"{sub}_GRADE"])

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for s in students:
                row = [s["PRN"], s["Seat No."], s["Name"], s["Mother's Name"],
                       s["SGPA 1"], s["SGPA 2"], s["SGPA 3"], s["SGPA 4"], s["CGPA"]]
                for sub in subject_headers:
                    if sub in s["Subjects"]:
                        row.extend([s["Subjects"][sub]["TOTAL"], s["Subjects"][sub]["GRADE"]])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)

        return "✅ Second year CSV generated"
    except FileNotFoundError:
        return f"❌ Error: {input_file} not found"
    except Exception as e:
        return f"❌ Error: {e}"


def generate_all_first_year_csv(input_file=DEFAULT_FILES["first_year_students"], output_file=DEFAULT_FILES["first_year_all_csv"]):
    """
    Generate CSV for all first-year students including incomplete/failed ones.
    """
    try:
        fy_students = []
        all_subjects = set()

        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        students = content.split("PRN:")
        students = [s.strip() for s in students if s.strip()]

        for s in students:
            record = "PRN:" + s

            prn_match = re.search(r"PRN:\s*(\d+)", record)
            prn = prn_match.group(1) if prn_match else ""

            seat_match = re.search(r"SEAT NO.:\s*(\d+)", record)
            seat_no = seat_match.group(1) if seat_match else ""

            name_match = re.search(r"NAME:\s*(.+?)\s*Mother", record, re.DOTALL)
            name = name_match.group(1).replace("\n", " ").strip() if name_match else ""

            mother_match = re.search(r"Mother(?:'s)? Name\s*[:-]?\s*(.+)", record, re.DOTALL)
            mother_name = mother_match.group(1).split("\n")[0].lstrip("-: ").strip() if mother_match else ""

            sgpa1_match = re.search(r"First Semester SGPA\s*:\s*([0-9.]+|---)", record)
            sgpa2_match = re.search(r"Second Semester SGPA\s*:\s*([0-9.]+|---)", record)

            sgpa1 = sgpa1_match.group(1) if sgpa1_match else "---"
            sgpa2 = sgpa2_match.group(1) if sgpa2_match else "---"

            try:
                if sgpa1 != "---" and sgpa2 != "---":
                    cgpa = round((float(sgpa1) + float(sgpa2)) / 2, 2)
                else:
                    cgpa = "---"
            except ValueError:
                cgpa = "---"

            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+", re.MULTILINE
            )

            subjects = {}
            for match in subject_pattern.finditer(record):
                sub_code, total, grade = match.groups()
                subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                all_subjects.add(sub_code)

            fy_students.append({
                "PRN": prn, "Seat No.": seat_no, "Name": name, "Mother's Name": mother_name,
                "SGPA 1": sgpa1, "SGPA 2": sgpa2, "CGPA": cgpa, "Subjects": subjects
            })

        base_headers = ["PRN", "Seat No.", "Name", "Mother's Name", "SGPA 1", "SGPA 2", "CGPA"]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()
        for sub in subject_headers:
            headers.extend([f"{sub}_TOTAL", f"{sub}_GRADE"])

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for st in fy_students:
                row = [st["PRN"], st["Seat No."], st["Name"], st["Mother's Name"], st["SGPA 1"], st["SGPA 2"], st["CGPA"]]
                for sub in subject_headers:
                    if sub in st["Subjects"]:
                        row.extend([st["Subjects"][sub]["TOTAL"], st["Subjects"][sub]["GRADE"]])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)
        return "✅ First year ALL CSV generated"
    except FileNotFoundError:
        return f"❌ Error: {input_file} not found"
    except Exception as e:
        return f"❌ Error generating CSV: {e}"


# --- REFACTORED GENERIC FUNCTIONS ---

def get_top5_students(csv_file, sort_key="CGPA"):
    """
    Read CSV file, sort students by given key (e.g. 'CGPA', 'SGPA 1'), 
    and return top 5 students as a list of strings.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Name", "")
                prn = row.get("PRN", "")
                try:
                    val = float(row.get(sort_key, "---"))
                    students.append({"Name": name, "PRN": prn, sort_key: val})
                except ValueError:
                    continue

        top5 = sorted(students, key=lambda x: x[sort_key], reverse=True)[:5]
        return [
            f"{i+1}. {s['Name']} | {s['PRN']} | {sort_key}: {s[sort_key]}"
            for i, s in enumerate(top5)
        ]
    except FileNotFoundError:
        return [f"❌ Error: CSV file not found ({csv_file.name if hasattr(csv_file, 'name') else csv_file})"]
    except Exception as e:
        return [f"❌ Error fetching top 5 students: {e}"]


def get_subject_toppers(csv_file):
    """
    Read CSV and find toppers for each subject (_TOTAL columns).
    Returns a list of strings: "SubjectCode | Name | PRN | Marks: X"
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            headers = reader.fieldnames

        if not data or not headers:
            return ["❌ Error: No data found in CSV!"]

        subject_columns = [h for h in headers if h.endswith("_TOTAL")]
        toppers_list = []

        for sub_col in subject_columns:
            sub_code = sub_col.replace("_TOTAL", "")
            max_marks = -1
            top_students = []

            for row in data:
                marks_text = row.get(sub_col, "").strip()
                if not marks_text:
                    continue
                try:
                    marks = float(marks_text)
                except ValueError:
                    continue
                
                if marks > max_marks:
                    max_marks = marks
                    top_students = [row]
                elif marks == max_marks:
                    top_students.append(row)

            for st in top_students:
                toppers_list.append(
                    f"{sub_code} | {st.get('Name', '')} | {st.get('PRN', '')} | Marks: {max_marks}"
                )

        return toppers_list
    except FileNotFoundError:
        return [f"❌ Error: CSV file not found ({csv_file.name if hasattr(csv_file, 'name') else csv_file})"]
    except Exception as e:
        return [f"❌ Error fetching subject toppers: {e}"]


def get_subject_summary(csv_file):
    """
    Calculates Pass/Fail count and percentage based on subject codes.
    Marks and Grade present => PASS. Missing => FAIL.
    """
    subject_summary = defaultdict(lambda: {"Pass": 0, "Fail": 0})
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return {"Error": "❌ No data found in CSV!"}

            subject_codes = sorted(
                [col.replace("_TOTAL", "") for col in reader.fieldnames if col.endswith("_TOTAL")]
            )

            for row in rows:
                for sub in subject_codes:
                    total = row.get(f"{sub}_TOTAL", "").strip()
                    grade = row.get(f"{sub}_GRADE", "").strip()

                    if not total or not grade:
                        subject_summary[sub]["Fail"] += 1
                    else:
                        subject_summary[sub]["Pass"] += 1

            total_students = len(rows)
            final_summary = {}
            for sub, counts in subject_summary.items():
                pass_count = counts["Pass"]
                fail_count = counts["Fail"]

                pass_percent = round((pass_count / total_students) * 100, 2) if total_students else 0
                fail_percent = round((fail_count / total_students) * 100, 2) if total_students else 0

                final_summary[sub] = {
                    "Pass": pass_count,
                    "Fail": fail_count,
                    "Pass%": pass_percent,
                    "Fail%": fail_percent
                }

            return dict(sorted(final_summary.items()))
    except FileNotFoundError:
        return {"Error": f"❌ Error: CSV file not found ({csv_file.name if hasattr(csv_file, 'name') else csv_file})"}
    except Exception as e:
        return {"Error": f"❌ Error while generating subject summary: {e}"}


def generate_sgpa_chart(csv_file, sgpa_col, title, output_filename):
    """
    Generates a bar chart distribution for a specific SGPA column.
    """
    categories = {
        "Distinction (>=8.5)": 0, "O (8.0 - 8.49)": 0, "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0, "B+ (6.5 - 6.99)": 0, "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0, "Pass (<5.5)": 0, "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sgpa_str = row.get(sgpa_col, "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5: categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5: categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0: categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5: categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0: categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5: categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0: categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5: categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1

        total = sum(categories.values())
        percentages = {k: round((v / total) * 100, 2) if total > 0 else 0 for k, v in categories.items()}

        static_dir = BASE_DIR / "static"
        static_dir.mkdir(exist_ok=True)
        chart_path = static_dir / output_filename

        plt.figure(figsize=(10, 6))
        plt.bar(
            percentages.keys(), percentages.values(),
            color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800", "#F44336", "#00BCD4", "#9E9E9E", "#795548"]
        )
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        # Return just the filename for url_for in templates
        return output_filename, percentages
    except FileNotFoundError:
        print(f"Error generating chart: CSV file not found ({csv_file})")
        return None, {}
    except Exception as e:
        print(f"Error generating chart: {e}")
        return None, {}
