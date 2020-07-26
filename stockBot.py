from bs4 import BeautifulSoup
import numpy as np
import requests
import pandas as pd
import threading
from tqdm import tqdm
import os.path

class Stock():


    def __init__(self):
        self.datas = pd.DataFrame(columns=['name', 'code', '시가총액', '외국인보유률', 'PER', '추정PER', 'PBR', '동일업종 PER'])
        filename = 'stocks.xlsx'
        if os.path.exists(filename):
            self.datas = pd.read_excel(filename,sheet_name="Sheet1")
        else:
            self.url = "https://finance.naver.com/item/main.nhn?code="
            code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
            code_df['종목코드'] = pd.Series(code_df['종목코드'], dtype=str)
            code_df['종목코드'] = code_df['종목코드'].str.zfill(6)
            code_df = code_df.loc[:, ['회사명', '종목코드']]
            code_df.columns = ['name', 'code']
            self._crawling(code_df)
            self.datas.to_excel(filename, index=False)

    def _crawling(self,code_df):
        for i in tqdm(range(len(code_df))):
            row = code_df.iloc[i]
            try:
                url = self.url + row['code']
                response = requests.get(url).text
                soup = BeautifulSoup(response,'html.parser')
                temp_list = [row['name'],row['code']]
                aside = soup.find('div',class_="aside_invest_info")
                infodiv = aside.find('div',class_="tab_con1")
                temp_list.append(self._get_all_price(infodiv))
                temp_list.append(self._get_foreign(infodiv))
                temp_list+=self._get_dart(infodiv)
                temp_list.append(self._get_same_biz(infodiv))
                #self.datas.append(temp_list)
                self.datas.loc[len(self.datas)]=temp_list
                #print(self.datas.head())
            except:
                #print("error")
                pass

    def _get_all_price(self, infodiv):
        first = infodiv.find('div',class_='first')
        first_table = first.table
        tr = first_table.find('tr',class_='strong')
        td = tr.find('td')
        return td.text.replace('\t','').replace('\n','')

    def _get_foreign(self,infodiv):
        gray = infodiv.find("div",class_='gray')
        tr = gray.find('tr',class_='strong')
        return tr.find('em').text

    def _get_dart(self,infodiv):
        dart=[]
        per_table = infodiv.find('table',class_='per_table')
        ems = per_table.find_all('em')
        for i in range(0,len(ems)-1,2):
            dart.append(ems[i].text)
        return dart

    def _get_same_biz(self,infodiv):
        same_biz = infodiv.find('table',attrs={"summary":"동일업종 PER 정보"})
        return same_biz.find('em').text

    def get_items(self):
        return self.datas


st = Stock()
print(st.get_items())
