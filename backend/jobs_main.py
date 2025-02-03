import asyncio
import logging
import random
import time
import sys
import os
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URL for saving jobs
API_URL = "https://jmagz.xyz/api/jobs"

# Ensure the console uses UTF-8 encoding
sys.stdout.reconfigure(encoding="utf-8")

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

BASE_URL = "https://uk.indeed.com"

# Combine job titles into a single search query with OR logic
job_titles = [
    "Frontend Web Developer",
    "Vuejs Web Developer",
    "Website Developer",
    "DevOps Engineer",
    "AWS DevOps Engineer",
    "Site Reliability Engineer"
]
search_query = " OR ".join([f'"{title}"' for title in job_titles])

# 🔁 Function to Save Scraped Job via API
async def save_to_api(job):
    """Send the job data to the API for saving into the RDS."""
    try:
        response = requests.post(API_URL, json=job)
        if response.status_code == 201:
            logging.info(f"📄 Job successfully saved to API: {job['title']}")
        else:
            logging.error(f"❌ Failed to save job: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"⚠️ Error sending job to API: {e}")

# 🔁 Function to Fetch Job Details
# ✅ Function to Fetch Job Details with Updated Selectors
async def fetch_job_details(browser, url, retries=3):
    """Fetch job details from the job's individual page."""
    for attempt in range(retries):
        try:
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")

            # Updated Selectors
            try:
                title = await page.locator("h2[data-testid='simpler-jobTitle']").text_content(timeout=5000)
            except:
                title = "N/A"
                logging.warning(f"Title not found for {url}")

            try:
                location = await page.locator("div[data-testid='jobsearch-JobInfoHeader-companyLocation']").text_content(timeout=5000)
            except:
                location = "N/A"
                logging.warning(f"Location not found for {url}")

            try:
                description = await page.locator("#jobDescriptionText").text_content(timeout=10000)
            except:
                description = "N/A"
                logging.warning(f"Description not found for {url}")

            try:
                company = await page.locator("div[data-company-name='true'] a").text_content(timeout=5000)
            except:
                company = "N/A"
                logging.warning(f"Company not found for {url}")

            await page.close()
            await context.close()

            return {
                "title": title.strip() if title else "N/A",
                "location": location.strip() if location else "N/A",
                "description": description.strip() if description else "N/A",
                "company": company.strip() if company else "N/A",
            }
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}/{retries}: Failed to fetch details for {url} - {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    # Return N/A if all retries fail
    return {"title": "N/A", "location": "N/A", "description": "N/A", "company": "N/A"}



# 🔁 Main Scraping Function
async def scrape_jobs_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        all_jobs_data = []

        search_url = f"{BASE_URL}/jobs?q={search_query.replace(' ', '+')}&l=London&radius=25&jt=fulltime&fromage=7"
        current_page_url = search_url

        while current_page_url:
            page = await browser.new_page()
            await page.goto(current_page_url, timeout=60000)
            logging.info(f"🔎 Scraping page: {current_page_url}")
            logging.info("🔖 Page title: %s", await page.title())

            job_elements = await page.locator(".jcs-JobTitle").all()
            logging.info(f"🔍 Found {len(job_elements)} job elements.")

            # Process jobs on the current page
            for job_element in job_elements:
                try:
                    list_title = await job_element.locator("span[id^='jobTitle']").text_content(timeout=5000) or "N/A"
                    relative_url = await job_element.get_attribute("href", timeout=10000)
                    absolute_url = urljoin(BASE_URL, relative_url)

                    logging.info(f"🔢 Fetching details for URL: {absolute_url}")
                    details = await fetch_job_details(browser, absolute_url)

                    if details["title"] == "N/A":
                        details["title"] = list_title.strip()

                    job_data = {
                        "url": absolute_url,
                        **details
                    }

                    all_jobs_data.append(job_data)
                    await save_to_api(job_data)  # 🔁 Save to API

                    delay = random.uniform(3, 7)  # Simulate human-like behavior
                    logging.info(f"💤 Waiting for {delay:.2f} seconds before next job.")
                    time.sleep(delay)

                except Exception as e:
                    logging.error(f"❌ Error processing job on page {current_page_url}: {e}")

            # Check for Next Page
            try:
                next_button = page.locator("a[data-testid='pagination-page-next']")
                if await next_button.is_visible():
                    next_page_relative_url = await next_button.get_attribute("href")
                    current_page_url = urljoin(BASE_URL, next_page_relative_url)
                else:
                    current_page_url = None
            except Exception as e:
                logging.error(f"❌ Error finding next page link: {e}")
                current_page_url = None

            await page.close()

        await browser.close()

        # Save scraped jobs to a text file
        with open("job_details.txt", "w", encoding="utf-8") as file:
            for i, job in enumerate(all_jobs_data, start=1):
                job_info = (
                    f"Job {i}:\n"
                    f"  Title: {job['title']}\n"
                    f"  URL: {job['url']}\n"
                    f"  Location: {job['location']}\n"
                    f"  Company: {job['company']}\n"
                    f"  Description: {job['description']}\n\n"
                )
                print(job_info)
                file.write(job_info)

if __name__ == "__main__":
    asyncio.run(scrape_jobs_with_playwright())
