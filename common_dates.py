from collections import defaultdict
from datetime import datetime, timedelta

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
            if satellite_product is None:
                satellite_product = 'average'
        else:
            raise ValueError("Invalid satellite_name. Please select 'modis' or 'landsat'.")

        if self.view_time_column:
            self.selected_column = df[['date', self.satellite_column, self.view_time_column]]
        else:
            self.selected_column = df[['date', self.satellite_column]]

    def _parse_date(self, date_string, time_string):
        if time_string:
            return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(date_string, '%Y-%m-%d')

    def _find_matching_rows(self, satellite_datetime):
        start_of_day = satellite_datetime.replace(hour=0, minute=0, second=0)
        end_of_day = satellite_datetime.replace(hour=23, minute=59, second=59)
        matching_rows = self.excel_data[
            ((self.excel_data['datetime'] >= start_of_day) & (self.excel_data['datetime'] <= end_of_day))
        ]
        return matching_rows

    def _calculate_daily_average(self):
        daily_averages = defaultdict(list)

        for index, row in self.excel_data.iterrows():
            date = row['datetime'].date()
            daily_averages[date].append(row['value'])

        for date, values in daily_averages.items():
            daily_averages[date] = sum(values) / len(values)

        return daily_averages

    def match_data(self, time_interval_minutes=None):
        matches = []

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
                        matches.append({'source': source, 'datetime': satellite_datetime, 'value': value})

                        matches.append({'source': 'Ground', 'datetime': ground_datetime, 'value': match_row['value']})
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
                    matches.append({'source': source, 'datetime': satellite_datetime, 'value': value})

                    matches.append({'source': 'Ground', 'datetime': ground_datetime, 'value': match_row['value']})

        return matches, daily_averages
