import requests
import re
import codecs
import sys
import urllib.request
from bs4 import BeautifulSoup

def get_google_url(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    print (f'math_={match_}')
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)
    print (f'doc_id={doc_id}')
    new_url = 'https://docs.google.com/document/d/' + doc_id + '/export?format=txt'
    print(f'new_url={new_url}')
    return new_url


def load_document_g(url):
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def load_document_text(url: str) -> str:
    print(requests.get('https://httpbin.org/ip').json())
    new_url = get_google_url(url)
    text = ''
    try:
        # Download the document as plain text
        response = requests.get(new_url)
        response.raise_for_status()
        if 'text/plain' in response.headers['Content-Type']:
            print('Правильный доступ к документу!')
            text = response.text
        else:
            raise ValueError('Invalid Google Docs URL')
            print('Нет доступа к документу анонимным пользователям')
            logging.error(f'!!! No access to the document by anonymous users !!!')

    except Exception as e:  # обработка ошибок requests.exceptions.HTTPError: 404 Client Error: Not Found for url
        print(f'!!! load_document_text error: {str(e)}')
        sys.exit(1)

    return text


def load_text(file_path):
    # Открытие файла для чтения
    with codecs.open(file_path, "r", encoding="utf-8", errors="ignore") as input_file:
        # Чтение содержимого файла
        content = input_file.read()
    return content

# Функции для работы с файлом
def write_to_file(file_data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(file_data)

def append_to_file(new_line, file_name):
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write('\n' + new_line)

def split_text(text, max_length): # функция разбиения сроки на части переводом коретки
    words = text.split()  # Разделяем строку на слова
    result = []  # Список для результата

    current_line = ""  # Текущая строка
    for word in words:
        if len(current_line) + len(word) <= max_length:  # Если добавление слова не превышает максимальную длину
            current_line += word + " "  # Добавляем слово и пробел к текущей строке
        else:
            result.append(current_line.strip())  # Добавляем текущую строку в результат без лишних пробелов
            current_line = word + " "  # Начинаем новую строку с текущим словом

    if current_line:  # Если осталась незавершенная строка
        result.append(current_line.strip())  # Добавляем незавершенную строку в результат

    return '\n'.join(result)  # Возвращаем результат, объединяя строки символом перевода строки


if __name__ == '__main__':
    SYSTEM_DOC_URL = 'https://docs.google.com/document/d/1wCls61lqFOj3CSRfKbjeOjwfD78NkDt7/edit?usp=sharing&ouid=104673724125492337414&rtpof=true&sd=true'
    new_url = get_google_url(SYSTEM_DOC_URL)
    # system = load_document_text(new_url)  # Загрузка файла с Промтом
    system = load_document_g(new_url) # Загрузка файла с Промтом
    print(system)