# ValidateData
Разработка программного модуля для валидации температурных данных KA Landsat и Terra/Aqua на основе наземных измерений

Title: "Development of a Software Module for Validating KA Landsat and Terra/Aqua MODIS Satellite Data Based on Ground Measurements"

The essence of the work is to have an Excel file where time and values obtained from the ground by the geodesy institute are recorded. We read and record them. Then we take data from the selected satellite obtained at ground coordinates and compare them based on matching time and date, displaying matches within a 15-minute tolerance. We extract values from them and plot graphs, calculate RMSE and MBE, create a map, create Excel and PDF tables.
Satellite data is divided into Modis - Terra and Aqua separately, as well as into Day and Night. Landsat is not divided.
The module consists of Python scripts (about 11 executable files) that work in CMD.
