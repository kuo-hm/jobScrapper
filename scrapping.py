
import time
import csv
from bs4 import BeautifulSoup
import requests
from itertools import zip_longest


# let you control the browser
from selenium import webdriver

# Let you scrape the data by using (xpath, tag, attribute, value,class,....)
from selenium.webdriver.common.by import By

# Make the browser wait for the element to be visible before scraping it.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


job_title = []
company_name = []
contrat = []
links = []
post_date = []


baseUrl = "https://fr.indeed.com/Bordeaux-Emplois-python?vjk=4812319f6345ed6d"

# Path of the chromedriver.exe
chromedriver_path = 'chromedriver'

# initializing the desired Setings of the browser
options = webdriver.ChromeOptions()

# Remove the logs from the console
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Make the browser headless(without GUI)
options.add_argument('--headless')
# Give the browser a size of the screen
options.add_argument("--window-size=1920,1080")
# Disable the browser from using the GPU
options.add_argument("--disable-gpu")

# UserAgent for the browser
useAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={useAgent}')

# Giving the driver the settings for the browser and the path of the chromedriver to be used
driver = webdriver.Chrome(chromedriver_path, chrome_options=options)

# The WebDriveWait object is used to wait for the element to be visible before scraping it. it takes the driver, the time to wait in seconds.
wait = WebDriverWait(driver, 20)

# Give the driver the url to be scraped
driver.get(baseUrl)

# The request object is used to get the html code of the page
result = requests.get(
    baseUrl)
src = result.content
soup = BeautifulSoup(src, "lxml")

# Get all the divs in the page that contain the job listing
div = soup.find_all("div", {"class": "cardOutline"})

# Append the url of the job to the list
links.append(baseUrl)

# Function to get the job data and it have the job id as a parameter


def get_job(id):

    time.sleep(2)

    try:
        # when the page is loaded, the driver will wait for the element to be visible
        wait.until(EC.presence_of_element_located(
            (By.ID, 'vjs-container-iframe')))
    except Exception as error:
        print(error)

    try:
        # After the element is visible, the driver will access the iframe and get the html code of the page
        driver.switch_to.frame('vjs-container-iframe')

        # Wait for the element to be visible before scraping it
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME,
             'jobsearch-InlineCompanyRating')))

        # Wait for a bit before scraping the data so that the page can load
        driver.implicitly_wait(10)

        try:
            # Get the container of the contract type
            types = driver.find_element(By.CLASS_NAME,
                                        'jobsearch-JobDescriptionSection-sectionItem')

            # Get the contra type from the container
            type = types.find_elements(By.TAG_NAME, 'div')
            type = type[1].text
            contrat.append(type)
        except:
            # If the contra type is not found, it will append an empty string
            contrat.append("n/a")

        try:

            # Get the job title by class name
            title = driver.find_element(By.CLASS_NAME,
                                        'jobsearch-JobInfoHeader-title')

            # Split the title to get the job title
            titre = title.text.split("\n")
            titre = titre[0]
            job_title.append(titre)
        except:
            job_title.append("n/a")
        try:

            # Get the company name container by class name
            company = driver.find_element(By.CLASS_NAME,
                                          'jobsearch-InlineCompanyRating')
            company_names = company.find_element(By.TAG_NAME, 'a').text
            company_name.append(company_names)
        except:
            company_name.append("n/a")

        try:
            # Get the post date container by class name
            date = driver.find_element(By.CLASS_NAME,
                                       'jobsearch-HiringInsights-entry--text')
            post_date.append(date.text)
        except:
            post_date.append("n/a")

        # After the data is scraped, the driver will switch to another job listing and append the url to the list
        url = f'https://fr.indeed.com/Bordeaux-Emplois-python?vjk={id}'
        driver.get(url)
        links.append(url)

        # Waiting 10 seconds before scraping the data again
        driver.implicitly_wait(10)
    except Exception as error:
        print(error)


try:
    for post in div:

        # Get the job id from the div
        id = post.find("a").attrs['data-jk']

        # pass the job id to the get_job function
        get_job(id)

except Exception as error:
    print(error)


file_list = [job_title, company_name, post_date, contrat,
             links]
exported = zip_longest(*file_list)
with open("indeed.csv", "w") as myfile:
    wr = csv.writer(myfile)
    wr.writerow(["job title", "company name", "date",
                "Contrat", "Links"])
    wr.writerows(exported)
