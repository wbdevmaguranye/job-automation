import asyncio
import logging
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import random
import time
import sys
from database import get_connection  # Import your database connection function

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

async def fetch_job_details(browser, url, retries=3):
    """Fetch job details from the job's individual page using specific IDs."""
    for attempt in range(retries):
        try:
            # Open a new context and page for each job
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")

            # Extract details using IDs
            location = await page.locator("#jobLocationText").text_content(timeout=5000) or "N/A"
            try:
                title = await page.locator("h2[data-testid='jobsearch-JobInfoHeader-title']").text_content(timeout=5000)
            except:
                title = "N/A"

            description = await page.locator("#jobDescriptionText").text_content(timeout=10000) or "N/A"
            try:
                company = await page.locator("div[data-company-name='true'] a").text_content(timeout=5000)
            except:
                company = "N/A"

            # Close the context and page
            await page.close()
            await context.close()

            return {
                "title": title.strip(),
                "location": location.strip(),
                "description": description.strip(),
                "company": company.strip(),
            }
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}/{retries}: Failed to fetch details for {url} - {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    return {"title": "N/A", "location": "N/A", "description": "N/A", "company": "N/A"}

async def save_to_database(job):
    """Save job details into the database."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO Jobs (title, location, description, company, url)
            VALUES (%s, %s, %s, %s, %s)
        """, (job['title'], job['location'], job['description'], job['company'], job['url']))
        connection.commit()
        logging.info("Job saved to database: %s", job['title'])
    except Exception as e:
        logging.error(f"Failed to save job to database: {e}")
    finally:
        cursor.close()
        connection.close()

async def scrape_jobs_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        all_jobs_data = []

        # Build search URL with OR logic
        search_url = f"{BASE_URL}/jobs?q={search_query.replace(' ', '+')}&l=London&radius=25&jt=fulltime&fromage=7"
        current_page_url = search_url

        while current_page_url:
            page = await browser.new_page()
            await page.goto(current_page_url, timeout=60000)
            logging.info(f"Scraping page: {current_page_url}")
            logging.info("Page title: %s", await page.title())

            job_elements = await page.locator(".jcs-JobTitle").all()
            logging.info(f"Found {len(job_elements)} job elements.")

            # Process jobs on the current page
            for job_element in job_elements:
                try:
                    # Extract title directly from the job list as a fallback
                    list_title = await job_element.locator("span[id^='jobTitle']").text_content(timeout=5000) or "N/A"
                    relative_url = await job_element.get_attribute("href", timeout=10000)
                    absolute_url = urljoin(BASE_URL, relative_url)

                    logging.info(f"Fetching details for URL: {absolute_url}")
                    details = await fetch_job_details(browser, absolute_url)

                    # Override title if the detailed page title is more descriptive
                    if details["title"] == "N/A":
                        details["title"] = list_title.strip()

                    job_data = {
                        "url": absolute_url,
                        **details
                    }

                    all_jobs_data.append(job_data)
                    await save_to_database(job_data)  # Save job data to the database

                    # Simulate human behavior by adding a random delay between requests
                    delay = random.uniform(3, 7)  # Wait between 3 to 7 seconds
                    logging.info(f"Waiting for {delay:.2f} seconds before processing the next job.")
                    time.sleep(delay)

                except Exception as e:
                    logging.error(f"Error processing job on page {current_page_url}: {e}")

            # Check if there's a "Next Page" link
            try:
                next_button = page.locator("a[data-testid='pagination-page-next']")
                if await next_button.is_visible():
                    next_page_relative_url = await next_button.get_attribute("href")
                    current_page_url = urljoin(BASE_URL, next_page_relative_url)
                else:
                    current_page_url = None  # No more pages to scrape
            except Exception as e:
                logging.error(f"Error finding next page link: {e}")
                current_page_url = None  # Stop the loop if there's an error

            await page.close()

        # Close the browser
        await browser.close()

        # Print all jobs
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
                print(job_info)  # Ensure UTF-8 encoding
                file.write(job_info)

if __name__ == "__main__":
    asyncio.run(scrape_jobs_with_playwright())
