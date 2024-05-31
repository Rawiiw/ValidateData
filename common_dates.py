import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt

class CommonDates:
    def __init__(self, df, excel_data, satellite, satellite_product=None, time_of_day=None):
        self.excel_data = excel_data
        self.satellite_name = satellite
        self.satellite_product = satellite_product
        self.time_of_day = time_of_day

        if satellite == 'modis':
            if satellite_product == 'aqua':
                self.satellite_column = 'LST_Day_1km' if time_of_day == 'day' else 'LST_Night_1km'
                self.view_time_column = 'Day_view_time' if time_of_day == 'day' else 'Night_view_time'
            elif satellite_product == 'terra':
                self.satellite_column = 'LST_Day_1km' if time_of_day == 'day' else 'LST_Night_1km'
                self.view_time_column = 'Day_view_time' if time_of_day == 'day' else 'Night_view_time'
            else:
                raise ValueError("Invalid satellite_product. Please select 'aqua' or 'terra'.")
        elif satellite == 'landsat':
            self.satellite_column = 'ST_B10'
            self.view_time_column = None
        else:
            raise ValueError("Invalid satellite_name. Please select 'modis' or 'landsat'.")

        # Проверка наличия необходимых колонок
        required_columns = ['date', self.satellite_column]
        if self.view_time_column:
            required_columns.append(self.view_time_column)

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"One or more columns {missing_columns} are missing from the DataFrame")

        if self.view_time_column:
            self.selected_column = df[['date', self.satellite_column, self.view_time_column]]
        else:
            self.selected_column = df[['date', self.satellite_column]]

    def _parse_date(self, date_string, time_string):
        if time_string:
            return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    def _find_matching_rows(self, satellite_datetime):
        matching_rows = self.excel_data.iloc[(self.excel_data['datetime'] - satellite_datetime).abs().argsort()[:1]]
        return matching_rows

    def _calculate_daily_average(self):
        daily_averages = defaultdict(list)
        for index, row in self.excel_data.iterrows():
            date = row['datetime'].date()
            daily_averages[date].append(row['value'])
        for date, values in daily_averages.items():
            daily_averages[date] = sum(values) / len(values)
        return daily_averages

    def _remove_outliers(self, data):
        mean = np.mean(data)
        std_dev = np.std(data)
        filtered_data = [x for x in data if (mean - 3 * std_dev) <= x <= (mean + 3 * std_dev)]
        return filtered_data

    def _remove_obvious_outliers(self, data):
        filtered_data = [x for x in data if 0 <= x <= 50]  # Допустимый диапазон температур
        filtered_data = [filtered_data[i] for i in range(len(filtered_data) - 1) if
                         abs(filtered_data[i] - filtered_data[i + 1]) <= 10]
        return filtered_data

    def _remove_matches_outliers(self, matches):
        values = [float(match['value']) for match in matches]
        mean = np.mean(values)
        std_dev = np.std(values)
        cleaned_matches = [match for match in matches if
                           (mean - 3 * std_dev) <= float(match['value']) <= (mean + 3 * std_dev)]
        return cleaned_matches

    def _remove_matches_based_on_difference(self, matches):
        differences = []
        for i in range(0, len(matches), 2):
            diff = abs(float(matches[i]['value']) - float(matches[i + 1]['value']))
            differences.append(diff)

        std_dev = np.std(differences)
        threshold = 3 * std_dev

        cleaned_matches = []
        for i in range(0, len(matches), 2):
            if abs(float(matches[i]['value']) - float(matches[i + 1]['value'])) <= threshold:
                cleaned_matches.extend([matches[i], matches[i + 1]])

        return cleaned_matches

    def match_data(self, time_interval_minutes=None):
        matches = []

        # Сначала удаляем явные выбросы
        cleaned_values = self._remove_obvious_outliers(self.excel_data['value'].tolist())
        removed_values = set(self.excel_data['value']) - set(cleaned_values)
        self.excel_data = self.excel_data[self.excel_data['value'].isin(cleaned_values)]

        # Затем применяем стандартное удаление выбросов через 3 сигмы
        cleaned_values = self._remove_outliers(self.excel_data['value'].tolist())
        removed_values = set(self.excel_data['value']) - set(cleaned_values)
        self.excel_data = self.excel_data[self.excel_data['value'].isin(cleaned_values)]

        daily_averages = self._calculate_daily_average()

        for index, row in self.selected_column.iterrows():
            satellite_date = row['date']
            satellite_time = None
            if self.view_time_column:
                satellite_time = row[self.view_time_column]
            satellite_datetime = self._parse_date(satellite_date, satellite_time)
            matching_rows = self._find_matching_rows(satellite_datetime)

            if matching_rows.empty:
                continue

            for _, match_row in matching_rows.iterrows():
                ground_datetime = match_row['datetime']
                if time_interval_minutes is not None:
                    time_diff = abs(ground_datetime - satellite_datetime)
                    if time_diff <= timedelta(minutes=time_interval_minutes):
                        if self.satellite_product:
                            satellite_product_str = self.satellite_product.capitalize()
                        else:
                            satellite_product_str = ''
                        if self.time_of_day:
                            time_of_day_str = self.time_of_day.capitalize()
                        else:
                            time_of_day_str = ''
                        source = f'Satellite - {self.satellite_name} {satellite_product_str} {time_of_day_str}'
                        value = row[self.satellite_column]
                        matches.append({'source': source, 'datetime': satellite_datetime, 'value': float(value)})
                        matches.append({'source': 'Ground', 'datetime': ground_datetime, 'value': float(match_row['value'])})
                else:
                    if self.satellite_product:
                        satellite_product_str = self.satellite_product.capitalize()
                    else:
                        satellite_product_str = ''
                    if self.time_of_day:
                        time_of_day_str = self.time_of_day.capitalize()
                    else:
                        time_of_day_str = ''
                    source = f'Satellite - {self.satellite_name} {satellite_product_str} {time_of_day_str}'
                    value = row[self.satellite_column]
                    matches.append({'source': source, 'datetime': satellite_datetime, 'value': float(value)})
                    matches.append({'source': 'Ground', 'datetime': ground_datetime, 'value': float(match_row['value'])})

        # Удаление выбросов из matches
        matches = self._remove_matches_outliers(matches)

        # Удаление выбросов на основе разницы значений
        matches = self._remove_matches_based_on_difference(matches)

        return matches, daily_averages

