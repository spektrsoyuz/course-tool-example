import json
import time

import requests
from bs4 import BeautifulSoup
from requests import RequestException


def get_catalog(level, subjects):
    courses = {}
    for subject in subjects:
        url = f'https://catalog.kettering.edu/coursesaz/{level.lower()}/{subject.lower()}/'
        courses[subject] = get_catalog_subject(url)

    return courses


def get_catalog_subject(url):
    courses = {}
    source = request(url)
    soup = BeautifulSoup(source.text, 'html.parser')

    courseblocks = soup.find_all('div', attrs={'class': 'courseblock'})
    for courseblock in courseblocks:
        courseblocktitle = courseblock.find('p', attrs={'class': 'courseblocktitle'}).text.split('\xa0')
        courseblockdesc = str(courseblock.find('p', attrs={'class': 'courseblockdesc'})).split('<br/>')

        coreqs = 'None'
        prereqs = 'None'
        standing = 'None'
        desc = strip_html(courseblockdesc[-3]).replace('\n', ' ')

        for line in courseblockdesc:
            if 'Minimum Class Standing:' in line:
                standing = line.split(':')[1].strip()

            if 'Prerequisites:' in line:
                prereqs = strip_html(line).replace('Prerequisites: ', '')

            if 'Corequisites:' in line:
                coreqs = strip_html(line).replace('Corequisites: ', '')

        if '91' in courseblocktitle[0]:
            desc = ''

        course = {
            'tag': courseblocktitle[0],
            'name': courseblocktitle[2].replace('\n', ''),
            'desc': desc.replace('  ', ' '),
            'coreqs': coreqs.replace('\n', ''),
            'prereqs': prereqs.replace('\n', ''),
            'standing': standing,
            'credits': courseblocktitle[-1].replace(' Credits', ''),
        }

        courses[courseblocktitle[0]] = course

    return courses


def request(url, max_retries=3):
    for i in range(max_retries):
        try:
            print(f'html request: {url}, attempt {i + 1}')
            response = requests.get(url)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(f'Error: {e}')
            time.sleep(1)


def strip_html(html):
    soup = BeautifulSoup(str(html), 'html.parser')
    plain_text = soup.get_text()
    return plain_text


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
