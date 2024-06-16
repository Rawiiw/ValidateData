import ee
import pandas as pd

class AquaDataManager:
    __instance = None

    def get_image_collection(self, coordinates, date_start, date_end):
        point = ee.Geometry.Point(coordinates)
        transformed_point = point.transform('SR-ORG:6974', 1000)

        def mask_clouds(image):
            # Извлечение QC битов
            qc = image.select('QC_Day')
            cloud_mask = qc.bitwiseAnd(1 << 0).eq(0)  # Бит 0: облака
            image = image.updateMask(cloud_mask)  # Применение маски облаков
            return image

        lst = ee.ImageCollection('MODIS/061/MYD11A1') \
            .filterBounds(transformed_point) \
            .filterDate(date_start, date_end) \
            .map(mask_clouds)  # Применение маски облачности

        return lst

    def sample_image(self, image, point):
        image = image.addBands(image.metadata("system:time_start"))
        image = image.addBands(image.select('LST_Day_1km').multiply(0.02).subtract(273.15), overwrite=True)
        image = image.addBands(image.select('LST_Night_1km').multiply(0.02).subtract(273.15), overwrite=True)
        image = image.addBands(image.select('Night_view_time').multiply(0.1), overwrite=True)
        image = image.addBands(image.select('Day_view_time').multiply(0.1), overwrite=True)
        image = image.addBands(image.select('Night_view_angle').add(-65), overwrite=True)
        image = image.addBands(image.select('Day_view_angle').add(-65), overwrite=True)
        image = image.addBands(image.select('Emis_31').multiply(0.002).add(0.49), overwrite=True)
        image = image.addBands(image.select('Emis_32').multiply(0.002).add(0.49), overwrite=True)
        image = image.addBands(image.select('Clear_day_cov').multiply(0.0005), overwrite=True)
        image = image.addBands(image.select('Clear_night_cov').multiply(0.0005), overwrite=True)
        return image.sampleRegions(collection=point, scale=1000)

    def get_feature_collection(self, lst, point):
        featureCollection = ee.FeatureCollection(lst.map(lambda image: self.sample_image(image, point))).flatten()
        return featureCollection

    def replace_numbers_by_strings(self, feature):
        def as_time_string(v):
            return ee.String(v.floor().int().format('%02d')) \
                .cat(':') \
                .cat(ee.String(v.subtract(v.floor()).multiply(60).int().format('%02d'))) \
                .cat(':00')

        d = ee.Date(feature.get('system:time_start'))
        dt = as_time_string(ee.Number(feature.get('Day_view_time')))
        nt = as_time_string(ee.Number(feature.get('Night_view_time')))
        dtemp = ee.Number(feature.get('LST_Day_1km')).format('%6.2f')
        ntemp = ee.Number(feature.get('LST_Night_1km')).format('%6.2f')
        emis31 = ee.Number(feature.get('Emis_31')).format('%6.2f')
        emis32 = ee.Number(feature.get('Emis_32')).format('%6.2f')
        day_cov = ee.Number(feature.get('Clear_day_cov')).format('%6.2f')
        night_cov = ee.Number(feature.get('Clear_night_cov')).format('%6.2f')
        day_angle = ee.Number(feature.get('Day_view_angle')).format('%6.2f')
        night_angle = ee.Number(feature.get('Night_view_angle')).format('%6.2f')
        return feature.set({
            'Night_view_time': nt,
            'Day_view_time': dt,
            'Night_view_angle': night_angle,
            'Day_view_angle': day_angle,
            'LST_Day_1km': dtemp,
            'LST_Night_1km': ntemp,
            'Emis_31': emis31,
            'Emis_32': emis32,
            'Clear_day_cov': day_cov,
            'Clear_night_cov': night_cov,
            'date': d.format('YYYY-MM-dd')
        })

    def get_datatable(self, featureCollection):
        columns = [
            "LST_Day_1km",
            "QC_Day",
            "Day_view_time",
            "Day_view_angle",
            "LST_Night_1km",
            "QC_Night",
            "Night_view_time",
            "Night_view_angle",
            "Emis_31",
            "Emis_32",
            "Clear_day_cov",
            "Clear_night_cov",
            "date",
            "name"
        ]

        modis_datatable = featureCollection.map(self.replace_numbers_by_strings).select(columns)
        return modis_datatable

    def get_image_data(self, coordinates, date_start, date_end):
        lst = self.get_image_collection(coordinates, date_start, date_end)
        return lst

    def get_feature_data(self, lst, coordinates):
        point = ee.Geometry.Point(coordinates)
        featureCollection = self.get_feature_collection(lst, point)
        return featureCollection

    def create_dataframe(self, featureCollection):
        datatable = self.get_datatable(featureCollection)
        if datatable is not None:
            df = pd.DataFrame([feature['properties'] for feature in datatable.getInfo()['features']])
            return df
        else:
            print("Feature collection is empty.")
            return None

def dataframe_to_dict(df):
    if df is not None:
        return df.to_dict(orient='records')
    else:
        return None
