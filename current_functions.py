import json
import re

import openpyxl
from bs4 import BeautifulSoup


def get_current_courses(filename):
    courses = {}
    with open(filename, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

        table = soup.find('table', attrs={'class': 'datadisplaytable'})
        table_body = table.find('tbody')
        table_rows = table_body.find_all('tr', recursive=False)

        course_titles = []
        course_infos = []
        course_times = []

        for row in table_rows:
            if row.find('th', recursive=False):
                course_titles.append(row.find('th'))
            if row.find('td', recursive=False):
                course_infos.append(row.find('td'))

                datadisplaytable = row.find('table', attrs={'class': 'datadisplaytable'})
                if datadisplaytable.find_all('tr'):
                    time_data = datadisplaytable.find_all('tr')
                    time_data.pop(0)
                    course_times.append(time_data)

        for index in range(len(course_titles)):
            course_title = course_titles[index].text
            course_info = course_infos[index].text.strip()
            course_time = course_times[index]

            name, crn, tag, section = course_title.rsplit(" - ", 3)
            name = name.strip()
            crn = crn.strip()
            tag = tag.strip()
            section = section.strip()

            desc_match = re.search(r'(.*)Associated Term:', course_info, re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip().replace('\n', '')

            term_match = re.search(r'Associated Term:\s*(.*)', course_info)
            if term_match:
                term = term_match.group(1).strip().replace('\n', '')

            reg_dates_match = re.search(r'Registration Dates:\s*(.*)', course_info)
            if reg_dates_match:
                reg_dates = reg_dates_match.group(1).strip().replace('\n', '')

            levels_match = re.search(r'Levels:\s*(.*)', course_info)
            if levels_match:
                levels = [level.strip() for level in levels_match.group(1).split(',')]

            credits_match = re.search(r'(\d+\.\d+)\s*Credits', course_info)
            if credits_match:
                creds = credits_match.group(1).strip().replace('\n', '')

            for time in course_time:
                data_list = time.text.split('\n')
                data_list.pop(0)
                meeting_times = {
                    'type': data_list[0].strip(),
                    'time': data_list[1].strip(),
                    'days': data_list[2].strip(),
                    'where': data_list[3].strip(),
                    'date_range': data_list[4].strip(),
                    'schedule_type': data_list[5].strip(),
                    'instructors': data_list[6].strip()
                }

            course = {
                'tag': tag,
                'name': name,
                'section': section,
                'desc': desc,
                'term': term,
                'reg_dates': reg_dates,
                'levels': levels,
                'credits': creds,
                'meeting_times': meeting_times
            }

            courses[crn] = course

    return courses


def to_excel(courses, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    header = ['CRN', 'Tag', 'Name', 'Section', 'Description', 'Term', 'Registration Dates', 'Levels', 'Credits',
              'Course Type', 'Time', 'Days', 'Where', 'Date Range', 'Schedule Type', 'Instructors']
    sheet.append(header)

    for crn, course_info in courses.items():
        row_data = [
            crn,
            course_info['tag'],
            course_info['name'],
            course_info['section'],
            course_info['desc'],
            course_info['term'],
            course_info['reg_dates'],
            ', '.join(course_info['levels']),
            course_info['credits'],
            course_info['meeting_times']['type'],
            course_info['meeting_times']['time'],
            course_info['meeting_times']['days'],
            course_info['meeting_times']['where'],
            course_info['meeting_times']['date_range'],
            course_info['meeting_times']['schedule_type'],
            course_info['meeting_times']['instructors'],
        ]
        sheet.append(row_data)

    workbook.save(filename)


def to_json(courses, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(courses, indent=4))
