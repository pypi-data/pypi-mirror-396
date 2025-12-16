import re
import json
import time
# import socks
import socket
import pandas
import chardet
import requests
import datetime
from io import StringIO
from urllib import parse
from datetime import timedelta
from pytip import FakeAgent, date_to_string, elapsed_time
from ..tools import (
    duplicate_name, convert_code_market, dataframe_fill_nat
)