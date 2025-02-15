import catalog_functions
import current_functions


def main():
    undergrad_tags = catalog_functions.read_json('undergrad.json')
    course_catalog = catalog_functions.get_catalog('undergrad', undergrad_tags)
    catalog_functions.to_json(course_catalog, 'results_catalog.json')

    current_courses = current_functions.get_current_courses('input/Class Schedule Listing.htm')
    current_functions.to_json(current_courses, 'results_current.json')
    current_functions.to_excel(current_courses, 'results_current.xlsx')


if __name__ == '__main__':
    main()
