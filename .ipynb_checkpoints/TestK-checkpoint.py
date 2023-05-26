#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import requests   #3歳補正導入済み
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
from pytz import timezone
import copy
import numpy as np


st.title('テキトー指数研究所＠WEB')
st.header('園田・姫路・門別・地方交流重賞')
st.subheader('新パラメータ版')

st.write('   ')
st.info('【南関東版】\https://azzukky-n.streamlit.app/')
st.info('【JRA版】\https://azzukky-j.streamlit.app/')

st.write('   ')
st.write('   ')
st.write('●クラスが上がるほど、良く当たる傾向があります。')
st.write('●南関東の全レースにも使えますが、賞金理論を実装していません。')
st.write('●園田・姫路・門別・南関東・地方交流重賞以外も計算しますが、完全にでたらめです。')
st.write('●３歳戦はあまりあてになりません。')
st.write('●過去３走していない馬の指数はゼロになります。')
st.write('●中央からの転入馬の指数は大きくなりますので、指数よりも状態と騎手を重視してください。')
st.write('   ')
st.write('   ')


yosoubi = st.radio('いつのレース？', ['今日', '明日', '日付入力'])

utc_time = dt.now(timezone('Asia/Tokyo'))
jst_date_today = utc_time.strftime('%Y%m%d')
jst_time_tomorrow = utc_time + td(days = 1)
jst_date_tomorrow = jst_time_tomorrow.strftime('%Y%m%d')
kotoshi = utc_time.year

if yosoubi == '今日':
    nengappi = jst_date_today
elif yosoubi == '明日':
    nengappi = jst_date_tomorrow
elif yosoubi == '日付入力':
    nengappi = str(kotoshi) + st.text_input('レースの日付を入力：例0628')    
    
basho = st.radio('開催場所？', ['園田', '姫路', '門別', '大井', '船橋', '川崎', '浦和', '盛岡', '水沢', '金沢', '笠松', '名古屋', '高知', '佐賀'])

if basho == '大井':
    place = "2015"
elif basho == '船橋':
    place = "1914"
elif basho == '川崎':
    place = "2135"
elif basho == '浦和':
    place = "1813"
elif basho == '水沢':
    place = "1106"
elif basho == '金沢':
    place = "2218"
elif basho == '姫路':
    place = "2826"
elif basho == '名古屋':
    place = "2433"
elif basho == '佐賀':
    place = "3230"
elif basho == '高知':
    place = "3129"
elif basho == '笠松':
    place = "2320"
elif basho == '園田':
    place = "2726"
elif basho == '門別':
    place = "3601"
elif basho == '盛岡':
    place = "1006"
else:
    place = "0"    



race = st.number_input('【半角数字】レース番号？', 1, 12, 11)

race_for_keisan = nengappi + place + '00' + '00' + str(str(race).zfill(2))

st.write('   ')
st.subheader('計算するときはチェックボックスをチェック！')
st.subheader('次のレースを計算する前にチェックを外す！')

push = st.checkbox('チェック！！')
if push == True:
    
    st.write('計算には約1分かかります。しばらくお待ちください。')
    
    url = 'https://keiba.rakuten.co.jp/race_card/list/RACEID/' + race_for_keisan

    html = requests.get(url)
    html.encoding = 'UTF-8'
    soup = BeautifulSoup(html.text, "html.parser")
    syusso_uma = soup.find('table').find_all('a', attrs = {'href': re.compile('^https://keiba.rakuten.co.jp/horse_detail/')})
    profile = soup.find_all('td', attrs = 'profile')
    syusso_jockey = soup.find('table').find_all('a', attrs = {'href': re.compile('^https://keiba.rakuten.co.jp/jockey/')})
    odds = soup.find('table').find_all('span', attrs = {'rate'})
    
    if bool(syusso_uma) == False:
        print('該当レースはありません')
    else:
        rd = re.findall(r'\d+', url)[0][:8]
        racedate = dt.strptime(rd, '%Y%m%d')
        racename = soup.find('h2').text.replace('\u3000', ' ')
        racenumber = soup.find('h1').text[:-4]
        course_distance = soup.select('#raceInfomation > div > div.raceNote > ul.trackState.trackMainState > li.distance')[0].text.strip()
        if ',' in course_distance:
            course_distance = course_distance.replace(',' , '')
        else:
            coursedistance = course_distance
        race_course = course_distance[0]
        race_distance = int(re.findall(r'\d+', course_distance)[0])

        horse_id_list = []
        horse_name_list = []
        for uma in syusso_uma:
            horse_id = re.findall(r'\d+', uma['href'])[0]
            horse_id_list.append(horse_id)
            horse_name = uma.text
            horse_name_list.append(horse_name)

        weight_list = []
        gender_list = []
        age_list = []        
        for uma2 in profile:
            uma2_text = uma2.text
            weight = re.findall(r'\d\d.\d', uma2_text)[0]
            weight_list.append(weight)
            sei = re.findall(r'\D\d+', uma2_text)[0][0]
            gender_list.append(sei)
            rei = re.findall(r'\D\d+', uma2_text)[0][1:]
            age_list.append(rei)        

        syusso_list = [x1 + ' ' + x2 +  ' ' + x3 + ' ' + x4 for (x1, x2, x3, x4) in zip(horse_id_list, weight_list, gender_list, age_list)]

        jockey_list = []
        for uma3 in syusso_jockey:
            jockey = uma3.text
            jockey_list.append(jockey)

        umaban = []
        for i in range(len(horse_id_list)):
            umaban.append(i+1)

        odds_list = []        
        for od in odds:
            od_text = od.text
            horse_odd = re.findall(r'\d+.\d', od_text)
            if len(horse_odd) ==0:
                odds_list.append('---')
            else:
                odds_list.append(horse_odd[0])            
            
    horse_results = {}                                  
    for horse_id in syusso_list:
        time.sleep(1)
        url2 = 'https://keiba.rakuten.co.jp/horse_detail/detail/HORSEID/' + horse_id[:10].rstrip()    
        horse_results[horse_id] = pd.read_html(url2)[1].head(15)

    past_results = copy.deepcopy(horse_results)   #個々から下のコードに影響されないhorse_resultsのコピーを作る。

    processed_horse_results = {}
    for horse_id, df in past_results.items():

        df = df.drop(df.index[df['タイム'] == '-'])
        df['日付2'] = [dt.strptime(i, "%Y/%m/%d") for i in df['日付']]
        df['レース名2'] = df['レース名'].str.strip('[過去映像]')
        df['コース'] = df['距離'].map(lambda x:str(x)[0])
        df['距離2'] = df['距離'].map(lambda x:str(x)[1:]).astype(int)
        df['着順2'] = df['着順'].str.split('/', expand = True)[0].astype(int)
        df['差2'] = df['差'].astype(float)

        df.drop(['馬番', '人気', '上3F', 'R', '負担重量', '調教師', 'レース名', '距離', '着順', '日付', '差', '騎手'], axis = 1, inplace = True)

        df = df.loc[:, ['日付2', '競馬場', 'レース名2', 'コース', '距離2', '着順2', '差2', 'タイム']].dropna()
        df = df[(df['差2'] < 4.0)]
        df = df[(df['競馬場'] != '外国')]
        df.reset_index(inplace=True, drop=True)

        processed_horse_results[horse_id] = df

    zenso_list = []
    for horse_id, df in past_results.items():
        zenso = past_results[horse_id]['競馬場'][0]
        if 'Ｊ' in zenso:
            zenso_list.append('JRA')
        else:
            zenso_list.append(zenso)        
        
        
        
    def shisu(processed_horse_results):
        jra = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
        nankan = ['浦和', '船橋', '大井', '川崎']
        hyogo = ['園田', '姫路']
        tokai = ['名古屋', '笠松']
        others = ['水沢' '盛岡', '金沢', '高知', '佐賀']

        GI = ['チャン', 'フェブ']
        GII = ['東海Ｓ']
        GIII = ['根岸Ｓ', 'マーチ', 'アンタ', '平安Ｓ', 'プロキ', 'ユニコ', 'レパー', 'エルム', 'シリウ', 'みやこ', '武蔵野', 'カペラ']   

        tekito_shisu = {}
        for horse_id, p_df in processed_horse_results.items():  #p_dfはprocessed dafa frame
            if len(p_df) < 3:
                tekito_shisu[horse_id] = 0

            elif len(p_df) == 3:

                base_number = []
                for t in range(3):                    
                
                    if 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GI:  
                        kijun = 800
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GII:  
                        kijun = 700
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GIII:  
                        kijun = 650   
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and 'オープン' in p_df.iloc[t]['レース名2']:  
                        kijun = 600
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '３勝' in p_df.iloc[t]['レース名2']:  
                        kijun = 500
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '２勝' in p_df.iloc[t]['レース名2']:
                        kijun = 400
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '１勝' in p_df.iloc[t]['レース名2']:  
                        kijun = 300
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '未勝利' in p_df.iloc[t]['レース名2']:
                        kijun = 200
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '新馬' in p_df.iloc[t]['レース名2']:
                        kijun = 200    


                    elif '帝王賞' in p_df.iloc[t]['レース名2']:  
                        kijun = 800
                    elif '東京大賞典' in p_df.iloc[t]['レース名2']:  
                        kijun = 800
                    elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 700
                    elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 600
                    elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 500

                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 500
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 450
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 400
                    elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2']) \
                        and ('Ｓ１' and 'Ｓ２' and 'Ｓ３' not in p_df.iloc[t]['レース名2']): 
                        kijun = 350 
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' not in p_df.iloc[t]['レース名2'])): #A2
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' in p_df.iloc[t]['レース名2'])): #A2B1
                        kijun = 270
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])): #B1
                        kijun = 240  
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' in p_df.iloc[t]['レース名2'])): #B1B2
                        kijun = 230        
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' and 'Ｂ３' not in p_df.iloc[t]['レース名2'])): #B2  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ３' in p_df.iloc[t]['レース名2'])):  #B2B3
                        kijun = 210
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])): #B3
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' in p_df.iloc[t]['レース名2'])): #B3C1
                        kijun = 180
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ３' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])): #C1
                        kijun = 160
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' in p_df.iloc[t]['レース名2'])): #C1C2
                        kijun = 150
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])): #C2
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ３' in p_df.iloc[t]['レース名2'])): #C2C3
                        kijun = 130
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' not in p_df.iloc[t]['レース名2'])): #C3  
                        kijun = 120

                    elif p_df.iloc[t]['競馬場'] in hyogo and ('ＪＲＡ交流' in p_df.iloc[t]['レース名2']):  
                        kijun = 280    
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('重賞' in p_df.iloc[t]['レース名2']):  
                        kijun = 350
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 280
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ１'and 'Ａ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 260
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ１' and 'Ｂ１' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 240
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ２' and 'Ｂ１' in p_df.iloc[t]['レース名2']):  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])):
                        kijun = 200        
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ１' and 'Ｂ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 180
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ１' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])):
                        kijun = 160     
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ２' and 'Ｃ１' in p_df.iloc[t]['レース名2']):  
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 120
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ１' and 'Ｃ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 110
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 100
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ２' and 'Ｃ３' in p_df.iloc[t]['レース名2']):  
                        kijun = 90   
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 80

                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 280
                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 240 
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ａ' in p_df.iloc[t]['レース名2']:  
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ｂ' in p_df.iloc[t]['レース名2']:
                        kijun = 130  
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ｃ' in p_df.iloc[t]['レース名2']:
                        kijun = 60                    

                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 330
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 270
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 210
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 190
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 160
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 150
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 130
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 100
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 90
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 80
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 70

                    elif p_df.iloc[t]['競馬場'] in others and 'オープン' in p_df.iloc[t]['レース名2'] \
                        and 'Ｊｐｎ' not in p_df.iloc[t]['レース名2']:  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in others and 'Ａ' in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ' not in p_df.iloc[t]['レース名2']:  
                        kijun = 200

                    else:
                        kijun = 60

                    base_number.append(kijun)

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]
                    
    #着差は楽天競馬とnetkeibaで書き方が違う。地方版は楽天競馬に対応            
                chakusa = []
                for u in range(3):

                    if p_df.iloc[u]['着順2'] == 1:
                        if p_df.iloc[u]['差2'] > 0.7:
                            race_chakusa = 1.5
                        elif 0.5 < p_df.iloc[u]['差2'] <= 0.7:
                            race_chakusa = 1.3
                        elif 0.3 < p_df.iloc[u]['差2'] <= 0.5:
                            race_chakusa = 1.2    
                        else:
                            race_chakusa = 1.0
                    elif p_df.iloc[u]['着順2'] > 1:
                        if 0.0 <= p_df.iloc[u]['差2'] <= 0.5:
                            race_chakusa = 1.0
                        elif 0.5 < p_df.iloc[u]['差2'] <= 1.0:
                            race_chakusa = 0.8
                        elif 1.0 < p_df.iloc[u]['差2'] <= 2.0:
                            race_chakusa = 0.5
                        else:
                            race_chakusa = 0.2

                    chakusa.append(race_chakusa)

                a, b, c = chakusa[0], chakusa[1], chakusa[2]


                #連勝係数       
                if p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1 and p_df.iloc[2]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2']) / 4
                    if rensho < -0.7:
                        e = 1.25
                    elif -0.7 <= rensho < -0.5:
                        e = 1.20 
                    elif -0.5 <= rensho < -0.3:
                        e = 1.15
                    else:
                        e = 1.10
                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1: # and p_df.iloc[2]['着順2'] != 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] +p_df.iloc[2]['差2']) / 4
                    if rensho < -0.7:
                        e = 1.20
                    elif -0.7 <= rensho < -0.5:
                        e = 1.15    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.10
                    else:
                        e = 1.05
                else:
                    e = 1.0

                #斤量補正        
                #if '牝' in horse_id:
                    #f = kijun1 * 0.1 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                #else:
                    #f = kijun1 * 0.1 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))

                #斤量補正        
                if 800 <= race_distance <= 1000:
                    if '牝' in horse_id:
                        f = kijun1 * 0.15 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.15 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif 1000 < race_distance <= 1400:
                    if '牝' in horse_id:
                        f = kijun1 * 0.1166 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.1166 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif 1400 < race_distance <= 1800:
                    if '牝' in horse_id:
                        f = kijun1 * 0.0833 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.0833 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif race_distance > 1800:
                    if '牝' in horse_id:
                        f = kijun1 * 0.05 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.05 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                    
                    
                    
                    
                #休養係数        
                if td(weeks = 0) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 12):
                    g = 1.0
                elif td(weeks = 12) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 24):
                    g = 0.95
                elif td(weeks = 24) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (racedate - p_df.iloc[0]['日付2']):
                    g = 0.8
                else:
                    g = 1.0

                #レース毎の牝馬補正    
                hinba = []
                for v in range(3):

                    if '牝' in p_df.iloc[v]['レース名2']:
                        female = 0.9
                    else:
                        female = 1.0
                    hinba.append(female)

                a1, b1, c1 = hinba[0], hinba[1], hinba[2]

                #距離係数                
                av_dist = (p_df.iloc[0]['距離2'] + p_df.iloc[1]['距離2'] + p_df.iloc[2]['距離2']) / 3 
                if 800 <= race_distance <= 1000:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1000 < race_distance <= 1400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 250 and abs(race_distance - av_dist) > 250:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 400 and av_dist < 1600:
                        h = 0.9
                    else:
                        h = 1.0

                #コース係数
                if race_course == 'ダ':
                    if p_df.iloc[0]['コース'] == '芝' and p_df.iloc[1]['コース'] == '芝' and p_df.iloc[2]['コース'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0           


                ts = ((kijun1 *1.5 *a *a1 + kijun2 *b *b1 + kijun3 *c *c1) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts)                    
                
                
                
#4戦以上出走している馬の指数                
            else:
                base_number = []
                for t in range(4):                    
                
                    if 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GI:  
                        kijun = 800
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GII:  
                        kijun = 700
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and p_df.iloc[t]['レース名2'][:3] in GIII:  
                        kijun = 650   
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and 'オープン' in p_df.iloc[t]['レース名2']:  
                        kijun = 600
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '３勝' in p_df.iloc[t]['レース名2']:  
                        kijun = 500
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '２勝' in p_df.iloc[t]['レース名2']:
                        kijun = 400
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '１勝' in p_df.iloc[t]['レース名2']:  
                        kijun = 300
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '未勝利' in p_df.iloc[t]['レース名2']:
                        kijun = 200
                    elif 'Ｊ' in p_df.iloc[t]['競馬場'] and '新馬' in p_df.iloc[t]['レース名2']:
                        kijun = 200    


                    elif '帝王賞' in p_df.iloc[t]['レース名2']:  
                        kijun = 800
                    elif '東京大賞典' in p_df.iloc[t]['レース名2']:  
                        kijun = 800
                    elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 700
                    elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 600
                    elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 500

                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 500
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 450
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 400
                    elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2']) \
                        and ('Ｓ１' and 'Ｓ２' and 'Ｓ３' not in p_df.iloc[t]['レース名2']): 
                        kijun = 350 
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' not in p_df.iloc[t]['レース名2'])): #A2
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' in p_df.iloc[t]['レース名2'])): #A2B1
                        kijun = 270
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])): #B1
                        kijun = 240  
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' in p_df.iloc[t]['レース名2'])): #B1B2
                        kijun = 230        
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ１' and 'Ｂ３' not in p_df.iloc[t]['レース名2'])): #B2  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ３' in p_df.iloc[t]['レース名2'])):  #B2B3
                        kijun = 210
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])): #B3
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' in p_df.iloc[t]['レース名2'])): #B3C1
                        kijun = 180
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ３' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])): #C1
                        kijun = 160
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' in p_df.iloc[t]['レース名2'])): #C1C2
                        kijun = 150
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])): #C2
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ３' in p_df.iloc[t]['レース名2'])): #C2C3
                        kijun = 130
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' not in p_df.iloc[t]['レース名2'])): #C3  
                        kijun = 120

                    elif p_df.iloc[t]['競馬場'] in hyogo and ('ＪＲＡ交流' in p_df.iloc[t]['レース名2']):  
                        kijun = 280    
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('重賞' in p_df.iloc[t]['レース名2']):  
                        kijun = 350
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 280
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ１'and 'Ａ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 260
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ１' and 'Ｂ１' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 240
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ２' and 'Ｂ１' in p_df.iloc[t]['レース名2']):  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])):
                        kijun = 200        
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ１' and 'Ｂ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 180
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ａ１' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])):
                        kijun = 160     
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ２' and 'Ｃ１' in p_df.iloc[t]['レース名2']):  
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ１' in p_df.iloc[t]['レース名2']) \
                        and ('Ｂ２' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 120
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ１' and 'Ｃ２' in p_df.iloc[t]['レース名2']):  
                        kijun = 110
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ２' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 100
                    elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ２' and 'Ｃ３' in p_df.iloc[t]['レース名2']):  
                        kijun = 90   
                    elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ３' in p_df.iloc[t]['レース名2']) \
                        and ('Ｃ２' not in p_df.iloc[t]['レース名2'])):  
                        kijun = 80

                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 280
                    elif p_df.iloc[t]['競馬場'] in tokai and 'ＳＰ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 240 
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ａ' in p_df.iloc[t]['レース名2']:  
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ｂ' in p_df.iloc[t]['レース名2']:
                        kijun = 130  
                    elif p_df.iloc[t]['競馬場'] in tokai and 'Ｃ' in p_df.iloc[t]['レース名2']:
                        kijun = 60                    

                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 330
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｈ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 270
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 210
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 190
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 160
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 150
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 130
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 100
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ２' in p_df.iloc[t]['レース名2']:  
                        kijun = 90
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ３' in p_df.iloc[t]['レース名2']:  
                        kijun = 80
                    elif p_df.iloc[t]['競馬場'] == '門別' and 'Ｂ' not in p_df.iloc[t]['レース名2'] \
                        and 'Ｃ４' in p_df.iloc[t]['レース名2']:  
                        kijun = 70

                    elif p_df.iloc[t]['競馬場'] in others and 'オープン' in p_df.iloc[t]['レース名2'] \
                        and 'Ｊｐｎ' not in p_df.iloc[t]['レース名2']:  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in others and 'Ａ' in p_df.iloc[t]['レース名2'] \
                        and 'Ｂ' not in p_df.iloc[t]['レース名2']:  
                        kijun = 200

                    else:
                        kijun = 60
                        
                    base_number.append(kijun)
                
                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]


    #着差は楽天競馬とnetkeibaで書き方が違う。地方版は楽天競馬に対応            
                chakusa = []
                for u in range(4):

                    if p_df.iloc[u]['着順2'] == 1:
                        if p_df.iloc[u]['差2'] > 0.7:
                            race_chakusa = 1.5
                        elif 0.5 < p_df.iloc[u]['差2'] <= 0.7:
                            race_chakusa = 1.3
                        elif 0.3 < p_df.iloc[u]['差2'] <= 0.5:
                            race_chakusa = 1.2    
                        else:
                            race_chakusa = 1.0
                    elif p_df.iloc[u]['着順2'] > 1:
                        if 0.0 <= p_df.iloc[u]['差2'] <= 0.5:
                            race_chakusa = 1.0
                        elif 0.5 < p_df.iloc[u]['差2'] <= 1.0:
                            race_chakusa = 0.8
                        elif 1.0 < p_df.iloc[u]['差2'] <= 2.0:
                            race_chakusa = 0.5
                        else:
                            race_chakusa = 0.2

                    chakusa.append(race_chakusa)

                a, b, c, d = chakusa[0], chakusa[1], chakusa[2], chakusa[3]

                
                
                #連勝係数       
                if p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1 and p_df.iloc[2]['着順2'] == 1 \
                        and p_df.iloc[3]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2'] -p_df.iloc[3]['差2']) / 4
                    if rensho < -0.7:
                        e = 1.35
                    elif -0.7 <= rensho < -0.5:
                        e = 1.30    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.25
                    else:
                        e = 1.20                
                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1 and p_df.iloc[2]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2'] +p_df.iloc[3]['差2']) / 4   
                    if rensho < -0.7:
                        e = 1.25
                    elif -0.7 <= rensho < -0.5:
                        e = 1.20    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.15
                    else:
                        e = 1.10
                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] +p_df.iloc[2]['差2'] +p_df.iloc[3]['差2']) / 4   
                    if rensho < -0.7:
                        e = 1.20
                    elif -0.7 <= rensho < -0.5:
                        e = 1.15    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.10
                    else:
                        e = 1.05
                else:
                    e = 1.0

                #斤量補正        
                #if '牝' in horse_id:
                    #f = kijun1 * 0.1 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                #else:
                    #f = kijun1 * 0.1 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))

                    
                #斤量補正        
                if 800 <= race_distance <= 1000:
                    if '牝' in horse_id:
                        f = kijun1 * 0.15 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.15 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif 1000 < race_distance <= 1400:
                    if '牝' in horse_id:
                        f = kijun1 * 0.1166 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.1166 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif 1400 < race_distance <= 1800:
                    if '牝' in horse_id:
                        f = kijun1 * 0.0833 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.0833 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                elif race_distance > 1800:
                    if '牝' in horse_id:
                        f = kijun1 * 0.05 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                    else:
                        f = kijun1 * 0.05 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))
                    
                    
                    
                    
                    
                    
                    
                #休養係数        
                if td(weeks = 0) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 12):
                    g = 1.0
                elif td(weeks = 12) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 24):
                    g = 0.95
                elif td(weeks = 24) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (racedate - p_df.iloc[0]['日付2']):
                    g = 0.8
                else:
                    g = 1.0

                #レース毎の牝馬補正    
                hinba = []
                for v in range(4):

                    if '牝' in p_df.iloc[v]['レース名2']:
                        female = 0.9
                    else:
                        female = 1.0
                    hinba.append(female)

                a1, b1, c1, d1 = hinba[0], hinba[1], hinba[2], hinba[3]
                
                
                #距離係数                
                av_dist = (p_df.iloc[0]['距離2'] + p_df.iloc[1]['距離2'] + p_df.iloc[2]['距離2'] + p_df.iloc[3]['距離2']) / 4 
                if 800 <= race_distance <= 1000:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1000 < race_distance <= 1400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 250 and abs(race_distance - av_dist) > 250:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 400 and av_dist < 1600:
                        h = 0.9
                    else:
                        h = 1.0

                #コース係数
                if race_course == 'ダ':
                    if p_df.iloc[0]['コース'] == '芝' and p_df.iloc[1]['コース'] == '芝' and p_df.iloc[2]['コース'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0           



                ts = ((kijun1 *1.3 *a *a1 + kijun2 *1.2 *b *b1 + kijun3 *1.1 *c *c1 + kijun4 *1.0 *d *d1 ) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts)

        return tekito_shisu



    kekka = shisu(processed_horse_results)
    hyo1 = pd.DataFrame({'馬番': umaban, '馬名': horse_name_list})
    hyo1['指数'] = kekka.values()
    hyo1['騎手'] = jockey_list
    hyo1['年齢'] = age_list
    hyo1['斤量'] = weight_list
    hyo1['斤量'] = hyo1['斤量'].astype(float)
    hyo1['オッズ'] = odds_list
    hyo1['前走'] = zenso_list
    
    
    past_weight_list = []
    for xxx, kr in horse_results.items():
        kkr = (kr['負担重量'][0])
        past_weight_list.append(kkr)
    s = pd.Series(past_weight_list)
    hyo1['斤量増減']= hyo1['斤量'] - s

#20220520時点のデータ 

#騎手補正：連帯率40以上:1.2, 35-40%:1.15, 30-35%:1.1, 25-30%:1.05, 20-25%:1.025     

    hyo1.loc[hyo1['騎手'] == '森泰斗', '指数'] = hyo1['指数'] * 1.15 
    hyo1.loc[hyo1['騎手'] == '御神訓', '指数'] = hyo1['指数'] * 1.15
    hyo1.loc[hyo1['騎手'] == '真島大', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '矢野貴', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '笹川翼', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '左海誠', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '本田重', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '山崎誠', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '吉原寛', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '和田譲', '指数'] = hyo1['指数'] * 1.025    
    hyo1.loc[hyo1['騎手'] == '町田直', '指数'] = hyo1['指数'] * 1.025   
    hyo1.loc[hyo1['騎手'] == '張田昂', '指数'] = hyo1['指数'] * 1.025        
    hyo1.loc[hyo1['騎手'] == '本橋孝', '指数'] = hyo1['指数'] * 1.025   
    hyo1.loc[hyo1['騎手'] == '澤田達', '指数'] = hyo1['指数'] * 1.05    
    hyo1.loc[hyo1['騎手'] == '野澤憲', '指数'] = hyo1['指数'] * 1.025     
    
    hyo1.loc[hyo1['騎手'] == '吉村智', '指数'] = hyo1['指数'] * 1.20
    hyo1.loc[hyo1['騎手'] == '下原理', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '田中学', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '笹田知', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '川原正', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '大山真', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '廣瀬航', '指数'] = hyo1['指数'] * 1.05    
    hyo1.loc[hyo1['騎手'] == '鴨宮祥', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '田野豊', '指数'] = hyo1['指数'] * 1.025
    
    hyo1.loc[hyo1['騎手'] == '赤岡修', '指数'] = hyo1['指数'] * 1.20
    hyo1.loc[hyo1['騎手'] == '永森大', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '西川敏', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '倉兼育', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '宮川実', '指数'] = hyo1['指数'] * 1.20
    hyo1.loc[hyo1['騎手'] == '岡村卓', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '郷間勇', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '多田誠', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '妹尾浩', '指数'] = hyo1['指数'] * 1.025    
    hyo1.loc[hyo1['騎手'] == '塚本雄', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '佐原秀', '指数'] = hyo1['指数'] * 1.025
    
    hyo1.loc[hyo1['騎手'] == '山口勲', '指数'] = hyo1['指数'] * 1.15
    hyo1.loc[hyo1['騎手'] == '飛田愛', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '真島正', '指数'] = hyo1['指数'] * 1.20    
    hyo1.loc[hyo1['騎手'] == '石川慎', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '倉富隆', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '鮫島克', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '竹吉徹', '指数'] = hyo1['指数'] * 1.05    
    hyo1.loc[hyo1['騎手'] == '山下裕', '指数'] = hyo1['指数'] * 1.025
    
    hyo1.loc[hyo1['騎手'] == '岡部誠', '指数'] = hyo1['指数'] * 1.20
    hyo1.loc[hyo1['騎手'] == '今井貴', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '大畑雅', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '加藤聡', '指数'] = hyo1['指数'] * 1.05     
    hyo1.loc[hyo1['騎手'] == '丸野勝', '指数'] = hyo1['指数'] * 1.05 
    hyo1.loc[hyo1['騎手'] == '丹羽克', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '村上弘', '指数'] = hyo1['指数'] * 1.025    
    hyo1.loc[hyo1['騎手'] == '宮下瞳', '指数'] = hyo1['指数'] * 1.025    
    
    hyo1.loc[hyo1['騎手'] == '吉原寛', '指数'] = hyo1['指数'] * 1.20

    hyo1.loc[hyo1['騎手'] == '桑村真', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '五十冬', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '服部茂', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '阿部龍', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '石川倭', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '岩橋勇', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '宮崎光', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '落合玄', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '阪野学', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '小野楓', '指数'] = hyo1['指数'] * 1.025    
        
    hyo1.loc[hyo1['騎手'] == '山本聡', '指数'] = hyo1['指数'] * 1.20     
    hyo1.loc[hyo1['騎手'] == '村上忍', '指数'] = hyo1['指数'] * 1.10     
    hyo1.loc[hyo1['騎手'] == '山本政', '指数'] = hyo1['指数'] * 1.10 
    hyo1.loc[hyo1['騎手'] == '高松亮', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '木村暁', '指数'] = hyo1['指数'] * 1.05    
    hyo1.loc[hyo1['騎手'] == '高橋悠', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '坂口裕', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '陶文峰', '指数'] = hyo1['指数'] * 1.025
    
    hyo1.loc[hyo1['騎手'] == '武　豊', '指数'] = hyo1['指数'] * 1.05    
    hyo1.loc[hyo1['騎手'] == '川田将', '指数'] = hyo1['指数'] * 1.20
    hyo1.loc[hyo1['騎手'] == '福永祐', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '松山弘', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == 'Ｍデム', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '戸崎圭', '指数'] = hyo1['指数'] * 1.00

    hyo1.loc[hyo1['騎手'] == 'レーン', '指数'] = hyo1['指数'] * 1.075
    hyo1.loc[hyo1['騎手'] == 'ルメー', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '川田将', '指数'] = hyo1['指数'] * 1.125
    hyo1.loc[hyo1['騎手'] == '横山武', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == 'Ｍデム', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '福永祐', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '戸崎圭', '指数'] = hyo1['指数'] * 1.025
    hyo1.loc[hyo1['騎手'] == '武　豊', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '横山典', '指数'] = hyo1['指数'] * 1.025    
    hyo1.loc[hyo1['騎手'] == '岩田望', '指数'] = hyo1['指数'] * 1.00 
    hyo1.loc[hyo1['騎手'] == '岩田康', '指数'] = hyo1['指数'] * 0.975
    hyo1.loc[hyo1['騎手'] == '藤岡佑', '指数'] = hyo1['指数'] * 0.975   
    hyo1.loc[hyo1['騎手'] == '松山弘', '指数'] = hyo1['指数'] * 1.00

    hyo1.loc[hyo1['騎手'] == '吉田隼', '指数'] = hyo1['指数'] * 1.00    
    hyo1.loc[hyo1['騎手'] == '坂井瑠', '指数'] = hyo1['指数'] * 1.00    
    hyo1.loc[hyo1['騎手'] == '藤岡康', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '三浦皇', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '菅原明', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '横山和', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '池添謙', '指数'] = hyo1['指数'] * 0.975
    hyo1.loc[hyo1['騎手'] == '西村淳', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '北村友', '指数'] = hyo1['指数'] * 1.00            
    hyo1.loc[hyo1['騎手'] == '田辺裕', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '鮫島克', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '菱田裕', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '石橋脩', '指数'] = hyo1['指数'] * 0.975
    hyo1.loc[hyo1['騎手'] == '内田博', '指数'] = hyo1['指数'] * 0.95    
    hyo1.loc[hyo1['騎手'] == '幸英明', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '濱中俊', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '荻野極', '指数'] = hyo1['指数'] * 0.95
    hyo1.loc[hyo1['騎手'] == '丹内祐', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '石川裕', '指数'] = hyo1['指数'] * 0.975
    hyo1.loc[hyo1['騎手'] == '和田竜', '指数'] = hyo1['指数'] * 0.975    
    hyo1.loc[hyo1['騎手'] == '北村宏', '指数'] = hyo1['指数'] * 0.975

    
    #前走からの斤量増減補正

    hyo1.loc[hyo1['斤量増減'] == -6.0, '指数'] = hyo1['指数'] * 1.20    
    hyo1.loc[hyo1['斤量増減'] == -5.5, '指数'] = hyo1['指数'] * 1.18    
    hyo1.loc[hyo1['斤量増減'] == -5.0, '指数'] = hyo1['指数'] * 1.16
    hyo1.loc[hyo1['斤量増減'] == -4.5, '指数'] = hyo1['指数'] * 1.14    
    hyo1.loc[hyo1['斤量増減'] == -4.0, '指数'] = hyo1['指数'] * 1.12
    hyo1.loc[hyo1['斤量増減'] == -3.5, '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['斤量増減'] == -3.0, '指数'] = hyo1['指数'] * 1.08 
    hyo1.loc[hyo1['斤量増減'] == -2.5, '指数'] = hyo1['指数'] * 1.06 
    hyo1.loc[hyo1['斤量増減'] == -2.0, '指数'] = hyo1['指数'] * 1.04 
    hyo1.loc[hyo1['斤量増減'] == -1.5, '指数'] = hyo1['指数'] * 1.02
    hyo1.loc[hyo1['斤量増減'] == -1.0, '指数'] = hyo1['指数'] * 1.0
    hyo1.loc[hyo1['斤量増減'] == -0.5, '指数'] = hyo1['指数'] * 1.0
    hyo1.loc[hyo1['斤量増減'] == 0.0, '指数'] = hyo1['指数'] * 1.0
    hyo1.loc[hyo1['斤量増減'] == 0.5, '指数'] = hyo1['指数'] * 1.0
    hyo1.loc[hyo1['斤量増減'] == 1.0, '指数'] = hyo1['指数'] * 1.0
    hyo1.loc[hyo1['斤量増減'] == 1.5, '指数'] = hyo1['指数'] * 0.98
    hyo1.loc[hyo1['斤量増減'] == 2.0, '指数'] = hyo1['指数'] * 0.96
    hyo1.loc[hyo1['斤量増減'] == 2.5, '指数'] = hyo1['指数'] * 0.94
    hyo1.loc[hyo1['斤量増減'] == 3.0, '指数'] = hyo1['指数'] * 0.92
    hyo1.loc[hyo1['斤量増減'] == 3.5, '指数'] = hyo1['指数'] * 0.90
    hyo1.loc[hyo1['斤量増減'] == 4.0, '指数'] = hyo1['指数'] * 0.88
    hyo1.loc[hyo1['斤量増減'] == 4.5, '指数'] = hyo1['指数'] * 0.86
    hyo1.loc[hyo1['斤量増減'] == 5.0, '指数'] = hyo1['指数'] * 0.84
    hyo1.loc[hyo1['斤量増減'] == 5.5, '指数'] = hyo1['指数'] * 0.82
    hyo1.loc[hyo1['斤量増減'] == 6.0, '指数'] = hyo1['指数'] * 0.80 
    
    
    hyo1['指数']= hyo1['指数'].astype(int)

#偏差値計算    
    final_shisu = hyo1['指数'].to_list()
    ave = np.average(final_shisu)
    std = np.std(final_shisu)

    deviation = []
    for i in final_shisu:
      deviation_value = '{:.1f}'.format(float((i - ave) / std * 10 + 50), 1)
      deviation.append(deviation_value)

    hyo1['偏差値'] = deviation
    
    
    hyo1['年齢'] = hyo1['年齢'].astype(int)
    hyo1['順位'] = hyo1['指数'].rank(ascending=False).astype(int)
    hyo2 = hyo1[['順位', '馬番', '馬名', '前走', '指数', '偏差値', '騎手', '年齢', 'オッズ']]
    hyo3 = hyo2.sort_values('順位')
    hyo3.set_index("順位", inplace=True)
    
    st.write('【' + racenumber + '】' +  racename)
    st.dataframe(hyo3)
    
else:
    st.write('・・・・・・・・')
    
