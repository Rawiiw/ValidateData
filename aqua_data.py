import ee
import pandas as pd
from datetime import datetime

class AquaDataManager:
    def __init__(self):
        self.modis_product = 'MODIS/006/MYD11A1'

    def get_image_collection(self, coordinates, date_start, date_end):
        point = ee.Geometry.Point(coordinates)
        lst = ee.ImageCollection(self.modis_product) \
            .filterBounds(point) \
            .filterDate(date_start, date_end)
        return lst

    def mask_clouds(self, image):
        QC_Day = image.select('QC_Day')
        QC_Night = image.select('QC_Night')
        cloud_mask_day = QC_Day.bitwiseAnd(0b11).eq(0)
        cloud_mask_night = QC_Night.bitwiseAnd(0b11).eq(0)
        return image.updateMask(cloud_mask_day).updateMask(cloud_mask_night)

    def sample_image(self, image, point):
        image = self.mask_clouds(image)
        image = image.addBands(image.metadata("system:time_start"))
        image = image.addBands(image.select('LST_Day_1km').multiply(0.02).subtract(273.15), overwrite=True)
        image = image.addBands(image.select('LST_Night_1km').multiply(0.02).subtract(273.15), overwrite=True)
        image = image.addBands(image.select('Night_view_time').multiply(0.1), overwrite=True)
        image = image.addBands(image.select('Day_view_time').multiply(0.1), overwrite=True)
        image = image.addBands(image.select('Night_view_angle').add(-65), overwrite=True)
        image = image.addBands(image.select('Day_view_angle').add(-65), overwrite=True)
        image = image.addBands(image.select('Emis_31').multiply(0.002).add(0.49), overwrite=True)
        image = image.addBands(image.select('Emis_32').multiply(0.002).add(0.49), overwrite=True)
        image = image.addBands(image.select('Clear_day_cov').multiply(0.005), overwrite=True)
        image = image.addBands(image.select('Clear_night_cov').multiply(0.005), overwrite=True)
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

        aqua_datatable = featureCollection.map(self.replace_numbers_by_strings).select(columns)
        return aqua_datatable

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