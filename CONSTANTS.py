import re

MinInHour = 60
SecInMinute = 60
MILISECONDS = 1000

DAY_PATTERN = r'^\d{1,365}[Dd]$'
DAY_WINDOW = r'^(\d{1,365})[Dd]$'

MONTH_PATTERN = r'^\d{1,120}[Mm]$'
MONTH_WINDOW = r'^(\d{1,120})[Mm]$'

NECESSARY_COLS = ["ClientID","user_path","timeline"]
RENAME_COLS = {'user_path':'path','ClientID':'total_conversions'}