from docx import Document
from docx.shared import Pt
import os
import re

# Predefined categories and skills
PREDEFINED_CATEGORIES = {
    "Cloud Platforms": ["EC2", "S3", "RDS", "Lambda", "VPC", "AWS CloudFormation"],
    "CI/CD Tools": ["Jenkins", "GitLab CI/CD", "GitHub Actions", "CircleCI"],
    "Infrastructure as Code (IaC) Tools": ["Terraform", "Ansible", "CloudFormation"],
    "Monitoring Tools": ["Prometheus", "Grafana", "Datadog", "New Relic"],
}


def sanitize_filename(filename):
    """
    Remove or replace invalid characters from the filename.
    """
    return re.sub(r'[<>:"/\\|?*$,]', '_', filename)


def extract_relevant_skills(job_description, predefined_categories):
    """
    Extract relevant skills from the job description for each predefined category.
    """
    matched_skills = {category: [] for category in predefined_categories}
    for category, skills in predefined_categories.items():
        for skill in skills:
            if skill.lower() in job_description.lower():
                matched_skills[category].append(skill)
    return matched_skills


def customize_summary(original_summary, matched_skills):
    """
    Customize the professional summary by incorporating matched skills.
    """
    summary = original_summary
    if matched_skills["Cloud Platforms"]:
        cloud_skills = ", ".join(matched_skills["Cloud Platforms"])
        summary += f" Proficient in leveraging cloud platforms such as {cloud_skills}."
    if matched_skills["CI/CD Tools"]:
        ci_cd_skills = ", ".join(matched_skills["CI/CD Tools"])
        summary += f" Experienced in CI/CD pipelines using tools like {ci_cd_skills}."
    if matched_skills["Infrastructure as Code (IaC) Tools"]:
        iac_skills = ", ".join(matched_skills["Infrastructure as Code (IaC) Tools"])
        summary += f" Skilled in IaC tools like {iac_skills}."
    if matched_skills["Monitoring Tools"]:
        monitoring_skills = ", ".join(matched_skills["Monitoring Tools"])
        summary += f" Experienced in monitoring tools like {monitoring_skills}."
    return summary


def customize_cv(template_path, output_path, replacements):
    """
    Customize the CV template by replacing placeholders with specific content.
    """
    try:
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
            for placeholder, value in replacements.items():
                if placeholder in paragraph.text:
                    paragraph.text = paragraph.text.replace(placeholder, value)
                     # Save original formatting
                    is_bold = any(run.bold for run in paragraph.runs)
                    is_underline = any(run.underline for run in paragraph.runs)
                    font_size = next((run.font.size for run in paragraph.runs if run.font.size), Pt(11))  # Default size is 11pt

                    # Clear the paragraph text
                    paragraph.text = ""

                    # Add new text with normal formatting
                    new_run = paragraph.add_run(value)
                    new_run.font.size = font_size
                    new_run.bold = False  # Ensure the new text is not bold
                    new_run.underline = False  # Ensure the new text is not underlined
                    
        doc.save(output_path)
        print(f"File successfully written: {output_path}")
    except Exception as e:
        print(f"Error customizing CV: {e}")


def generate_cv(job, template_type, output_dir):
    """
    Generate a customized CV based on the job description and template type.
    Save the CV locally and return the path.
    """
    # Root directory and template path
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_file = os.path.join(root_dir, "templates", f"{template_type}_cv_template.docx")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate a sanitized filename for the CV
    sanitized_title = sanitize_filename(job['title'])
    output_file = os.path.join(output_dir, f"Joel_Maguranye_{sanitized_title}_CV.docx")

    # Check if the template exists
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Extract matched skills
    description = job.get("description", "N/A")
    matched_skills = extract_relevant_skills(description, PREDEFINED_CATEGORIES)

    # Prepare the summary and replacements
    original_summary = "DevOps Engineer with over 5 years of experience in cloud infrastructure, specializing in CI/CD pipelines and infrastructure automation."
    customized_summary = customize_summary(original_summary, matched_skills)

    replacements = {
        "{job_title}": job.get("title", "N/A"),
        "{skills}": ", ".join([", ".join(skills) for skills in matched_skills.values() if skills]),
        "{professional_summary}": customized_summary,
        "{job_duties}": description,
        "{company}": job.get("company", "N/A"),
        "{location}": job.get("location", "N/A"),
    }

    # Customize the CV and save locally
    customize_cv(template_file, output_file, replacements)
    print(f"CV saved locally at: {output_file}")
    return output_file

