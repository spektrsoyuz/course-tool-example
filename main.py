import course_functions


def main():
    undergrad_tags = course_functions.read_json('undergrad.json')
    course_catalog = course_functions.get_catalog('undergrad', undergrad_tags)
    course_functions.to_json(course_catalog, 'results_catalog.json')


if __name__ == '__main__':
    main()
