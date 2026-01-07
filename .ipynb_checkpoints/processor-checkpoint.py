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

import csv

def get_top5_students(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV, sort students by CGPA, and return top 5 students as a list of strings.
    Each string: "Name | PRN | CGPA"
    """
    try:
        students = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["Name"]
                prn = row["PRN"]
                cgpa = float(row["CGPA"])
                students.append({"Name": name, "PRN": prn, "CGPA": cgpa})

        # Sort descending by CGPA
        top5 = sorted(students, key=lambda x: x["CGPA"], reverse=True)[:5]

        # Format for display
        top5_list = [f"{i+1}. {s['Name']} | {s['PRN']} | CGPA: {s['CGPA']}" for i, s in enumerate(top5)]
        return top5_list

    except Exception as e:
        return [f"❌ Error fetching top 5 students: {e}"]
import csv

def get_subject_toppers(csv_file="first_year_subject_totals.csv"):
    """
    Read first-year CSV and find toppers for each subject (_TOTAL columns).
    Returns a list of strings for display:
    "SubjectCode | Name | PRN | Marks"
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            headers = reader.fieldnames

        # Identify all subjects by looking for columns ending with '_TOTAL'
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
                toppers_list.append(f"{sub_code} | {st['Name']} | {st['PRN']} | Marks: {max_marks}")

        return toppers_list

    except Exception as e:
        return [f"❌ Error fetching subject toppers: {e}"]
