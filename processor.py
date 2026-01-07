import pdfplumber
import re

def clean_pdf(pdf_file):
    """
    Extract text from PDF while skipping:
    - First page
    - Page numbers
    - Dotted lines
    - Unwanted keywords
    - Empty lines
    Save the cleaned text as 'output.txt'.
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
                        # Skip page numbers
                        if re.match(r"^Page\s+\d+", line_strip):
                            continue
                        # Skip dotted lines
                        if re.match(r"^[.]{5,}$", line_strip):
                            continue
                        # Skip unwanted keywords
                        if any(keyword in line for keyword in remove_keywords):
                            continue
                        # Skip empty lines
                        if line_strip == "":
                            continue
                        text += line_strip + "\n"

        # Save cleaned text
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(text)

        #return "✅ PDF converted to output.txt successfully! (Page 1, headers, footers, page numbers, dots skipped)"

    except Exception as e:
        return f"❌ Error cleaning PDF: {e}"
def separate_students(input_file="output.txt"):
    """
    Read the cleaned PDF text from 'input_file', separate students into
    first-year and second-year, and save them into separate text files.
    Returns counts for both.
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

            # New student record starts
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

            # Track last non-empty line
            if line_strip != "":
                previous_line = line_strip

        # Last record
        if current_record:
            record_text = "".join(current_record)
            if "First Year" in previous_line:
                first_year_records.append(record_text)
            elif "SGPA :" in previous_line:
                second_year_records.append(record_text)

        # Save separated files
        with open("first_year_students.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(first_year_records))

        with open("second_year_students.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(second_year_records))

        #return f"✅ Students separated successfully! First Year: {len(first_year_records)}, Second Year: {len(second_year_records)}"

    except Exception as e:
        return f"❌ Error separating students: {e}"

import re
import csv

def generate_first_year_csv(input_file="first_year_students.txt", output_file="first_year_subject_totals.csv"):
    """
    Read first-year student text file, extract student info and subjects,
    and generate a CSV with all subjects and grades.
    """
    try:
        fy_students = []
        all_subjects = set()

        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by PRN
        students = content.split("PRN:")
        students = [s.strip() for s in students if s.strip()]

        for s in students:
            record = "PRN:" + s

            # Extract PRN
            prn_match = re.search(r"PRN:\s*(\d+)", record)
            prn = prn_match.group(1) if prn_match else ""

            # Extract Seat No.
            seat_match = re.search(r"SEAT NO.:\s*(\d+)", record)
            seat_no = seat_match.group(1) if seat_match else ""

            # Extract Name
            name_match = re.search(r"NAME:\s*(.+?)\s*Mother", record, re.DOTALL)
            name = name_match.group(1).replace("\n", " ").strip() if name_match else ""

            # Extract Mother's Name
            mother_match = re.search(r"Mother(?:'s)? Name\s*[:-]?\s*(.+)", record, re.DOTALL)
            if mother_match:
                mother_name = mother_match.group(1).split("\n")[0].strip()
                mother_name = mother_name.lstrip("-: ").strip()
            else:
                mother_name = ""

            # Extract SGPA
            sgpa1_match = re.search(r"First Semester SGPA\s*:\s*([0-9.]+|---)", record)
            sgpa2_match = re.search(r"Second Semester SGPA\s*:\s*([0-9.]+|---)", record)

            sgpa1 = sgpa1_match.group(1) if sgpa1_match else "---"
            sgpa2 = sgpa2_match.group(1) if sgpa2_match else "---"

            # Skip if incomplete
            if "---" in (sgpa1, sgpa2):
                continue

            sgpa1_val = float(sgpa1)
            sgpa2_val = float(sgpa2)
            cgpa = round((sgpa1_val + sgpa2_val) / 2, 2)

            # Extract subject codes with their details
            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+",
                re.MULTILINE
            )

            subjects = {}
            for match in subject_pattern.finditer(record):
                sub_code = match.group(1)
                total = match.group(2)
                grade = match.group(3)
                subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                all_subjects.add(sub_code)

            fy_students.append({
                "PRN": prn,
                "Seat No.": seat_no,
                "Name": name,
                "Mother's Name": mother_name,
                "SGPA 1": sgpa1,
                "SGPA 2": sgpa2,
                "CGPA": cgpa,
                "Subjects": subjects
            })

        # Create CSV headers
        base_headers = ["PRN", "Seat No.", "Name", "Mother's Name", "SGPA 1", "SGPA 2", "CGPA"]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()
        for sub in subject_headers:
            headers.append(f"{sub}_TOTAL")
            headers.append(f"{sub}_GRADE")

        # Write CSV
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for st in fy_students:
                row = [
                    st["PRN"],
                    st["Seat No."],
                    st["Name"],
                    st["Mother's Name"],
                    st["SGPA 1"],
                    st["SGPA 2"],
                    st["CGPA"]
                ]
                for sub in subject_headers:
                    if sub in st["Subjects"]:
                        row.append(st["Subjects"][sub]["TOTAL"])
                        row.append(st["Subjects"][sub]["GRADE"])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)

        #return f"✅ CSV created: {output_file} with {len(fy_students)} students and {len(subject_headers)} subjects."

    except Exception as e:
        return f"❌ Error generating CSV: {e}"
    
import re
import csv

import re
import csv

def generate_second_year_csv(input_file="second_year_students.txt", output_file="second_year_subject_totals.csv"):
    """
    Reads the university result text file and generates a single CSV
    including all four semesters (1–4) with SGPA and subject marks/grades.
    """

    try:
        all_subjects = set()
        students = []

        with open(input_file, "r", encoding="utf-8") as f:
            data = f.read()

        # Split each student record by PRN
        records = data.split("PRN:")
        records = [r.strip() for r in records if r.strip()]

        for rec in records:
            rec = "PRN:" + rec

            # --- Basic Details ---
            prn = re.search(r"PRN:\s*(\d+)", rec)
            seat = re.search(r"SEAT NO.:\s*(\d+)", rec)
            name = re.search(r"NAME:\s*([A-Z\s]+)", rec)
            mother = re.search(r"Mother'?s Name\s*[:-]?\s*([A-Z\s]+)", rec)

            prn = prn.group(1) if prn else ""
            seat_no = seat.group(1) if seat else ""
            name_val = name.group(1).strip() if name else ""
            mother_val = mother.group(1).strip() if mother else ""

            # --- SGPA & CGPA Extraction ---
            sgpa = {}
            for sem in range(1, 5):
                match = re.search(rf"{['First','Second','Third','Fourth'][sem-1]} Semester SGPA\s*:\s*([0-9.]+|---)", rec)
                sgpa[str(sem)] = match.group(1) if match else "---"

            cgpa = re.search(r"C\.G\.P\.A\.\s*:\s*([0-9.]+)", rec)
            cgpa = cgpa.group(1) if cgpa else "---"

            # --- Subject Extraction (for all 4 semesters) ---
            sem_sections = re.findall(r"SEMESTER:\s*\d(.*?)(?=SEMESTER:|C\.G\.P\.A)", rec, re.DOTALL)
            sem_text = "\n".join(sem_sections)

            # Matches lines with subject code, total marks, grade etc.
            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+",
                re.MULTILINE
            )

            subjects = {}
            for m in subject_pattern.finditer(sem_text):
                sub_code = m.group(1)
                total = m.group(2)
                grade = m.group(3)

                if total.isdigit() and grade.isalpha():
                    subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                    all_subjects.add(sub_code)

            students.append({
                "PRN": prn,
                "Seat No.": seat_no,
                "Name": name_val,
                "Mother's Name": mother_val,
                "SGPA 1": sgpa["1"],
                "SGPA 2": sgpa["2"],
                "SGPA 3": sgpa["3"],
                "SGPA 4": sgpa["4"],
                "CGPA": cgpa,
                "Subjects": subjects
            })

        # --- CSV Writing ---
        base_headers = [
            "PRN", "Seat No.", "Name", "Mother's Name",
            "SGPA 1", "SGPA 2", "SGPA 3", "SGPA 4", "CGPA"
        ]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()

        for sub in subject_headers:
            headers.append(f"{sub}_TOTAL")
            headers.append(f"{sub}_GRADE")

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for s in students:
                row = [
                    s["PRN"], s["Seat No."], s["Name"], s["Mother's Name"],
                    s["SGPA 1"], s["SGPA 2"], s["SGPA 3"], s["SGPA 4"], s["CGPA"]
                ]
                for sub in subject_headers:
                    if sub in s["Subjects"]:
                        row.append(s["Subjects"][sub]["TOTAL"])
                        row.append(s["Subjects"][sub]["GRADE"])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)

        print(f"✅ CSV generated successfully: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


def generate_all_first_year_csv(input_file="first_year_students.txt", output_file="first_year_all_subject_totals.csv"):
    """
    Read first-year student text file, extract student info and subjects,
    and generate a CSV with all students (including fail/incomplete ones).
    """
    try:
        fy_students = []
        all_subjects = set()

        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by PRN
        students = content.split("PRN:")
        students = [s.strip() for s in students if s.strip()]

        for s in students:
            record = "PRN:" + s

            # Extract PRN
            prn_match = re.search(r"PRN:\s*(\d+)", record)
            prn = prn_match.group(1) if prn_match else ""

            # Extract Seat No.
            seat_match = re.search(r"SEAT NO.:\s*(\d+)", record)
            seat_no = seat_match.group(1) if seat_match else ""

            # Extract Name
            name_match = re.search(r"NAME:\s*(.+?)\s*Mother", record, re.DOTALL)
            name = name_match.group(1).replace("\n", " ").strip() if name_match else ""

            # Extract Mother's Name
            mother_match = re.search(r"Mother(?:'s)? Name\s*[:-]?\s*(.+)", record, re.DOTALL)
            if mother_match:
                mother_name = mother_match.group(1).split("\n")[0].strip()
                mother_name = mother_name.lstrip("-: ").strip()
            else:
                mother_name = ""

            # Extract SGPA values
            sgpa1_match = re.search(r"First Semester SGPA\s*:\s*([0-9.]+|---)", record)
            sgpa2_match = re.search(r"Second Semester SGPA\s*:\s*([0-9.]+|---)", record)

            sgpa1 = sgpa1_match.group(1) if sgpa1_match else "---"
            sgpa2 = sgpa2_match.group(1) if sgpa2_match else "---"

            # Calculate CGPA only if both are valid
            try:
                if sgpa1 != "---" and sgpa2 != "---":
                    cgpa = round((float(sgpa1) + float(sgpa2)) / 2, 2)
                else:
                    cgpa = "NA"
            except:
                cgpa = "NA"

            # Extract subjects
            subject_pattern = re.compile(
                r"(\d{6}[A-Z]?)\s+(?:[^\n]*?)\s+(\d{2,3})\s+\d+\s+\d+\s+([A-Z])\s+\d+\s+\d+",
                re.MULTILINE
            )

            subjects = {}
            for match in subject_pattern.finditer(record):
                sub_code = match.group(1)
                total = match.group(2)
                grade = match.group(3)
                subjects[sub_code] = {"TOTAL": total, "GRADE": grade}
                all_subjects.add(sub_code)

            fy_students.append({
                "PRN": prn,
                "Seat No.": seat_no,
                "Name": name,
                "Mother's Name": mother_name,
                "SGPA 1": sgpa1,
                "SGPA 2": sgpa2,
                "CGPA": cgpa,
                "Subjects": subjects
            })

        # Create CSV headers
        base_headers = ["PRN", "Seat No.", "Name", "Mother's Name", "SGPA 1", "SGPA 2", "CGPA"]
        subject_headers = sorted(all_subjects)
        headers = base_headers.copy()
        for sub in subject_headers:
            headers.append(f"{sub}_TOTAL")
            headers.append(f"{sub}_GRADE")

        # Write CSV
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for st in fy_students:
                row = [
                    st["PRN"],
                    st["Seat No."],
                    st["Name"],
                    st["Mother's Name"],
                    st["SGPA 1"],
                    st["SGPA 2"],
                    st["CGPA"]
                ]
                for sub in subject_headers:
                    if sub in st["Subjects"]:
                        row.append(st["Subjects"][sub]["TOTAL"])
                        row.append(st["Subjects"][sub]["GRADE"])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)

    except Exception as e:
        return f"❌ Error generating CSV: {e}"

import csv

import csv

def get_top5_students(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students), sort students by CGPA, 
    and return top 5 students as a list of strings.
    Each string: "1. Name | PRN | CGPA: X.XX"
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    cgpa = float(row["CGPA"])
                    students.append({"Name": name, "PRN": prn, "CGPA": cgpa})
                except:
                    continue

        # Sort descending by CGPA
        top5 = sorted(students, key=lambda x: x["CGPA"], reverse=True)[:5]

        # Format for display
        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | CGPA: {s['CGPA']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 students: {e}"]
    
def get_top5_students_second_year(csv_file="second_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students), sort students by CGPA, 
    and return top 5 students as a list of strings.
    Each string: "1. Name | PRN | CGPA: X.XX"
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    cgpa = float(row["CGPA"])
                    students.append({"Name": name, "PRN": prn, "CGPA": cgpa})
                except:
                    continue

        # Sort descending by CGPA
        top5 = sorted(students, key=lambda x: x["CGPA"], reverse=True)[:5]

        # Format for display
        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | CGPA: {s['CGPA']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 students: {e}"]


def get_top5_students_sgpa_wise_sem1(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students), sort by SGPA 1,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa1 = float(row["SGPA 1"])
                    students.append({"Name": name, "PRN": prn, "SGPA 1": sgpa1})
                except:
                    continue

        top5 = sorted(students, key=lambda x: x["SGPA 1"], reverse=True)[:5]

        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 1: {s['SGPA 1']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 1 students: {e}"]

def get_top5_students_sem1_second_year(csv_file="second_year_subject_totals.csv") :
    """
    Read first-year CSV (including fail students), sort by SGPA 1,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa1 = float(row["SGPA 1"])
                    students.append({"Name": name, "PRN": prn, "SGPA 1": sgpa1})
                except:
                    continue

        top5 = sorted(students, key=lambda x: x["SGPA 1"], reverse=True)[:5]

        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 1: {s['SGPA 1']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 1 students: {e}"]

def get_top5_students_sem2_second_year(csv_file="second_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students), sort by SGPA 2,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa2 = float(row["SGPA 2"])
                    students.append({"Name": name, "PRN": prn, "SGPA 2": sgpa2})
                except:
                    continue

        top5 = sorted(students, key=lambda x: x["SGPA 2"], reverse=True)[:5]

        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 2: {s['SGPA 2']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 2 students: {e}"]

def get_top5_students_sem3_second_year(csv_file="second_year_subject_totals.csv"):
    """
    Read second-year CSV (including fail students), sort by SGPA 3,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa3 = float(row["SGPA 3"])
                    students.append({"Name": name, "PRN": prn, "SGPA 3": sgpa3})
                except:
                    continue

        # Sort by SGPA 3 descending
        top5 = sorted(students, key=lambda x: x["SGPA 3"], reverse=True)[:5]

        # Format output
        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 3: {s['SGPA 3']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 3 students: {e}"]
    

def get_top5_students_sem4_second_year(csv_file="second_year_subject_totals.csv"):
    """
    Read second-year CSV (including fail students), sort by SGPA 4,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa4 = float(row["SGPA 4"])
                    students.append({"Name": name, "PRN": prn, "SGPA 4": sgpa4})
                except:
                    continue

        # Sort by SGPA 4 descending
        top5 = sorted(students, key=lambda x: x["SGPA 4"], reverse=True)[:5]

        # Format output
        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 4: {s['SGPA 4']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 4 students: {e}"]



def get_top5_students_sgpa_wise_sem2(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students), sort by SGPA 2,
    and return top 5 students.
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                try:
                    sgpa2 = float(row["SGPA 2"])
                    students.append({"Name": name, "PRN": prn, "SGPA 2": sgpa2})
                except:
                    continue

        top5 = sorted(students, key=lambda x: x["SGPA 2"], reverse=True)[:5]

        top5_list = [
            f"{i+1}. {s['Name']} | {s['PRN']} | SGPA 2: {s['SGPA 2']}"
            for i, s in enumerate(top5)
        ]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 SGPA 2 students: {e}"]
    
def get_subject_toppers(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students) and find toppers 
    for each subject (_TOTAL columns).
    Returns a list of strings for display:
    "SubjectCode | Name | PRN | Marks: X"
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            headers = reader.fieldnames

        # Identify all subjects by columns ending with '_TOTAL'
        subject_columns = [h for h in headers if h.endswith("_TOTAL")]
        toppers_list = []

        for sub_col in subject_columns:
            sub_code = sub_col.replace("_TOTAL", "")
            max_marks = -1
            top_students = []

            for row in data:
                marks_text = row.get(sub_col, "")
                if marks_text.strip() == "":
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
                    f"{sub_code} | {st['Name']} | {st['PRN']} | Marks: {max_marks}"
                )

        return toppers_list

    except Exception as e:
        return [f"❌ Error fetching subject toppers: {e}"]

import csv
from collections import defaultdict

def get_subject_summary(csv_file="first_year_all_subject_totals.csv"):
    """
    Reads student data from the CSV and calculates:
    - Pass count
    - Fail count
    - Pass percentage
    - Fail percentage
    based on subject codes.

    Rule:
    - Marks and Grade are both present => PASS
    - Marks or Grade missing => FAIL
    """

    subject_summary = defaultdict(lambda: {"Pass": 0, "Fail": 0})

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return {"Error": "❌ No data found in CSV!"}

            # Find all subjects (columns ending with _TOTAL)
            subject_codes = sorted(
                [col.replace("_TOTAL", "") for col in reader.fieldnames if col.endswith("_TOTAL")]
            )

            for row in rows:
                for sub in subject_codes:
                    total_col = f"{sub}_TOTAL"
                    grade_col = f"{sub}_GRADE"

                    total = row.get(total_col, "").strip()
                    grade = row.get(grade_col, "").strip()

                    if total == "" or grade == "":
                        subject_summary[sub]["Fail"] += 1
                    else:
                        subject_summary[sub]["Pass"] += 1

            # Compute percentages
            total_students = len(rows)
            final_summary = {}
            for sub, counts in subject_summary.items():
                pass_count = counts["Pass"]
                fail_count = counts["Fail"]

                pass_percent = round((pass_count / total_students) * 100, 2)
                fail_percent = round((fail_count / total_students) * 100, 2)

                final_summary[sub] = {
                    "Pass": pass_count,
                    "Fail": fail_count,
                    "Pass%": pass_percent,
                    "Fail%": fail_percent
                }

            return dict(sorted(final_summary.items()))

    except Exception as e:
        return {"Error": f"❌ Error while generating subject summary: {e}"}

def get_subject_summary_2(csv_file="second_year_subject_totals.csv"):
    """
    Reads student data from the CSV and calculates:
    - Pass count
    - Fail count
    - Pass percentage
    - Fail percentage
    based on subject codes.

    Rule:
    - Marks and Grade are both present => PASS
    - Marks or Grade missing => FAIL
    """

    subject_summary = defaultdict(lambda: {"Pass": 0, "Fail": 0})

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return {"Error": "❌ No data found in CSV!"}

            # Find all subjects (columns ending with _TOTAL)
            subject_codes = sorted(
                [col.replace("_TOTAL", "") for col in reader.fieldnames if col.endswith("_TOTAL")]
            )

            for row in rows:
                for sub in subject_codes:
                    total_col = f"{sub}_TOTAL"
                    grade_col = f"{sub}_GRADE"

                    total = row.get(total_col, "").strip()
                    grade = row.get(grade_col, "").strip()

                    if total == "" or grade == "":
                        subject_summary[sub]["Fail"] += 1
                    else:
                        subject_summary[sub]["Pass"] += 1

            # Compute percentages
            total_students = len(rows)
            final_summary = {}
            for sub, counts in subject_summary.items():
                pass_count = counts["Pass"]
                fail_count = counts["Fail"]

                pass_percent = round((pass_count / total_students) * 100, 2)
                fail_percent = round((fail_count / total_students) * 100, 2)

                final_summary[sub] = {
                    "Pass": pass_count,
                    "Fail": fail_count,
                    "Pass%": pass_percent,
                    "Fail%": fail_percent
                }

            return dict(sorted(final_summary.items()))

    except Exception as e:
        return {"Error": f"❌ Error while generating subject summary: {e}"}

def get_subject_toppers_2(csv_file="second_year_subject_totals.csv"):
    """
    Read first-year CSV (including fail students) and find toppers 
    for each subject (_TOTAL columns).
    Returns a list of strings for display:
    "SubjectCode | Name | PRN | Marks: X"
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            headers = reader.fieldnames

        # Identify all subjects by columns ending with '_TOTAL'
        subject_columns = [h for h in headers if h.endswith("_TOTAL")]
        toppers_list = []

        for sub_col in subject_columns:
            sub_code = sub_col.replace("_TOTAL", "")
            max_marks = -1
            top_students = []

            for row in data:
                marks_text = row.get(sub_col, "")
                if marks_text.strip() == "":
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
                    f"{sub_code} | {st['Name']} | {st['PRN']} | Marks: {max_marks}"
                )

        return toppers_list

    except Exception as e:
        return [f"❌ Error fetching subject toppers: {e}"]



from flask import Flask, render_template_string, url_for
import csv
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)

# --------------------------------------------------------
# Function: Generate SGPA Distribution Chart
# --------------------------------------------------------
def get_sgpa_chart(csv_file="first_year_all_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sgpa_str = row.get("SGPA 1", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1  # Invalid SGPA → Treat as fail

        total = sum(categories.values())
        percentages = {
            k: round((v / total) * 100, 2) if total > 0 else 0
            for k, v in categories.items()
        }

        if not os.path.exists("static"):
            os.makedirs("static")

        chart_path = os.path.join("static", "sgpa_chart.png")

        plt.figure(figsize=(10, 6))
        plt.bar(
            percentages.keys(),
            percentages.values(),
            color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                   "#F44336", "#00BCD4", "#9E9E9E", "#795548"]
        )
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("First Year SGPA (Sem 1) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"Error generating chart: {e}")
        return None, {}


# --------------------------------------------------------
# Flask Home Page (Displays Chart Directly)
# --------------------------------------------------------
@app.route('/')
def home():
    chart_path, percentages = get_sgpa_chart()

    # If chart_path failed, make sure it's defined
    if not chart_path:
        chart_path = ""

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
            <p style="color:red;">❌ Chart could not be generated.</p>
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
    </body>
    </html>
    """
    return render_template_string(html_page, chart_path=chart_path, percentages=percentages)


from flask import Flask, render_template_string, url_for
import csv
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)

# --------------------------------------------------------
# Function: Generate SGPA Distribution Chart
# --------------------------------------------------------
def get_sgpa_chart_sem2(csv_file="first_year_all_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sgpa_str = row.get("SGPA 2", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1  # Invalid SGPA → Treat as fail

        total = sum(categories.values())
        percentages = {
            k: round((v / total) * 100, 2) if total > 0 else 0
            for k, v in categories.items()
        }

        if not os.path.exists("static"):
            os.makedirs("static")

        chart_path = os.path.join("static", "sgpa_chart2.png")

        plt.figure(figsize=(10, 6))
        plt.bar(
            percentages.keys(),
            percentages.values(),
            color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                   "#F44336", "#00BCD4", "#9E9E9E", "#795548"]
        )
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("First Year SGPA (Sem 2) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"Error generating chart: {e}")
        return None, {}

# --------------------------------------------------------
# Flask Home Page (Displays Chart Directly)
# --------------------------------------------------------
@app.route('/')
def home():
    chart_path, percentages = get_sgpa_chart_sem2()

    # If chart_path failed, make sure it's defined
    if not chart_path:
        chart_path = ""

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
            <p style="color:red;">❌ Chart could not be generated.</p>
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
    </body>
    </html>
    """
    return render_template_string(html_page, chart_path=chart_path, percentages=percentages)

def get_sgpa_chart_sem1_y2(csv_file="second_year_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sgpa_str = row.get("SGPA 1", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1

        total = sum(categories.values())
        percentages = {k: round((v / total) * 100, 2) if total > 0 else 0 for k, v in categories.items()}

        os.makedirs("static", exist_ok=True)
        chart_path = os.path.join("static", "sgpa_chart_sem1_y2.png")

        plt.figure(figsize=(10, 6))
        plt.bar(percentages.keys(), percentages.values(),
                color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                       "#F44336", "#00BCD4", "#9E9E9E", "#795548"])
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("Second Year SGPA (Sem 1) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"❌ Error generating SGPA chart for Sem1: {e}")
        return None, {}

def get_sgpa_chart_sem2_y2(csv_file="second_year_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sgpa_str = row.get("SGPA 2", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1

        total = sum(categories.values())
        percentages = {k: round((v / total) * 100, 2) if total > 0 else 0 for k, v in categories.items()}

        os.makedirs("static", exist_ok=True)
        chart_path = os.path.join("static", "sgpa_chart_sem2_y2.png")

        plt.figure(figsize=(10, 6))
        plt.bar(percentages.keys(), percentages.values(),
                color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                       "#F44336", "#00BCD4", "#9E9E9E", "#795548"])
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("Second Year SGPA (Sem 2) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"❌ Error generating SGPA chart for Sem2: {e}")
        return None, {}


def get_sgpa_chart_sem3_y2(csv_file="second_year_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sgpa_str = row.get("SGPA 3", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1

        total = sum(categories.values())
        percentages = {k: round((v / total) * 100, 2) if total > 0 else 0 for k, v in categories.items()}

        os.makedirs("static", exist_ok=True)
        chart_path = os.path.join("static", "sgpa_chart_sem3_y2.png")

        plt.figure(figsize=(10, 6))
        plt.bar(percentages.keys(), percentages.values(),
                color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                       "#F44336", "#00BCD4", "#9E9E9E", "#795548"])
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("Second Year SGPA (Sem 3) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"❌ Error generating SGPA chart for Sem3: {e}")
        return None, {}


def get_sgpa_chart_sem4_y2(csv_file="second_year_subject_totals.csv"):
    categories = {
        "Distinction (>=8.5)": 0,
        "O (8.0 - 8.49)": 0,
        "A+ (7.5 - 7.99)": 0,
        "A (7.0 - 7.49)": 0,
        "B+ (6.5 - 6.99)": 0,
        "B (6.0 - 6.49)": 0,
        "C (5.5 - 5.99)": 0,
        "Pass (<5.5)": 0,
        "Fail": 0
    }

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                sgpa_str = row.get("SGPA 4", "").strip()
                result = row.get("Result", "").lower()

                if result == "fail":
                    categories["Fail"] += 1
                    continue

                try:
                    sgpa = float(sgpa_str)
                    if sgpa >= 8.5:
                        categories["Distinction (>=8.5)"] += 1
                    elif 8.0 <= sgpa < 8.5:
                        categories["O (8.0 - 8.49)"] += 1
                    elif 7.5 <= sgpa < 8.0:
                        categories["A+ (7.5 - 7.99)"] += 1
                    elif 7.0 <= sgpa < 7.5:
                        categories["A (7.0 - 7.49)"] += 1
                    elif 6.5 <= sgpa < 7.0:
                        categories["B+ (6.5 - 6.99)"] += 1
                    elif 6.0 <= sgpa < 6.5:
                        categories["B (6.0 - 6.49)"] += 1
                    elif 5.5 <= sgpa < 6.0:
                        categories["C (5.5 - 5.99)"] += 1
                    elif 0 <= sgpa < 5.5:
                        categories["Pass (<5.5)"] += 1
                except ValueError:
                    categories["Fail"] += 1

        total = sum(categories.values())
        percentages = {k: round((v / total) * 100, 2) if total > 0 else 0 for k, v in categories.items()}

        os.makedirs("static", exist_ok=True)
        chart_path = os.path.join("static", "sgpa_chart_sem4_y2.png")

        plt.figure(figsize=(10, 6))
        plt.bar(percentages.keys(), percentages.values(),
                color=["#4CAF50", "#2196F3", "#9C27B0", "#FFEB3B", "#FF9800",
                       "#F44336", "#00BCD4", "#9E9E9E", "#795548"])
        plt.xlabel("SGPA Category", fontsize=12)
        plt.ylabel("Percentage of Students (%)", fontsize=12)
        plt.title("Second Year SGPA (Sem 4) Result Distribution", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        return chart_path, percentages

    except Exception as e:
        print(f"❌ Error generating SGPA chart for Sem4: {e}")
        return None, {}
