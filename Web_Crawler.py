from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException,TimeoutException
from urllib.parse import urlparse
from tldextract import extract
from multiprocessing import Process,current_process
import math
from tqdm.notebook import tqdm
import MySQLdb as mysql
import random
from PIL import Image
import warnings
warnings.filterwarnings("ignore")


process_cnt = 5
file_path = './url_list.txt'
png_path = './png_data'
html_path = './html_data'


class Crawler:
    def __init__(self,url_list:list):          
        self.options = Options()        
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")                                   
        self.url_list = url_list
        self.run()        
        
    def set_chrome_driver(self): 
        '''selenium chromedirver setting'''       
        options = self.options
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)        
        self.driver.implicitly_wait(2)
        self.driver.set_page_load_timeout(10)
        
    def get_url(self,url):
        '''selenium url get'''
        self.driver.get(url)
        
    def png_resizing(self):
        '''png size reduce'''
        path = self.path
        file_path = f'{png_path}/{path}.jpg'
        img = Image.open(file_path)
        img = img.convert('RGB')        
        img.save(f'{file_path[:-4]}.jpg','JPEG',qualty=75)
        
    def get_page_source(self):
        '''url html data save'''
        r = self.driver.page_source
        path = self.path
        with open(f'{html_path}/{path}.txt','w',encoding = 'utf8') as fw:
            fw.write(r)        

    def get_screenshot(self):  
        #selenium page capture, 주석처리 해제시 페이지의  모든 스크롤범위 만큼 캡쳐        
        '''
        required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
        required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(required_width, required_height)  
        '''          
        path = self.path
        file_path = f'{png_path}/{path}.jpg'
        self.driver.find_element(By.TAG_NAME,'body').screenshot(file_path)

        return file_path
    
   
    def run(self):        
        self.set_chrome_driver()
        urls = self.url_list
        for url in tqdm(urls,desc=current_process().name):
            try:
                self.path = urlparse(url).netloc
                #fname = extract_domain(url)
                self.get_url(url)
                self.get_screenshot()
                self.png_resizing()
                self.get_page_source()
            except WebDriverException:                
                logging(f'{url}\tpage_down\n')
            except Exception as e:
                logging(f'{url}\t{e}\n')
        self.driver.quit()
            
    def __del__(self):
        self.driver.quit()


def logging(log):
    with open(f'err_log.txt','a',encoding = 'utf8') as fw:
        fw.write(log)  


def split_ulist(url_list):
    '''selenium broser 별 url 분배'''
    lurl = len(url_list)
    length = math.ceil(lurl/process_cnt)
    res = []
    for x in range(process_cnt):
        r = url_list[length*x: length*(x+1)]
        if r == []:
            break
        res.append(r)    
    return res

def file_read(path:str):
    with open(path,'r',encoding = 'cp949') as fr:
        data = fr.readlines()
    return data


def file_read(url_file:str):     
    '''url list stored file'''
    r = []
    with open(url_file,'r') as fr:
        while True:
            line = fr.readline()
            if not line:
                break
            r.append(line.rstrip())
    random.shuffle(r)
    return r

if __name__ == '__main__':       
    data = file_read(file_path)           
    print(f'URL 총 수량 : {len(data)}')
    ulist = split_ulist(data)
    ps =[]
    for x in ulist:        
        p = Process(target = Crawler,args = (x,))
        ps.append(p)
        p.start()
    
    for p in ps:
        p.join()
   
    
