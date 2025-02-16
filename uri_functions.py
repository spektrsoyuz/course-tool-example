import json
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

MAIN_URL = 'https://web.uri.edu/catalog/#/courses'


def get_courses(subjects):
    courses = {}

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.6778.265 Safari/537.36"
    )

    webdriver_path = 'C:/Users/chris/Downloads/chromedriver-win64/chromedriver.exe'
    service = Service(webdriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    for name in subjects.values():
        group = name.replace(',', '%2C').replace('/', '%2F').replace(' ', '%20').replace('&', '%26')
        url = f'{MAIN_URL}?group={group}'
        print(url)
        driver.get(url)

        WebDriverWait(driver, 60).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'style__header___2lB0y'))
        )

        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        links = []

        ul = soup.find('ul', attrs={'class': 'style__withDivider___1CvOz'})
        hrefs = ul.find_all('a')
        for href in hrefs:
            link_match = re.search(r'href="([^"]+)"', str(href))
            if link_match:
                links.append(link_match.group(1))

        for link in links:
            url = f'https://web.uri.edu/catalog/{link}'
            print(url)
            course = get_course(driver, url)
            courses[course['cid']] = course
            print(course)

        concat_json(courses, 'export/results_uri.json')

    driver.quit()
    return courses


def get_course(driver, url):
    driver.get(url)
    time.sleep(1)

    cid = ''
    name = ''
    desc = ''
    modality = ''
    creds = ''
    college = ''
    department = ''

    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    course_view = soup.find(id='__KUALI_TLP').find('div', recursive=False)

    title = course_view.find('h2').text
    dash_index = title.find('-')
    if dash_index != -1:
        cid, name = title[:dash_index].strip(), title[dash_index + 1:].strip()

    body = course_view.find_all('div', attrs={'class': 'noBreak'})
    for _ in body:
        header = _.find('h3').text.strip()
        result = _.find('div').text.strip()

        if header == 'Description':
            desc = result
        if header == 'Modality':
            modality = result
        if header == 'Credits':
            creds = result
        if header == 'College':
            college = result
        if header == 'Department':
            department = result

    course = {
        'cid': cid,
        'name': name,
        'desc': desc,
        'modality': modality,
        'creds': creds,
        'college': college,
        'department': department,
    }

    return course


def read_json(filename):
    try:
        with open(filename, 'r') as file:
            json_as_dict = json.load(file)
            return json_as_dict
    except FileNotFoundError:
        print(f'File {filename} not found.')
        return []
    except json.decoder.JSONDecodeError:
        print(f'Invalid JSON format in {filename}.')
        return []


def to_json(courses, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(courses, indent=4))


def concat_json(courses, filename):
    try:
        with open(filename, 'r') as file:
            json_as_dict = json.load(file)
        json_as_dict.update(courses)
    except FileNotFoundError:
        json_as_dict = courses

    with open(filename, 'w') as file:
        file.write(json.dumps(json_as_dict, indent=4))
