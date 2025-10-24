import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Chrome options ---
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

search_queries = [
    # Morocco - English / French / Arabic
    {"keywords": "data science internship", "location": "Morocco"},
    {"keywords": "data scientist internship", "location": "Morocco"},
    {"keywords": "data engineer internship", "location": "Morocco"},
    {"keywords": "machine learning internship", "location": "Morocco"},
    {"keywords": "machine learning engineer internship", "location": "Morocco"},
    {"keywords": "AI internship", "location": "Morocco"},
    {"keywords": "artificial intelligence internship", "location": "Morocco"},
    {"keywords": "internship PFE data science", "location": "Morocco"},
    {"keywords": "stage science des données", "location": "Morocco"},
    {"keywords": "stage data engineering", "location": "Morocco"},
    {"keywords": "stage PFE data", "location": "Morocco"},
    # France - English / French
    {"keywords": "data science internship", "location": "France"},
    {"keywords": "data scientist internship", "location": "France"},
    {"keywords": "data engineering internship", "location": "France"},
    {"keywords": "data engineer internship", "location": "France"},
    {"keywords": "machine learning internship", "location": "France"},
    {"keywords": "machine learning engineer internship", "location": "France"},
    {"keywords": "AI internship", "location": "France"},
    {"keywords": "artificial intelligence internship", "location": "France"},
    {"keywords": "stage science des données", "location": "France"},
    {"keywords": "stage ingénieur data", "location": "France"},
    {"keywords": "stage ingénieur IA", "location": "France"},
    {"keywords": "stage apprentissage automatique", "location": "France"},
    {"keywords": "stage PFE data", "location": "France"},
    {"keywords": "internship PFE data science", "location": "France"},
]

max_pages = 5

def scroll_page(driver, scroll_pause=1.5):
    """Scroll gradually to load dynamic content."""
    last_height=100
    try:
        last_height= driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
    except Exception as e:
        print(f"Error during initial scroll: {e}")
    # last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(scroll_pause)
        new_height=100
        try:
            new_height = driver.execute_script("return document.body.scrollHeight")
        except Exception as e:
            print(f"Error getting new scroll height: {e}")
            continue
        if new_height == last_height:
            break
        last_height = new_height

def scrape_page(keywords, location, page_num, driver):
    start = page_num * 25
    url = (
        f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}&f_E=1&start={start}"
    )
    print(f"\n🔹 Loading page {page_num+1} for '{keywords}' in {location}")
    driver.get(url)
    time.sleep(2)
    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.find_all("div", class_="base-card")
    if not job_cards:
        job_cards = soup.find_all("li", class_="jobs-search-results__list-item")

    page_jobs = []
    for card in job_cards:
        title_tag = card.find("h3", class_="base-search-card__title")
        company_tag = card.find("h4", class_="base-search-card__subtitle")
        loc_tag = card.find("span", class_="job-search-card__location")
        link_tag = card.find("a", href=True)
        posted_tag = card.find("time")

        logo_tag = card.find("img")
        logo_url = None
        if logo_tag and logo_tag.has_attr("src"):
            logo_url = logo_tag["src"]
        elif logo_tag and logo_tag.has_attr("data-delayed-url"):
            logo_url = logo_tag["data-delayed-url"]

        page_jobs.append({
            "title": title_tag.get_text(strip=True) if title_tag else "N/A",
            "company": company_tag.get_text(strip=True) if company_tag else "N/A",
            "location": loc_tag.get_text(strip=True) if loc_tag else "N/A",
            "link": link_tag["href"].split("?")[0] if link_tag else "N/A",
            "logo": logo_url if logo_url else "N/A",
            "search_keywords": keywords,
            "search_location": location
        })
    return page_jobs

def scrape_query(query):
    driver = get_driver()
    all_jobs = []
    for page in range(max_pages):
        jobs = scrape_page(query["keywords"], query["location"], page, driver)
        if not jobs:
            print(f"No jobs found for '{query['keywords']}' in {query['location']} page {page+1}")
            break
        all_jobs.extend(jobs)
        print(f"Total jobs collected for '{query['keywords']}' in {query['location']}: {len(all_jobs)}")
    driver.quit()
    return all_jobs

all_results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(scrape_query, q) for q in search_queries]
    for future in as_completed(futures):
        all_results.extend(future.result())

df = pd.DataFrame(all_results)


df.drop_duplicates(subset="title", keep="first", inplace=True)

df.to_csv("public/linkedin_internships_all_pages.csv", index=False, encoding="utf-8")
print("\nAll queries scraped, duplicates removed, saved to public/linkedin_internships_all_pages.csv")
print(df.head())
