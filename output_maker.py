import os

import pandas as pd

def create_csv(df):
    file_name = input("Введите название файла CSV для сохранения (без расширения): ")
    file_name += ".csv"
    df.to_csv(file_name, index=False)
    print(f"Таблица сохранена в {file_name}")

def create_excel(df, folder=None):
    file_name = input("Введите название файла Excel для сохранения (без расширения): ")
    file_name += ".xlsx"

    if folder:
        file_path = os.path.join(folder, file_name)
    else:
        file_path = file_name

    df.to_excel(file_path, index=False)
    print(f"Таблица сохранена в {file_path}")
