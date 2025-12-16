import re
import pandas
import requests
from io import StringIO
from tqdm import tqdm
from pytip import FakeAgent
from lxml.html import fromstring, tostring