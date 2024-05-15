import ee
import pandas as pd
import os
from common_dates import CommonDates
from excel_manager import ExcelManager
from aqua_data import AquaDataManager
from landsat_data import LandsatDataManager
from rsme_mbe import calculate_rmse_mbe
from plot_data import plot_data
from map_viewer import MapViewer
from output_maker import create_csv, create_excel
from report import create_pdf_report
from terra_data import TerraDataManager


def authenticate_ee():
    ee.Authenticate()
    ee.Initialize(project='ee-kosinova')


def select_satellite():
    while True:
        satellite_choice = input("Выберите спутник (modis/landsat): ").lower()
        if satellite_choice in ["modis", "landsat"]:
            satellite_product = None
            day_or_night = None
            if satellite_choice == "modis":
                satellite_product = input("Выберите тип данных (Aqua/Terra): ").lower()
                if satellite_product not in ["aqua", "terra"]:
                    print("Некорректный тип данных для MODIS.")
                    continue
                day_or_night = input("Выберите Day или Night: ").lower()
                if day_or_night not in ["day", "night"]:
                    print("Некорректный выбор Day или Night.")
                    continue
            # Для Landsat нет запроса временного промежутка
            return satellite_choice, satellite_product, day_or_night
        else:
            print("Некорректный выбор спутника.")


def select_excel_data():
    excel_manager = ExcelManager()
    excel_manager.select_excel_file()
    if not excel_manager.read_excel():
        print("Не удалось прочитать данные из файла Excel.")
    else:
        excel_manager.print_data()
    return excel_manager


def get_coordinates():
    print("Введите координаты точки в формате 'широта,долгота':")
    coordinates = list(map(float, input("Координаты: ").split(',')))
    return coordinates


def process_data(matches, daily_averages):
    print("ID\tSatellite name\tSatellite value\tSatellite Datetime\tGround value\tGround Datetime")
    for idx in range(0, len(matches), 2):
        satellite_match = matches[idx]
        ground_match = matches[idx + 1]
        satellite_source = satellite_match['source']
        satellite_datetime = satellite_match['datetime']
        satellite_value = satellite_match['value']
        ground_value = ground_match['value']
        ground_datetime = ground_match['datetime']
        if 'source' in satellite_match:
            satellite_source = satellite_match['source']
            if len(satellite_source.split(' - ')) > 1:
                satellite_name = satellite_source.split(' - ')[1]
            else:
                satellite_name = "Landsat"
        else:
            satellite_name = "Landsat"
        print(
            f"{idx + 1}\t{satellite_name}\t{satellite_value}\t{satellite_datetime}\t{ground_value}\t{ground_datetime}")

    rmse, mbe = calculate_rmse_mbe(matches)
    print(f"RMSE: {rmse}")
    print(f"MBE: {mbe}")


def save_table(df, matches, excel_data):
    save_table = input("Хотите ли вы сохранить таблицу со значениями? (да/нет): ").lower()
    if save_table == "да":
        format_choice = input("Выберите формат для сохранения (csv/excel): ").lower()
        if format_choice in ["csv", "excel"]:
            matched_dates_df = pd.DataFrame(matches).rename(columns={'datetime': 'Common Date'})
            df = pd.concat([df, matched_dates_df], axis=1)
            excel_data = excel_data.rename(columns={'datetime': 'Ground Date', 'value': 'Ground Value'})
            df = pd.concat([df, excel_data], axis=1)
            os.makedirs("Tables", exist_ok=True)
            if format_choice == "csv":
                create_csv(df, folder="Tables")
            else:
                create_excel(df, folder="Tables")
        else:
            print("Некорректный выбор формата.")
    elif save_table == "нет":
        print("Таблица не сохранена.")
    else:
        print("Некорректный ответ.")


if __name__ == "__main__":
    authenticate_ee()
    excel_manager = select_excel_data()
    coordinates = get_coordinates()
    date_start = excel_manager.date_start.strftime('%Y-%m-%d')
    date_end = excel_manager.date_end.strftime('%Y-%m-%d')
    satellite_choice, satellite_product, day_or_night = select_satellite()
    satellite_data_manager = None
    time_interval_minutes = None

    if satellite_choice == "modis":
        if satellite_product in ["aqua", "terra"]:
            time_interval_minutes = int(input("Введите временной промежуток: "))
            satellite_data_manager = AquaDataManager() if satellite_product == "aqua" else TerraDataManager()
    elif satellite_choice == "landsat":
        satellite_data_manager = LandsatDataManager()

        time_interval_minutes = None

    if satellite_data_manager:
        lst = satellite_data_manager.get_image_collection(coordinates, date_start, date_end)
        featureCollection = satellite_data_manager.get_feature_data(lst, coordinates)
        df = satellite_data_manager.create_dataframe(featureCollection)
        excel_data = excel_manager.data
        common_dates = CommonDates(df, excel_data, satellite_choice, satellite_product, day_or_night)


        matches, daily_averages = common_dates.match_data(time_interval_minutes)
        process_data(matches, daily_averages)
        plot_data(satellite_choice, matches, time_interval_minutes, satellite_product, day_or_night)
        map_viewer = MapViewer(coordinates, date_start, date_end)
        map_viewer.display_map()
        save_table(df, matches, excel_data)
        create_pdf_report(df, matches, satellite_choice, date_start, date_end)
    else:
        print("Некорректный выбор спутника.")








