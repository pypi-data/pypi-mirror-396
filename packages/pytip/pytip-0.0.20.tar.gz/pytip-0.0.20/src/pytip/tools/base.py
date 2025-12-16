import re
import numpy
import pandas
import string
import random
import datetime
import itertools
# import xlrd
# import openpyxl


# import matplotlib.pyplot as plt
# from matplotlib.font_manager import fontManager
REGEX_DATETIME = {
    r'[\d]{4}-[\d]{2}-[\d]{2}.[A-Z]{2}[\d]{1,2}:[\d]{1,2}:[\d]{1,2}':
    r'%Y-%m-%d.%p%I:%M:%S', # '2022-07-31.AM3:02:30'
    r'[\d]{4}\.[\d]{2}\.[\d]{2}\.[A-Z]{2}[\d]{1,2}:[\d]{1,2}':
    r'%Y.%m.%d.%p%I:%M',    # '2022.07.31.AM3:02',
    r"^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}":
    r'%Y/%m/%d %H:%M:%S',    # '2023/03/28 10:40:00',
}
