import catalog_functions
import current_functions
import uri_functions


def main():
    undergrad_tags = catalog_functions.read_json('undergrad.json')
    course_catalog = catalog_functions.get_catalog('undergrad', undergrad_tags)
    catalog_functions.to_json(course_catalog, 'export/results_catalog.json')

    current_courses = current_functions.get_current_courses('input/Class Schedule Listing.htm')
    current_functions.to_json(current_courses, 'export/results_current.json')
    current_functions.to_excel(current_courses, 'export/results_current.xlsx')


def uri_test():
    subjects = uri_functions.read_json('uri_subjects.json')
    courses = uri_functions.get_courses(subjects)
    uri_functions.to_json(courses, 'export/results_uri.json')


if __name__ == '__main__':
    # main()
    uri_test()
