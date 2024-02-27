from bs4 import BeautifulSoup


def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    sections = soup.find_all('section', class_='accordeon-section')
    parsed_texts = []

    for section in sections:
        city_name = section.find(
            'div', class_='shop-city-name').get_text(strip=True)

        items = section.find_all('div', class_='accordeon_item')
        for item in items:
            # Розділення кожного accordeon_item новим рядком зі знаком ";"
            parsed_texts.append(';')
            # Додавання назви міста на початку кожного accordeon_item
            parsed_texts.append(city_name)

            texts = item.find_all('span')
            for text in texts:
                parsed_texts.append(text.get_text(strip=True))

            links = item.find_all('a', href=True)
            for link in links:
                parsed_texts.append(link.get_text(
                    strip=True) + ' - ' + link['href'])

    return parsed_texts


# Виклик функції parse_html
parsed_content = parse_html('Наші магазини _ Інтернет-магазин Техно Їжак.html')

# Запис результатів у текстовий файл
with open('parsed_content.txt', 'w', encoding='utf-8') as file:
    for line in parsed_content:
        file.write(line + '\n')
