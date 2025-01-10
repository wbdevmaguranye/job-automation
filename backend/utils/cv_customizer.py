from docx import Document
import os
from spacy import load

nlp = load("en_core_web_sm")

PREDEFINED_SKILLS = [
    "Jenkins", "Kubernetes", "GitOps", "EKS", "RDS", "Terraform", "AWS",
    "Azure", "SQL", "MongoDB", "Python", "Groovy", "Spring Boot", ".NET Core",
    "Argo Rollouts", "Helm", "CI/CD", "Velero", "Istio", "Lua"
]

def extract_skills_from_description(job_description, predefined_skills):
    """
    Extract relevant skills from the job description based on a predefined list of skills.
    :param job_description: String containing the job description.
    :param predefined_skills: List of predefined skills to match.
    :return: List of matched skills.
    """
    matched_skills = []
    for skill in predefined_skills:
        if skill.lower() in job_description.lower():
            matched_skills.append(skill)
    return matched_skills

def customize_cv(template_path, output_path, replacements):
    """
    Customize the CV template by replacing placeholders with specific content.
    :param template_path: Path to the CV template.
    :param output_path: Path to save the customized CV.
    :param replacements: Dictionary of placeholders and their replacements.
    """
    try:
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
            for placeholder, value in replacements.items():
                if placeholder in paragraph.text:
                    print(f"Before replacement: {paragraph.text}")
                    paragraph.text = paragraph.text.replace(placeholder, value)
                    print(f"After replacement: {paragraph.text}")

        # Save the customized CV
        doc.save(output_path)

        print(f"File successfully written: {output_path}")
    except Exception as e:
        print(f"Error customizing CV: {e}")

def generate_cv(job, template_type, output_dir="static/customized_cvs"):
    """
    Generate a customized CV based on the job description and template type.
    :param job: Dictionary containing job details (title, description, etc.).
    :param template_type: 'frontend' or 'devops' to determine the template.
    :param output_dir: Directory to save the customized CV.
    :return: Path to the customized CV.
    """
    # Get the absolute path to the project root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Build the template file path relative to the root directory
    template_file = os.path.join(root_dir, "backend", "templates", f"{template_type}_cv_template.docx")

    # Debug prints
    print(f"Template path: {template_file}")
    print(f"File exists: {os.path.exists(template_file)}")

    # Build the output directory path relative to the root directory
    output_dir_path = os.path.join(root_dir, output_dir)

    # Ensure the output directory exists
    os.makedirs(output_dir_path, exist_ok=True)
    print(f"Output directory ensured: {output_dir_path}")

    # Construct the output file path
    output_file = os.path.join(
        output_dir_path,
        f"{job['title'].replace(' ', '_')}_CV.docx"
    )

    # Extract skills from the job description
    description = job.get("description", "N/A")
    skills = extract_skills_from_description(description, PREDEFINED_SKILLS)
    skills_str = ", ".join(skills) if skills else "No specific skills found"

    replacements = {
        "{job_title}": job.get("title", "N/A"),
        "{skills}": skills_str,
        "{job_duties}": description,
        "{company}": job.get("company", "N/A"),
        "{location}": job.get("location", "N/A"),
    }

    # Customize the CV and save it to the output file
    customize_cv(template_file, output_file, replacements)

    # Debugging: Confirm the output file path
    print(f"File successfully written: {output_file}")
    print(f"Absolute path of the saved CV: {os.path.abspath(output_file)}")

    return output_file
