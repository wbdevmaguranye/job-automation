import logging
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# Keywords for filtering
FRONTEND_KEYWORDS = ["Frontend", "VueJS", "JavaScript", "React", "CSS", "HTML"]
DEVOPS_KEYWORDS = ["DevOps", "Site Reliability", "AWS", "Jenkins", "Kubernetes"]

def matches_keywords(title, keywords):
    """Check if the job title contains any of the specified keywords."""
    return any(keyword.lower() in title.lower() for keyword in keywords)

def scrape_jobs_with_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36"
    )

    driver = uc.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    jobs_data = []

    try:
        driver.get("https://uk.indeed.com/jobs?q=developer&l=")
        logging.info("Page title: %s", driver.title)

        # Wait for job elements to load
        job_elements = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jcs-JobTitle"))
        )
        logging.info("Found %d job elements on the page.", len(job_elements))

        for job_element in job_elements:
            try:
                title = job_element.text
                url = job_element.get_attribute("href")

                # Filter jobs based on keywords
                if not (matches_keywords(title, FRONTEND_KEYWORDS) or matches_keywords(title, DEVOPS_KEYWORDS)):
                    logging.info("Skipping job: %s (No matching keywords)", title)
                    continue

                logging.info("Processing job: %s", title)

                # Navigate to job URL to extract detailed information
                driver.get(url)
                time.sleep(random.uniform(2, 4))  # Random delay to avoid detection

                # Extract job details
                job_description = driver.find_element(By.ID, "jobDescriptionText").text
                location = driver.find_element(By.ID, "jobLocationText").text if driver.find_elements(By.ID, "jobLocationText") else "Not specified"
                pay = driver.find_element(By.XPATH, "//div[@role='group' and contains(., 'Pay')]").text if driver.find_elements(By.XPATH, "//div[@role='group' and contains(., 'Pay')]") else "Not specified"
                benefits = driver.find_element(By.ID, "benefits").text if driver.find_elements(By.ID, "benefits") else "Not specified"

                job_data = {
                    "title": title,
                    "url": url,
                    "description": job_description,
                    "location": location,
                    "pay": pay,
                    "benefits": benefits,
                }
                jobs_data.append(job_data)
                logging.info("Extracted details for job: %s", title)

                # Navigate back to the job listing page
                driver.back()
                time.sleep(random.uniform(2, 3))

            except Exception as e:
                logging.error("Error extracting job: %s", str(e))
                # Add partial job data with error marker
                jobs_data.append({"title": title, "url": url, "error": str(e)})

        # Handle pagination
        try:
            while True:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']"))
                )
                next_button.click()
                time.sleep(random.uniform(3, 5))  # Random delay

                # Process the next page of jobs
                job_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "jcs-JobTitle"))
                )
                logging.info("Found %d job elements on the next page.", len(job_elements))
        except Exception as e:
            logging.info("No more pages or pagination error: %s", str(e))

        logging.info("Final Scraped Jobs: %d", len(jobs_data))
        return jobs_data

    finally:
        # Ensure the driver quits gracefully
        try:
            if driver:
                driver.quit()
        except Exception as e:
            logging.error("Error while quitting the driver: %s", str(e))


if __name__ == "__main__":
    jobs_data = scrape_jobs_with_selenium()
    logging.info("Scraped %d jobs.", len(jobs_data))

    # Print the job details
    for i, job in enumerate(jobs_data, start=1):
        print(f"Job {i}:")
        for key, value in job.items():
            print(f"  {key.capitalize()}: {value}")
        print()
