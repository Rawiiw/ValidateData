import ee
import pandas as pd

class LandsatDataManager:
    __instance = None
    def get_image_collection(self, coordinates, date_start, date_end):
        point = ee.Geometry.Point(coordinates)
        lst = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filterBounds(point) \
            .filterDate(date_start, date_end)
        return lst

    def sample_image(self, image, point):
        image = image.addBands(image.metadata("system:time_start"))
        image = image.addBands(image.select('ST_B10').multiply(0.001), overwrite=True)
        image = image.addBands(image.select('ST_ATRAN').multiply(0.0001), overwrite=True)
        image = image.addBands(image.select('ST_CDIST').multiply(0.01), overwrite=True)
        image = image.addBands(image.select('ST_DRAD').multiply(0.001), overwrite=True)
        image = image.addBands(image.select('ST_EMIS').multiply(0.0001), overwrite=True)
        image = image.addBands(image.select('ST_EMSD').multiply(0.0001), overwrite=True)
        image = image.addBands(image.select('ST_QA').multiply(0.01), overwrite=True)
        image = image.addBands(image.select('ST_TRAD').multiply(0.001), overwrite=True)
        image = image.addBands(image.select('ST_URAD').multiply(0.001), overwrite=True)
        image = image.addBands(image.select('QA_PIXEL'), overwrite=True)

        return image.sampleRegions(collection=point, scale=1000)

    def get_feature_collection(self, lst, point):
        featureCollection = ee.FeatureCollection(lst.map(lambda image: self.sample_image(image, point))).flatten()
        return featureCollection

    def replace_numbers_by_strings(self, feature):
        d = ee.Date(feature.get('system:time_start'))
        st_b10 = ee.Number(feature.get('ST_B10')).format('%6.2f')
        st_atran = ee.Number(feature.get('ST_ATRAN')).format('%6.2f')
        st_cdist = ee.Number(feature.get('ST_CDIST')).format('%6.2f')
        st_drad = ee.Number(feature.get('ST_DRAD')).format('%6.2f')
        st_emis = ee.Number(feature.get('ST_EMIS')).format('%6.2f')
        st_emsd = ee.Number(feature.get('ST_EMSD')).format('%6.2f')
        st_qa = ee.Number(feature.get('ST_QA')).format('%6.2f')
        st_trad = ee.Number(feature.get('ST_TRAD')).format('%6.2f')
        st_urad = ee.Number(feature.get('ST_URAD')).format('%6.2f')
        return feature.set({
            'date': d.format('YYYY-MM-dd'),
            'ST_B10': st_b10,
            'ST_ATRAN': st_atran,
            'ST_CDIST': st_cdist,
            'ST_DRAD': st_drad,
            'ST_EMIS': st_emis,
            'ST_EMSD': st_emsd,
            'ST_QA': st_qa,
            'ST_TRAD': st_trad,
            'ST_URAD': st_urad
        })

    def get_datatable(self, featureCollection):
        columns = [
            "date",
            "ST_B10",
            "ST_ATRAN",
            "ST_CDIST",
            "ST_DRAD",
            "ST_EMIS",
            "ST_EMSD",
            "ST_QA",
            "ST_TRAD",
            "ST_URAD"
            "name"
        ]

        landsat_datatable = featureCollection.map(self.replace_numbers_by_strings).select(columns)
        return landsat_datatable

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
