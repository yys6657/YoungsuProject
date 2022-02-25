import requests
import pandas as pd
from requests_html import HTMLSession
from collections import defaultdict
from tqdm import tqdm
 

result_count = 20    #google 키워드 검색 시 결과 갯수 설정
keyword_file = 'google_keyword.csv'    # 카테고리 별 키워드 저장 csv파일
 
 
def get_source(keyword):
    q = '+'.join(keyword.split())
    url = f'https://www.google.com/search?q={q}&num={result_count+1}'

    try:
        session = HTMLSession()
        response = session.get(url)
        return response
 
    except requests.exceptions.RequestException as e:
        print(e)
 
 
def parse_results(response):   
    css_identifier_result = ".tF2Cxc"    
    css_identifier_link = ".yuRUbf a"    
     
    results = response.html.find(css_identifier_result)
 
    output = []
     
    for result in results:         
        url = result.find(css_identifier_link, first=True).attrs['href']
         
        if 'namu.wiki' in url:
            continue
         
        url = url.replace('https://','').replace('http://','')
        if url[-1] == '/':
            url = url[:-1]      
             
        output.append(url)
         
    return output
 
def google_result(word):
    res = get_source(word)
    return parse_results(res)
      
 
def get_keyword():   
    df = pd.read_csv(keyword_file,encoding = 'cp949')
    cat_info = df.columns.to_list()
    res = {}
    for x in cat_info:
        res[x] = df[x].dropna().tolist()
     
    return res
 
if __name__ == '__main__':
    csv_data = get_keyword()
 
    search_data = []
    res = defaultdict(dict)
    for cat in tqdm(csv_data.keys()):   
        for keyword in csv_data[cat]:       
            urls = google_result(keyword)
            search_data.extend(urls)
            res[cat].update({keyword : urls})          

    csv_list = []
    for k,v in res.items():
        for keyword,urls in v.items():
            if len(urls) == 0: continue      
            for url in urls:
                csv_list.append([k,keyword,url])
                 
    pd.DataFrame(csv_list,columns = ['category', 'keyword','url']).to_csv('google_keyword_search.csv',index = False,encoding = 'cp949')