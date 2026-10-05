"""Generate 3 sample CV PDFs for testing HireScope AI."""
from fpdf import FPDF


def make_cv(filename, name, email, phone, title, summary, skills, experience, education):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"{email} | {phone}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, summary)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Skills", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, ", ".join(skills))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Experience", new_x="LMARGIN", new_y="NEXT")
    for job, desc in experience:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, job, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, desc)
        pdf.ln(1)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Education", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, education)

    pdf.output(filename)
    print(f"Created {filename}")


# CV 1 - strong Python/Django match
make_cv(
    "cv_ahmed_khan.pdf",
    "Ahmed Khan",
    "ahmed.khan@email.com",
    "+92-300-1234567",
    "Senior Python Developer",
    "Results-driven Python developer with 4 years of experience building scalable web applications with Django and REST APIs.",
    ["Python", "Django", "Django REST Framework", "PostgreSQL", "REST APIs", "Docker", "Git", "Redis"],
    [
        ("Senior Python Developer - TechSolutions Karachi (2022-Present)",
         "Built REST APIs serving 100k+ requests/day using Django REST Framework and PostgreSQL. Led a team of 3 developers."),
        ("Python Developer - StartupHub Lahore (2020-2022)",
         "Developed e-commerce backend with Django, integrated payment gateways, optimized PostgreSQL queries."),
    ],
    "BS Computer Science, FAST NUCES (2016-2020)",
)

# CV 2 - frontend, weak match for Python role
make_cv(
    "cv_sara_ahmed.pdf",
    "Sara Ahmed",
    "sara.ahmed@email.com",
    "+92-321-7654321",
    "Frontend Developer",
    "Creative frontend developer with 2 years of experience crafting responsive UIs with React and modern JavaScript.",
    ["JavaScript", "React", "HTML", "CSS", "Tailwind CSS", "Figma", "Git"],
    [
        ("Frontend Developer - DesignStudio Karachi (2023-Present)",
         "Built responsive dashboards with React and Tailwind CSS. Collaborated with designers in Figma."),
        ("Junior Web Developer - WebWorks (2022-2023)",
         "Maintained company websites, converted Figma designs to HTML and CSS."),
    ],
    "BS Software Engineering, NED University (2018-2022)",
)

# CV 3 - junior Python, medium match
make_cv(
    "cv_bilal_hussain.pdf",
    "Bilal Hussain",
    "bilal.h@email.com",
    "+92-333-9876543",
    "Junior Python Developer",
    "Motivated Python developer with 1 year of experience in Flask and Django, eager to grow in backend development.",
    ["Python", "Flask", "Django", "SQLite", "HTML", "Git"],
    [
        ("Junior Python Developer - SoftTech Islamabad (2024-Present)",
         "Built internal tools with Flask, wrote REST endpoints, worked with SQLite databases."),
    ],
    "BS Computer Science, COMSATS (2020-2024)",
)
