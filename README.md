# ValidateData
Разработка программного модуля для валидации температурных данных KA Landsat и Terra/Aqua на основе наземных измерений

Title: "Development of a Software Module for Validating KA Landsat and Terra/Aqua MODIS Satellite Data Based on Ground Measurements"

The essence of the work is to have an Excel file where time and values obtained from the ground by the geodesy institute are recorded. We read and record them. Then we take data from the selected satellite obtained at ground coordinates and compare them based on matching time and date, displaying matches within a tolerance. We extract values from them and plot graphs, calculate RMSE and MBE, create a map, create Excel and PDF tables.
Satellite data is divided into Modis - Terra and Aqua separately, as well as into Day and Night. Landsat is not divided.
The module consists of Python scripts (about 11 executable files) that work in CMD.

Запуск:

1. Скачайте исполняемые файлы и requirements.txt в папку ValidateData
2. Запустите CMD консоль от имени администратора
3. Перейдите в папку с проектом с помощью команды cd (например, "cd C:\Users\Alexandra\Documents\ValidateData")
4. Введите команду pip install -r requirements.txt
5. После установки введите команду "python main.py"
6. Появится окно Проводника выбора файла с наземными данными

Instructions:

1. Download the executable files and requirements.txt to a folder.
2. Run the CMD console as an administrator.
3. Navigate to the project folder using the cd command (for example, "cd C:\Users\Alexandra\Documents\ValidateData").
4. Enter the command "pip install -r requirements.txt".
5. After installation, enter the command "python main.py".
6. A File Explorer window for selecting ground data file will appear.


![modis_comparison_aqua_day_20_2024-05-15_06-50-50](https://github.com/Rawiiw/ValidateData/assets/79237095/04af1873-1faa-42ac-a0d9-7483909b76b0)

![image](https://github.com/Rawiiw/ValidateData/assets/79237095/81ff298f-164b-47fa-835f-aa61f7c92f70)


![image](https://github.com/Rawiiw/ValidateData/assets/79237095/e66744d5-4558-4072-a960-688e8fdb3b0a)


![image](https://github.com/Rawiiw/ValidateData/assets/79237095/4538a9b0-639a-4d4a-88e1-6bab6c3b56e1)

