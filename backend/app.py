from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from docx import Document
import os
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "html",
    "css",
    "sql",
    "mysql",
    "mongodb",
    "postgresql",
    "git",
    "github",
    "flask",
    "django",
    "spring boot",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "c",
    "c++",
    "c#",
    "android",
    "kotlin",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "rest api",
    "firebase",
    "figma",
    "excel",
    "power bi",
    "tensorflow",
    "pytorch"
]


STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from",
    "have", "will", "your", "you", "our", "are", "was",
    "were", "has", "had", "not", "but", "all", "any",
    "can", "job", "role", "work", "working", "using",
    "into", "their", "they", "them", "about", "which",
    "who", "what", "where", "when", "how", "should",
    "must", "need", "years", "year", "skills"
}


def extract_pdf_text(filepath):
    reader = PdfReader(filepath)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(filepath):
    document = Document(filepath)
    text = ""

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


def extract_text(filepath, extension):

    if extension == ".pdf":
        return extract_pdf_text(filepath)

    if extension == ".docx":
        return extract_docx_text(filepath)

    raise ValueError("Only PDF and DOCX files are supported")


def detect_skills(text):
    text_lower = text.lower()
    found = []

    for skill in SKILLS:

        if skill.lower() in text_lower:
            found.append(skill)

    return sorted(set(found))


def extract_keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords[:30]


def analyze_sections(text):

    text_lower = text.lower()

    sections = {
        "contact": False,
        "education": False,
        "experience": False,
        "skills": False,
        "projects": False,
        "certifications": False,
        "summary": False
    }

    if (
        "@" in text
        or "phone" in text_lower
        or "mobile" in text_lower
        or "linkedin" in text_lower
    ):
        sections["contact"] = True

    if "education" in text_lower:
        sections["education"] = True

    if (
        "experience" in text_lower
        or "work experience" in text_lower
        or "internship" in text_lower
    ):
        sections["experience"] = True

    if "skills" in text_lower or "technical skills" in text_lower:
        sections["skills"] = True

    if "projects" in text_lower or "project" in text_lower:
        sections["projects"] = True

    if (
        "certification" in text_lower
        or "certifications" in text_lower
    ):
        sections["certifications"] = True

    if (
        "summary" in text_lower
        or "objective" in text_lower
        or "profile" in text_lower
    ):
        sections["summary"] = True

    return sections


def calculate_resume_score(text, skills, sections):

    score = 0

    # Skills: maximum 30
    score += min(len(skills) * 3, 30)

    # Sections: maximum 50
    for exists in sections.values():

        if exists:
            score += 7

    # Resume length/content: maximum 20
    word_count = len(text.split())

    if word_count >= 300:
        score += 20

    elif word_count >= 150:
        score += 12

    elif word_count >= 75:
        score += 7

    return min(score, 100)


def generate_strengths(skills, sections):

    strengths = []

    if len(skills) >= 8:
        strengths.append(
            "Strong technical skill coverage."
        )

    elif len(skills) >= 4:
        strengths.append(
            "Good technical skill coverage."
        )

    if sections["projects"]:
        strengths.append(
            "Projects section is included."
        )

    if sections["experience"]:
        strengths.append(
            "Experience or internship information is present."
        )

    if sections["education"]:
        strengths.append(
            "Education information is present."
        )

    if sections["certifications"]:
        strengths.append(
            "Certifications are included."
        )

    if sections["contact"]:
        strengths.append(
            "Contact information appears to be available."
        )

    if not strengths:
        strengths.append(
            "Resume text was successfully extracted."
        )

    return strengths


def generate_weaknesses(skills, sections, text):

    weaknesses = []

    if len(skills) < 4:
        weaknesses.append(
            "Add more relevant technical skills."
        )

    if not sections["summary"]:
        weaknesses.append(
            "Consider adding a professional summary."
        )

    if not sections["projects"]:
        weaknesses.append(
            "Add a projects section with measurable outcomes."
        )

    if not sections["experience"]:
        weaknesses.append(
            "Add internship or work experience if available."
        )

    if not sections["certifications"]:
        weaknesses.append(
            "Add relevant certifications if available."
        )

    if len(text.split()) < 150:
        weaknesses.append(
            "The resume appears to contain limited content."
        )

    return weaknesses


def generate_suggestions():

    return [
        "Customize the resume for each job description.",
        "Use measurable achievements wherever possible.",
        "Include relevant technical keywords from the job description.",
        "Keep project descriptions concise and result-oriented.",
        "Use clear section headings and consistent formatting."
    ]


def calculate_ats_match(resume_text, job_description):

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    resume_skills = set(detect_skills(resume_text))
    job_skills = set(detect_skills(job_description))

    matched_skills = sorted(
        resume_skills.intersection(job_skills)
    )

    missing_skills = sorted(
        job_skills - resume_skills
    )

    if job_skills:

        skill_score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

    else:

        job_keywords = set(
            extract_keywords(job_description)
        )

        resume_words = set(
            extract_keywords(resume_text)
        )

        matched_keywords = job_keywords.intersection(
            resume_words
        )

        if job_keywords:

            skill_score = (
                len(matched_keywords)
                / len(job_keywords)
            ) * 100

        else:

            skill_score = 0

    keyword_score = 0

    job_keywords = set(
        extract_keywords(job_description)
    )

    resume_words = set(
        extract_keywords(resume_text)
    )

    if job_keywords:

        keyword_score = (
            len(job_keywords.intersection(resume_words))
            / len(job_keywords)
        ) * 100

    ats_score = round(
        (skill_score * 0.7) +
        (keyword_score * 0.3)
    )

    return {
        "ats_score": min(ats_score, 100),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": sorted(
            job_keywords.intersection(resume_words)
        )[:20]
    }


@app.route("/")
def home():

    return jsonify({
        "message": "AI Resume Analyzer API is running"
    })


@app.route("/api/health")
def health():

    return jsonify({
        "status": "healthy"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_resume():

    if "resume" not in request.files:

        return jsonify({
            "error": "Please upload a resume."
        }), 400

    resume = request.files["resume"]

    if resume.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400

    extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if extension not in [".pdf", ".docx"]:

        return jsonify({
            "error": "Only PDF and DOCX files are supported."
        }), 400

    filepath = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )

    try:

        resume.save(filepath)

        if os.path.getsize(filepath) > MAX_FILE_SIZE:

            os.remove(filepath)

            return jsonify({
                "error": "File size must be below 5 MB."
            }), 400

        text = extract_text(
            filepath,
            extension
        )

        if not text.strip():

            return jsonify({
                "error": "Could not extract text from the resume."
            }), 400

        skills = detect_skills(text)

        sections = analyze_sections(text)

        score = calculate_resume_score(
            text,
            skills,
            sections
        )

        strengths = generate_strengths(
            skills,
            sections
        )

        weaknesses = generate_weaknesses(
            skills,
            sections,
            text
        )

        suggestions = generate_suggestions()

        return jsonify({

            "message": "Resume analyzed successfully",

            "filename": resume.filename,

            "text_length": len(text),

            "analysis": {

                "score": score,

                "skills": skills,

                "sections": sections,

                "strengths": strengths,

                "weaknesses": weaknesses,

                "suggestions": suggestions,

                "keywords": extract_keywords(text)

            },

            "extracted_text": text[:5000]

        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/match", methods=["POST"])
def match_job():

    if "resume" not in request.files:

        return jsonify({
            "error": "Please upload a resume."
        }), 400

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if not job_description:

        return jsonify({
            "error": "Please enter a job description."
        }), 400

    resume = request.files["resume"]

    if resume.filename == "":

        return jsonify({
            "error": "No resume selected."
        }), 400

    extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if extension not in [".pdf", ".docx"]:

        return jsonify({
            "error": "Only PDF and DOCX files are supported."
        }), 400

    filepath = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )

    try:

        resume.save(filepath)

        resume_text = extract_text(
            filepath,
            extension
        )

        result = calculate_ats_match(
            resume_text,
            job_description
        )

        return jsonify(result)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )