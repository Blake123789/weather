import requests
import json
from bs4 import BeautifulSoup

#print('my __name__ is ', __name__)

class WeaG:
    web="https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/web.html"
    site="https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json"
    URLS=["https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001",
          "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001",
          "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001" ]


    def __init__(self):
        self._init_env('env.json')
        self.params = {'Authorization': self.env['KEY']}        
        self.sites= {}
        self._init_web()
        self._init_apis()

    def _init_env(self, env_json):
        default = {'KEY': None,
                   'TIMEOUT' : 10}
        with open('env.json', 'r', encoding='utf-8') as f:
            env=json.load(f)
        
        self.env = default.copy()
        for k in env:
            if k in default:
                self.env[k] = env[k] 

    def _init_web(self):
        r=requests.get(__class__.site)
        if r.status_code == 200:
            self.sites={s['STname']:s['ID'] for s in r.json()}
        r.close()

    def _init_apis(self):
        for url in __class__.URLS :
            r = requests.get(url, params=self.params)
            if r.status_code == 200:
               # j = r.json()
                for s in r.json()['records']['Station']:
                    if s['StationName'] in self.sites:
                        if type(self.sites[s['StationName']])==str:
                            pass
                        else:
                            self.sites[s['StationName']].append(url)
                    else :
                        self.sites[s['StationName']]=[url]
            r.close()

    def grab(self, site):
        r = self.sites.get(site)
        if type(r) == list:
            return self._grab_apis(site)
        if type(r) == str:
            return self._grab_web(site)
        return {}
    
    def _grab_web(self, site):
        info = {}
        if sid := self.sites.get(site):
            url=__class__.web.replace('web',sid)
            r = requests.get(url)
            if r.status_code == 200:
               soup = BeautifulSoup(r.text, 'html.parser')
               if a := soup.find(headers="rain"):
                   info['R']=float(a.text)
               if a := soup.find(headers="hum"):
                   info['H']=float(a.text)/100
               if a := soup.find(class_="tem-C"):
                   info['T']=float(a.text)
               if a := soup.find(headers="time"):
                   info['O']=a.text
            r.close()
        return info
        
    def _grab_apis(self, site) : 
            info={}  
            for url in self.sites[site] :
                self.params.update({'StationName' : site})    
                r = requests.get(url, params=self.params)
                if r.status_code == 200:
                    j = r.json()
                    for k in j['records']['Station']:
                       if k['StationName'] == site:
                           info['O'] = k['ObsTime']['DateTime'].split('+')[0]
                           if 'WeatherElement' in k:
                               info['T'] = k['WeatherElement']['AirTemperature']
                               info['H'] = k['WeatherElement']['RelativeHumidity'] /100
                           elif 'RainfallElement' in k:
                               info['R'] = k['RainfallElement']['Now']['Precipitation']
            return info

    @staticmethod  # 可不用帶self
    #def tostr(self, info):
    def tostr(info):
        if not info:
            return "查無天氣資料"
        r=[]
        if 'O' in info :
            r.append(f'時間: {info["O"]}')
        if 'T' in info :
            r.append(f'溫度: {info["T"]:.1f}度')
        if 'H' in info :
            r.append(f'濕度: {info["H"]:.1%}')
        if 'R' in info :
            r.append(f'雨量: {info["R"]:.1f}mm')
        
        return '\n'.join(r)
#ch_name={'O':'時間' , 'T' : '溫度' , 'H' : '濕度' , 'R' : '雨量' }
    

#w.sites
#w.grab('國三S217K')

if __name__== "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('site')  # by ur design
    args=parser.parse_args()


    w=WeaG()
    #w.grab(args.site)
    #print(w.grab(args.site))
    print(w.tostr(w.grab(args.site)))

    #print(w.grab('城西'))
    #print(w.grab('西拉雅'))
    #print(w.grab('中央大學'))