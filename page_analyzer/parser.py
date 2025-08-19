from bs4 import BeautifulSoup


def check_data(response):
    parsed_content = BeautifulSoup(response.text, 'html.parser')
    result = {}

    h1 = parsed_content.h1.text if parsed_content.h1 else None
    title = parsed_content.title.text if parsed_content.title else None
    meta_description_tag = parsed_content.find('meta',
                                               attrs={'name': 'description'})
    description = meta_description_tag.get('content') if meta_description_tag \
        else None

    result['h1'] = h1
    result['title'] = title
    result['description'] = description

    return result