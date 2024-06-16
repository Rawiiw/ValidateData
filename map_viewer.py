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

    def mask_modis_clouds(self, image):
        qc = image.select('QC_Day')
        cloud_mask = qc.bitwiseAnd(1 << 0).eq(0)  # Бит 0: облака
        return image.updateMask(cloud_mask)

    def mask_jaxa_clouds(self, image):
        qc = image.select('QA_Flag')
        cloud_mask = qc.bitwiseAnd(1 << 0).eq(0)  # Предполагаем, что бит 0 - облака
        return image.updateMask(cloud_mask)

    def create_map(self):
        point = ee.Geometry.Point(self.coordinates)
        transformed_point = point.transform('SR-ORG:6974', 1000)

        lst_modis = ee.ImageCollection('MODIS/061/MYD11A1') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end) \
            .map(self.mask_modis_clouds)

        median_image = lst_modis.median()

        region = transformed_point.buffer(50000)
        image = median_image.clip(region)

        tile_url = image.select('LST_Day_1km').getThumbUrl({
            'min': -20, 'max': 40, 'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                                               '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                                               '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                                               'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                                               'ff0000', 'de0101', 'c21301', 'a71001', '911003']
        })

        map_center = [self.coordinates[1], self.coordinates[0]]
        m = geemap.Map(center=map_center, zoom=12)

        m.add_tile_layer(url=tile_url, name='MODIS MYD11A1')

        modis = ee.ImageCollection('MODIS/061/MOD11A1') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end) \
            .map(self.mask_modis_clouds)

        temperature_image = modis.select('LST_Day_1km')

        m.addLayer(temperature_image, {'min': 13000.0, 'max': 16500.0, 'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                                                                                    '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                                                                                    '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                                                                                    'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                                                                                    'ff0000', 'de0101', 'c21301', 'a71001', '911003']},
                   'Land Surface Temperature MODIS/061/MOD11A1')

        jaxa = ee.ImageCollection('JAXA/GCOM-C/L3/LAND/LST/V2') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end) \
            .map(self.mask_jaxa_clouds)

        if jaxa.size().getInfo() > 0:
            jaxa_image = jaxa.median().select('LST_AVE')
            m.addLayer(jaxa_image, {'min': 0, 'max': 40, 'palette': ['blue', 'green', 'red']}, 'JAXA GCOM-C LST')

        oxford = ee.ImageCollection('Oxford/MAP/LST_Day_5km_Monthly') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end) \
            .map(self.mask_modis_clouds)

        if oxford.size().getInfo() > 0:
            oxford_image = oxford.median().select('LST_Day')
            m.addLayer(oxford_image, {'min': 0, 'max': 50, 'palette': ['blue', 'green', 'red']}, 'Oxford MAP LST Day')

        mod21c3 = ee.ImageCollection('MODIS/061/MOD21C3') \
            .filterBounds(transformed_point) \
            .filterDate(self.date_start, self.date_end) \
            .map(self.mask_modis_clouds)

        mod21c3_image = mod21c3.median().select('LST_Day')

        m.addLayer(mod21c3_image, {'min': 0, 'max': 50, 'palette': ['purple', 'blue', 'green', 'yellow', 'orange', 'red']}, 'MODIS MOD21C3 LST Day')

        landsat_tile_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        m.add_tile_layer(url=landsat_tile_url, name='Landsat')

        return m

    def display_map(self):
        m = self.create_map()

        # Вопрос пользователю о сохранении карты
        save_map = input("Хотите ли вы сохранить карту? (да/нет): ").lower()
        if save_map == "да":
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            map_file_name = f'map_{current_time}.html'
            map_file_path = os.path.join(self.map_directory, map_file_name)
            m.to_html(map_file_path)
            webbrowser.open_new_tab(f'file://{os.path.abspath(map_file_path)}')
        elif save_map == "нет":
            print("Карта не сохранена.")
        else:
            print("Некорректный ответ.")