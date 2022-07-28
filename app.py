# 1st step install and import modules
# -- download the correct version of your chromedriver from https://chromedriver.storage.googleapis.com/index.html
# -- pip/pip3 install lxml
# -- pip/pip3 install requests
# -- pip/ pip3 install beautufulsoup4
# -- pip/ pip3 install selenium

import time
from selenium import webdriver

# Let you scrape the data by using (xpath, tag, attribute, value,class,....)
from selenium.webdriver.common.by import By
# Make the browser wait for the element to be visible before scraping it.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests
import csv
from itertools import zip_longest

job_title = []
company_name = []
location_name = []
skills = []
links = []
salary = []
Requirements = []
post_date = []
page = 0


baseUrl = "https://wuzzuf.net"


# Path of the chromedriver.exe
chromedriver_path = 'chromedriver'

# Setup the desired capabilities of the browser
options = webdriver.ChromeOptions()

# Remove the notifications
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Make the browser headless(without GUI)
options.add_argument('--headless')
# Give the browser a size
options.add_argument("--window-size=1920,1080")
# Disable the browser from using the GPU
options.add_argument("--disable-gpu")

# UserAgent for the browser
useAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={useAgent}')

# Giving the driver the capabilities to use the chrome driver and to use the chrome browser and to use the options
driver = webdriver.Chrome(chromedriver_path, chrome_options=options)

# Maximize the window of the browser
driver.maximize_window()
# Give the driver the url to visit


while True:
    try:
        print("Page: ", page+1)
        result = requests.get(
            f"https://wuzzuf.net/search/jobs/?a=hpb&q=python&start={page}")
        # 3rd step save page content/markup
        src = result.content
        # print(src)

        # 4th step create soup object to parse content
        soup = BeautifulSoup(src, "lxml")
        pg = int(soup.find("strong").text)
        pg = pg//15
        # 5th step find the elements containing info we need

        job_titles = soup.find_all("h2", {"class": "css-m604qf"})
        # print(job_titles)
        company_names = soup.find_all("a", {"class": "css-17s97q8"})
        # print(company_names)
        locations_names = soup.find_all("span", {"class": "css-5wys0k"})
        # print(locations_names)
        job_skills = soup.find_all("div", {"class": "css-y4udm8"})
        # print(job_skills)
        post_new = soup.find_all("div", {"class": "css-4c4ojb"})
        post_old = soup.find_all("div", {"class": "css-do6t5g"})
        posted = [*post_new, *post_old]
        # 6th step loop over returned lists to extract needed info other lists
        for i in range(len(job_titles)):
            job_title.append(job_titles[i].text)
            links.append(baseUrl+job_titles[i].find("a").attrs['href'])
            cp = company_names[i].text.replace("-", "")
            company_name.append(cp)
            location_name.append(locations_names[i].text)
            skills.append(job_skills[i].text)
            post_date.append(posted[i].text)

        for link in links:
            driver.get(link)
            # give the driver a wait time to load the page
            wait = WebDriverWait(driver, 10)
            # when the page is loaded, the driver will wait for the element to be visible
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/main/article/section[2]/div[4]/span[2]')))
            salaries = ""
            req = ""

            try:
                # select the element to be scraped
                salaries = driver.find_element(By.XPATH,
                                               '//*[@id="app"]/div/main/article/section[2]/div[4]/span[2]').text.strip()
            except:
                salaries = "Confidential"

            try:
                reqs = driver.find_element(By.XPATH,
                                           '//*[@id="app"]/div/main/article/section[4]/div/ul')
                res = ""
                for i in reqs.find_element(By.TAG_NAME, 'li'):
                    res += i.text.strip()+"| "
                res = res[:-2]
                Requirements.append(res)
            except:
                Requirements.append("No Requirements Found")

            salary.append(salaries)
        page += 1
        time.sleep(2)
        if page > pg:
            print("Done")
            break
        print("Page switched")
    except Exception as e:
        print(e)
        break


file_list = [job_title, company_name, post_date, location_name,
             skills, links, salary, Requirements]
exported = zip_longest(*file_list)
with open("web_scraping2.csv", "w") as myfile:
    wr = csv.writer(myfile)
    wr.writerow(["job title", "company name", "date",
                "location", "skills", "links", "salary", "Requirements"])
    wr.writerows(exported)
