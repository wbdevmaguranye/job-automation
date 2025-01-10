from docx import Document
from docx.shared import Pt
import os
from spacy import load

nlp = load("en_core_web_sm")

# Predefined categories and skills
PREDEFINED_CATEGORIES = {
    "Cloud Platforms": [
        "EC2", "S3", "RDS", "Lambda", "VPC", "AWS CloudFormation", "Azure Resource Manager",
        "CDK", "networking", "security", "IAM configurations"
    ],
    "CI/CD Tools": [
        "Jenkins", "GitLab CI/CD", "GitHub Actions", "CircleCI"
    ],
    "Infrastructure as Code (IaC) Tools": [
        "Terraform", "Ansible", "CloudFormation", "Bicep"
    ],
    "Monitoring Tools": [
        "Prometheus", "Grafana", "Datadog", "New Relic"
    ]
}

def extract_relevant_skills(job_description, predefined_categories):
    """
    Extract relevant skills from the job description for each predefined category.
    :param job_description: String containing the job description.
    :param predefined_categories: Dictionary of categories and their associated skills.
    :return: Dictionary with matched skills per category.
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
    :param original_summary: Original professional summary text.
    :param matched_skills: Dictionary with matched skills per category.
    :return: Customized professional summary.
    """
    summary = original_summary

    # Customize cloud platforms
    if matched_skills["Cloud Platforms"]:
        cloud_skills = ", ".join(matched_skills["Cloud Platforms"])
        summary = summary.replace("cloud platforms", f"Proficient in leveraging AWS services such as  {cloud_skills} to build scalable and reliable solutions." )

    # Customize CI/CD tools
    if matched_skills["CI/CD Tools"]:
        ci_cd_skills = ", ".join(matched_skills["CI/CD Tools"])
        summary = summary.replace("CI/CD pipelines", f"Proficient in designing and implementing CI/CD pipelines using tools like  {ci_cd_skills} to streamline software delivery processes." )

    # Customize IaC tools
    if matched_skills["Infrastructure as Code (IaC) Tools"]:
        iac_skills = ", ".join(matched_skills["Infrastructure as Code (IaC) Tools"])
        summary += f" Skilled in Infrastructure as Code (IaC) tools like {iac_skills} for efficient and repeatable infrastructure management."

    # Customize monitoring tools
    if matched_skills["Monitoring Tools"]:
        monitoring_skills = ", ".join(matched_skills["Monitoring Tools"])
        summary += f" Experienced in implementing robust monitoring solutions using tools like {monitoring_skills} to ensure system reliability and performance."

    return summary


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
    # Paths and setup
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template_file = os.path.join(root_dir, "backend", "templates", f"{template_type}_cv_template.docx")
    output_dir_path = os.path.join(root_dir, output_dir)
    os.makedirs(output_dir_path, exist_ok=True)
    output_file = os.path.join(output_dir_path, f"Joel Maguranye {job['title'].replace(' ', '_')}_CV.docx")

    # Extract matched skills
    description = job.get("description", "N/A")
    matched_skills = extract_relevant_skills(description, PREDEFINED_CATEGORIES)

    # Original summary
    original_summary = (
        "DevOps Engineer with over 5 years of experience in cloud infrastructure, specializing in CI/CD pipelines, and infrastructure automation."
        
    )
    customized_summary = customize_summary(original_summary, matched_skills)

    # Prepare replacements
    replacements = {
        "{job_title}": job.get("title", "N/A"),
        "{skills}": ", ".join([", ".join(skills) for skills in matched_skills.values() if skills]),
        "{professional_summary}": customized_summary,
        "{job_duties}": description,
        "{company}": job.get("company", "N/A"),
        "{location}": job.get("location", "N/A"),
    }

    # Customize the CV
    customize_cv(template_file, output_file, replacements)

    return output_file
