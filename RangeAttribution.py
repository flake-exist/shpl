import pandas as pd
import numpy as np

import re
import argparse

from datetime import datetime
from dateutil.relativedelta import relativedelta

from shapleyLib import Shapley
from CONSTANTS import *

class RangeAttribution:
    
    def __init__(self,date_start,date_finish,freq):
        
        self.MinInHour = MinInHour
        self.SecInMinute = SecInMinute
        self.MILISECONDS = MILISECONDS
        self.date_start = date_start
        self.date_finish = date_finish
        self.freq = freq

        
    def Preprocessing(self,path,sep=",",TIME_ZONE=3,MILISEC_FORMAT=True):
        
        if MILISEC_FORMAT == True:
            MiliSecDev = self.MILISECONDS
        else:
            MiliSecDev = 1

        secondShift = TIME_ZONE * self.MinInHour * self.SecInMinute

        data = pd.read_csv(path,sep)
        
        if np.all(data.columns.isin(NECESSARY_COLS)) == True:
            pass
        else:
            raise ValueError("DataFrame must contain columns : {}".format(NECESSARY_COLS))
            
        data['last_touch'] = data.timeline.apply(lambda x:int(x.split("=>")[-1]))
        data['LTsimple_date'] = data.last_touch.apply(lambda x:datetime.utcfromtimestamp(int(x/MiliSecDev) + secondShift).strftime('%Y-%m-%d'))
        data['LTdatetime'] = data.last_touch.apply(lambda x:datetime.fromtimestamp(int(x/MiliSecDev) + secondShift))

        return data
    
    def RangeData(self,data,date_start,date_finish):
        
        data_period = data[(data.LTdatetime >= date_start) & (data.LTdatetime < date_finish)]
        data_grouped_0 = data_period.groupby(['user_path'])['ClientID'].count()
        data_grouped_1 = data_grouped_0.to_frame()
        data_grouped_1.reset_index(level=0, inplace=True)
        data_grouped_1.rename(columns=RENAME_COLS,inplace=True)

        return data_grouped_1
    
    
    
    def RangeCreator(self):
        range_store = []

        if re.findall(DAY_PATTERN,self.freq) != []:
            freq_target = self.freq
            window_target = int(re.findall(DAY_WINDOW,self.freq)[0])
            tRange = pd.date_range(start=self.date_start, end=self.date_finish,freq=freq_target).to_pydatetime()

            for date in tRange:
                lRange = ((date,date + relativedelta(days=window_target)))
                range_store.append(lRange)
            return range_store

        elif re.findall(MONTH_PATTERN,self.freq) != []:
            freq_target = self.freq
            window_target = int(re.findall(MONTH_WINDOW,self.freq)[0])
            tRange = pd.date_range(start=self.date_start, end=self.date_finish,freq=freq_target).to_pydatetime()

            for date in tRange:
                lRange = (datetime(date.year,date.month,1),datetime(date.year,date.month,1) + relativedelta(months=window_target))
                range_store.append(lRange)
            return range_store

        else:
            raise ValueError(
                '''Incorrect frequency format.You can use days and months for exploring periods.
                Example : For days - 1D or 14d, For months - 1m or 2M ''')
            
        
    def RangeCalc(self,data_period,date_start,date_finish):
    
        if data_period.shape[0] == 0:
            return pd.DataFrame(columns=["channel","shapley_value","date_start","date_finish"])
        else:
            shapley = Shapley(data_period)
            attributed_values = shapley.Evaluate()
            attributed_data = pd.DataFrame(
                {"channel":list(attributed_values.keys()),
                 "shapley_value":list(attributed_values.values()),
                 "date_start":date_start,
                 "date_finish":date_finish})

            return attributed_data
        
    def AllRangeCalc(self,path,sep=",",time_zone=3,milisec_format=True):
        store = []
        
        #Calculate Date Ranges
        date_range = self.RangeCreator()
        
        data = self.Preprocessing(path,sep,time_zone,milisec_format)
        
        for drange in date_range:
            print(drange)
            
            data_period = self.RangeData(
                data=data,
                date_start=drange[0],
                date_finish=drange[1])
            
            shapley_values = self.RangeCalc(
                data_period=data_period,
                date_start=drange[0],
                date_finish=drange[0])
            
            store.append(shapley_values)
        
        result = pd.concat(store)
        
        return result
    
    
    
if __name__ == "__main__":
    
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--date_start', action='store', type=str, required=True)
    my_parser.add_argument('--date_finish', action='store', type=str, required=True)
    my_parser.add_argument('--freq', action='store', type=str, required=True)
    my_parser.add_argument('--input_path', action='store', type=str, required=True)
    my_parser.add_argument('--output_path', action='store', type=str, required=True)

    args = my_parser.parse_args()
    
    myAttr = RangeAttribution(date_start=args.date_start,date_finish=args.date_finish,freq=args.freq)
    r = myAttr.AllRangeCalc(args.input_path)
    r.to_csv(args.output)