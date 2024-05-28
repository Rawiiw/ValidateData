import os
import webbrowser
import ee
import geemap
from datetime import datetime

class MapViewer:
    def __init__(self, coordinates, date_start, date_end):
        if isinstance(coordinates, list):
            self.coordinates = coordinates
        else:
            self.coordinates = [float(coord.strip()) for coord in coordinates.split(',')]
        self.date_start = date_start
        self.date_end = date_end
        self.map_directory = os.path.join(os.getcwd(), 'Maps')  # Путь к папке с картами
        if not os.path.exists(self.map_directory):
            os.makedirs(self.map_directory)

    def create_map(self):
        # Создание точки и ее трансформация
        point = ee.Geometry.Point(self.coordinates)
        transformed_point = point.transform('SR-ORG:6974', 1000)

        # Получение коллекции изображений MODIS MYD11A1
        lst = ee.ImageCollection('MODIS/006/MYD11A1') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end)

        # Получение медианного изображения
        median_image = lst.median()

        # Определение региона и обрезка изображения
        region = transformed_point.buffer(50000)
        image = median_image.clip(region)

        # Получение URL для тайлов
        tile_url = image.select('LST_Day_1km').getThumbUrl({
            'min': -20, 'max': 40, 'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                                               '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                                               '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                                               'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                                               'ff0000', 'de0101', 'c21301', 'a71001', '911003']
        })

        # Создание карты Google Earth Engine
        map_center = [self.coordinates[1], self.coordinates[0]]  # меняем порядок координат
        m = geemap.Map(center=map_center, zoom=12)  # Увеличиваем значение zoom

        # Добавление слоя с тайлами MODIS LST Day
        m.add_tile_layer(url=tile_url, name='MODIS MYD11A1')

        # Добавление слоя с температурой MODIS MOD11A1
        modis = ee.ImageCollection('MODIS/061/MOD11A1') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end)

        # Выбор изображения с температурой
        temperature_image = modis.select('LST_Day_1km')

        # Добавление слоя с температурой
        m.addLayer(temperature_image, {'min': 13000.0, 'max': 16500.0, 'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                                                                                    '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                                                                                    '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                                                                                    'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                                                                                    'ff0000', 'de0101', 'c21301', 'a71001', '911003']},
                   'Land Surface Temperature MODIS/061/MOD11A1')

        # Добавление слоя с тайлами Landsat
        landsat_tile_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        m.add_tile_layer(url=landsat_tile_url, name='Landsat')

        return m

    def display_map(self):
        # Создание карты
        m = self.create_map()

        # Сохранение карты в HTML файл
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        map_file_name = f'map_{current_time}.html'  # Имя файла без указания пути к папке
        map_file_path = os.path.join(self.map_directory, map_file_name)  # Полный путь к файлу
        m.to_html(map_file_path)

        # Вопрос пользователю о сохранении карты
        save_map = input("Хотите ли вы сохранить карту? (да/нет): ").lower()
        if save_map == "да":
            webbrowser.open_new_tab(f'file://{os.path.abspath(map_file_path)}')
        elif save_map == "нет":
            print("Карта не сохранена.")
        else:
            print("Некорректный ответ.")