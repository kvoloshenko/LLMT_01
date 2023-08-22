import re
import requests
def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)
    print (f'doc_id={doc_id}')
    text = ''

    try:
        # Check if you have permission to view the document
        # permission_check_url = f'https://docs.google.com/drive/v3/files/{doc_id}/permissions'
        permission_check_url = f'https://docs.google.com/document/d/{doc_id}'
        print(f'permission_check_url={permission_check_url}')
        response = requests.get(permission_check_url)
        status_code = response.status_code
        print(f'status_code={status_code}')
        response.raise_for_status()


        # Download the document as plain text
        response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
        response.raise_for_status()
        text = response.text
    except Exception as e:  # обработка ошибок requests.exceptions.HTTPError: 404 Client Error: Not Found for url
        print(f'!!! load_document_text error: {str(e)}')
        # logging.error(f'!!! load_document_text error: {str(e)}')

    return text


SYSTEM_DOC_URL = 'https://docs.google.com/document/d/1AbpsbMLgyaY84ILvlj5lfw6v1tCApItd'    # промпт Платон en

system = load_document_text(SYSTEM_DOC_URL)  # Загрузка файла с Промтом

print(f'system={system}')