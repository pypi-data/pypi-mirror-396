from .base import *


class Infos:
    r"""Fn Guide 에서 주요한 자료 크롤링"""


    def __init__(self, ticker) -> None:
        self.ticker = ticker


    @property
    def get_tag(self):
        r""" KOSPI / KEI 기업분류 크롤링
        Return:
            { ticker : 'title': 'KOSPI 전기', 'sub_title': 'FICS 기업분류' }        
        """
        url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{self.ticker}"
        url += "&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"    
        response = requests.get(url, headers={'Headers':FakeAgent.random})
        response_lxml = fromstring(response.text)
        description = response_lxml.xpath('.//p[@class="stxt_group"]')
        title       = description[0].xpath('./span[contains(@class,"stxt1")]/text()')[0] 
        sub_title   = description[0].xpath('./span[contains(@class,"stxt2")]/text()')[0]
        title, sub_title = [re.sub(r"\s+", " ", t.replace(r"\xa0", " ")).strip() for t in [title, sub_title]]
        return { 
            self.ticker : { 
                'title':title, "sub_title":sub_title
            }
        }


    @property
    def get_table_market(self):
        r""" 사업 주요목록 """
        url  = f"https://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{self.ticker}"
        url += "&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
        xpath = ".//table[caption[@class='cphidden' and text()='매출비중 추이']]"
        response = requests.get(url, headers={'Headers':FakeAgent.random})
        response_lxml = fromstring(response.text)
        table = response_lxml.xpath(xpath)
        table = tostring(table[0], encoding='unicode')
        table = pandas.read_html(StringIO(table))[0]
        return table
