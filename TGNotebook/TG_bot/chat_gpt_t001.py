'''
Ты программист на Python.
Добавь в этот в этот кон новую реализация функции create_search_index. Имя новой функции должно быть create_permanent_search_index.
Функция должна проверять, есть ли сохраненный серилизовать ответ функции create_embedding.
Если он есть, то восстановить его без повторного вызова функции create_embedding.
Если его нет, то вызывать функцию create_embedding и серилизовать ее ответ.
В конце вернуть полученный или восстановленный ответ функции create_embedding.
Добавь необходимые импорты.
Добавь комментарии.
Сделай пример вызова.
Вот код функции
def create_search_index(text: str) -> Chroma:
    return create_embedding(text)

'''

import pickle
import os
from typing import Optional
from chroma import Chroma

# Function to check if a serialized search index exists
def check_search_index() -> Optional[Chroma]:
    if os.path.exists("search_index.pickle"):
        with open("search_index.pickle", "rb") as file:
            return pickle.load(file)
    else:
        return None

# Function to create and save a search index
def create_permanent_search_index(text: str) -> Chroma:
    # Check if a saved search index exists
    search_index = check_search_index()

    if search_index is None:
        # If no search index exists, create a new one
        search_index = create_embedding(text)

        # Save the search index
        with open("search_index.pickle", "wb") as file:
            pickle.dump(search_index, file)
    return search_index

# Example usage
def main():
    text = "Hello, world!"
    search_index = create_permanent_search_index(text)
    print(search_index)

if __name__ == "__main__":
    main()