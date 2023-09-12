from dotenv import load_dotenv
import os
import сity_chat_gpt as chat_gpt
import logging

# XML теги для лога
LOG_S = '<log>'
LOG_E = '</log>'
X_CDATA_S = '<![CDATA['
X_CDATA_E = ']]>'
MESSAGE_TEXT_S = '<mt>' + X_CDATA_S
MESSAGE_TEXT_E = X_CDATA_E + '</mt>'
MESSAGE_DATE_S = '<md>'
MESSAGE_DATE_E = '</md>'
MESSAGE_ID_S = '<mi>'
MESSAGE_ID_E = '</mi>'
USER_NAME_S = '<un>'
USER_NAME_E = '</un>'
USER_ID_S = '<ui>'
USER_ID_E = '</ui>'
REPLY_TEXT_S = '<rt>' + X_CDATA_S
REPLY_TEXT_E = X_CDATA_E + '</rt>'

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

# возьмем переменные окружения из .env
load_dotenv()

TEXT_BEGINNING = os.environ.get("TEXT_BEGINNING")
logging.info(f'TEXT_BEGINNING = {TEXT_BEGINNING}')

TEXT_END = os.environ.get("TEXT_END")
logging.info (f'TEXT_END = {TEXT_END}')

QUESTION_FILTER = os.environ.get("QUESTION_FILTER")
if QUESTION_FILTER is None:
    QUESTION_FILTER = ""

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

def main():
    topic = 'какая модель градостроительного зонирования ?'
    print(f'topic={topic}')
    logging.info(f'{MESSAGE_TEXT_S}{topic}{MESSAGE_TEXT_E}')
    reply_text, num_tokens, messages, completion= chat_gpt.chat_question(topic)
    response = TEXT_BEGINNING + '\n'
    response = response + reply_text + '\n' + TEXT_END
    print(f'response={response}')
    logging.info(f'{REPLY_TEXT_S}{response}{REPLY_TEXT_E}')

if __name__ == "__main__":
    main()