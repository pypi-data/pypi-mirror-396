import os
import time
import numpy
import pickle
import pandas
import datetime
import requests
from tqdm import tqdm
from pathlib import Path
from abc import abstractmethod
from pytip import date_to_string, FakeAgent
from pytip import check_file, file_pickle
from ..tools import (
    duplicate_name, convert_code_market, dataframe_fill_nat
)