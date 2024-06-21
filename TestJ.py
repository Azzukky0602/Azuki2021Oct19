#!/usr/bin/env python
# coding: utf-8

# In[1]:



import streamlit as st
import requests   #3歳補正導入済み
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
import lxml.html
from datetime import datetime as dt
from datetime import timedelta as td
from pytz import timezone
import copy
import numpy as np
import html5lib

# タイムゾーンを指定して、日時を作成.
utc_time = dt.now(timezone('Asia/Tokyo'))
kotoshi = utc_time.year

jra = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
nankan = ['浦和', '船橋', '大井', '川崎']
hyogo = ['園田', '姫路']
others = ['門別', '盛岡', '水沢', '金沢', '名古屋', '高知', '佐賀']

age3_GI = ['皐月賞(GI)', '東京優駿(GI)', '菊花賞(GI)', '桜花賞(GI)', '優駿牝馬(GI)',
           '秋華賞(GI)', 'NHKマイルC(GI)', 'ジャパンダートダービ(GI)']
age3_GII = ['神戸新聞杯(GII)', '関西TVローズS(GII)', 'チューリップ賞(GII)', 'テレビ東京杯青葉賞(GII)', '朝日セントライト記念(GII)',
            'サンスポ賞フローラS(GII)', '京都新聞杯(GII)', 'ニュージーランドT(GII)', 'フジTVスプリングS(GII)', '報知弥生ディープ記念(GII)',
            'フィリーズレビュー(GII)']
age3_GIII = ['フェアリーS(GIII)', '共同通信杯(GIII)', 'ラジオNIKKEI賞(GIII)', '日刊スポシンザン記念(GIII)', '毎日杯(GIII)',
             'デイリー杯クイーンC(GIII)', 'アーリントンC(GIII)', '中スポ賞ファルコンS(GIII)', 'きさらぎ賞(GIII)',
            '共同通信杯(GIII)', '京成杯(GIII)', 'ユニコーンS(GIII)', 'フラワーC(GIII)', '紫苑S(GIII)', 'レパードS(GIII)']
age3_L = ['若葉S(L)', '若駒S(L)', 'クロッカスS(L)', 'ジュニアC(L)', '葵S(G)', 'プリンシパルS(L)', '鳳雛S(L)', 'ヒヤシンスS(L)',
         '紅梅S(L)', 'エルフィンS(L)', 'アネモネS(L)', 'スイートピーS(L)', '忘れな草賞(L)']
age3_OP = ['すみれS(OP)', '青竜S(OP)', '端午S(OP)', '青竜S(OP)', '伏竜S(OP)']


st.title('テキトー指数研究所＠WEB')
st.header('JRA版')
st.subheader('新パラメータ版')

st.write('   ')
st.info('【南関東版】\https://azzukky-n24.streamlit.app/')
st.info('【地方交流版】\https://azzukky-k24.streamlit.app/')
st.write('   ')
st.write('   ')
st.write('クラスが上がるほど、良く当たる傾向があります。')
st.write('３歳戦はあまりあてになりません。')
st.write('過去３走していない馬の指数はゼロになります。')
st.write('   ')
st.write('   ')

basho = st.radio('開催場所？', ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉'])

if basho == '札幌':
    place = "1"
elif basho == '函館':
    place = "2"
elif basho == '福島':
    place = "3"
elif basho == '新潟':
    place = "4"
elif basho == '東京':
    place = "5"
elif basho == '中山':
    place = "6"
elif basho == '中京':
    place = "7"
elif basho == '京都':
    place = "8"
elif basho == '阪神':
    place = "9"
elif basho == '小倉':
    place = "10"
else:
    place = "0"
    
kai = st.number_input('【半角数字】第何回開催？', 1, 6, 1)
day = st.number_input('【半角数字】何日目？', 1, 12, 6)
race = st.number_input('【半角数字】レース番号？', 1, 12, 11)

race_for_keisan = str(place.zfill(2)) + str(str(kai).zfill(2)) + str(str(day).zfill(2)) + str(str(race).zfill(2))


st.write('   ')
st.subheader('計算するときはチェックボックスをチェック！')
st.subheader('次のレースを計算する前にチェックを外す！')

push = st.checkbox('チェック！！')
if push == True:
   
    st.write('計算には約1分かかります。しばらくお待ちください。')
    
    url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + str(kotoshi) + race_for_keisan + '&rf=race_submenu'

    hyo = pd.read_html(url, encoding='euc-jp')[0]
    hyo.columns = hyo.columns.droplevel(0)
    hyo.columns = ['waku', 'umaban', 'noneed1', 'name', 'seirei', 'weight', 'jockey', 'stable', 'bodyweight', 'noneed1', 'odds', 'noneed2', 'noneed3']
    hyo.drop(columns=['waku', 'noneed1', 'noneed2', 'noneed3', 'bodyweight', 'odds'], inplace=True)

    hyo2 = copy.deepcopy(hyo)
    hyo2['gender'] = hyo2['seirei'].str[0]
    hyo2['age'] = hyo2['seirei'].str[1:].astype(int)

    html = requests.get(url)
    html.encoding = 'EUC-JP'
    soup = BeautifulSoup(html.text, "html.parser")

    syusso = soup.find('table').find_all('a', attrs = {'href': re.compile('^https://db.netkeiba.com/horse/')})
    syusso2 = soup.select('td:nth-of-type(6)')
    seirei = soup.select('td.Barei')

    day_css = soup.select('#RaceList_DateList > dd.Active > a')[0]
    rd = re.findall((r'\d+'), day_css['href'])[0]
    race_date = pd.Timestamp(rd)
    race_name = soup.find('title').text
    race_course = soup.find_all(class_='RaceData01')[0].text.strip()[10]  #20201219 netkeibaのWEB変更を受けて修正
    race_distance = int(soup.find_all(class_='RaceData01')[0].text.strip()[11:15]) #20201219 netkeibaのWEB変更を受けて修正

    L1 = []
    for uma in syusso:
        id_number = re.findall(r'\d+', uma['href'])[0]
        L1.append(id_number)

    L2 = []
    for weight in hyo2['weight']:
        L2.append(str(weight))

    L3 = []
    for sei in hyo2['gender']:
        L3.append(sei)

    L4 = []
    for rei in hyo2['age']:
        L4.append(str(rei))

    syusso_list = [x1 + ' ' + x2 +  ' ' + x3 + ' ' + x4  for (x1, x2, x3, x4) in zip(L1, L2, L3, L4)]


    tekito_shisu_list = []
    for horse in  syusso_list:
        time.sleep(1)
        url2 = 'https://db.netkeiba.com/horse/result/' + horse[:10]
        past_results = pd.read_html(url2, header = 0, encoding='EUC-JP')[0].head(10)
        past_results.columns = ['col1', 'col2','col3','col4','col5','col6','col7','col8','col9','col10','col11','col12','col13','col14',\
                           'col15','col16','col17','col18','col19','col20','col21','col22','col23','col24','col25','col26','col27','col28']

        past_results['date'] = [dt.strptime(i, "%Y/%m/%d") for i in past_results['col1']]
        past_results['result'] = past_results['col12'].astype(str)
        past_results['course'] = past_results['col15'].str[0]
        past_results['distance'] = past_results['col15'].str[1:].astype(int)
        past_results['place'] = past_results['col2'].str.extract('(\D+)')
        past_results['pastweight'] = past_results['col14']
        past_results['difference'] = past_results['col19']
        past_results['racename'] = past_results['col5']
        npr = past_results.loc[:, ['date', 'place', 'racename', 'course', 'distance', 'result', 'difference']].dropna()
        npr = npr[(npr['difference'] < 3.5)] 
        npr = npr[~npr['result'].str.contains('降')]

        if npr['result'].dtype != 'int':
            npr['result'] = pd.to_numeric(npr['result'])
            npr['result'] = npr['result'].astype(int)
        else:
            pass

        npr = npr.reset_index()



        if len(npr) < 3:
            tekito_shisu = 0
            tekito_shisu_list.append(tekito_shisu)

        #3歳、3戦のみ、皐月賞前
        elif len(npr) == 3:
            if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 4, 30):

                base_number = []
                for t in range(3):

                    if 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):  
                        kijun = 430
                    elif 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):  
                        kijun = 300        
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 480
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 315 
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 550
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 350    
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝' in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300           
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

        #3歳、3戦のみ、皐月賞後
            elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 5, 1):

                base_number = []
                for t in range(3):

                    if npr.iloc[t]['racename'] in age3_GIII:
                        kijun = 530
                    elif 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['racename'] in age3_GII:
                        kijun = 580
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 315                                              
                    elif npr.iloc[t]['racename'] in age3_GI:  
                        kijun = 650
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):  
                        kijun = 350                                                    
                    elif npr.iloc[t]['racename'] in age3_L:
                        kijun = 500   
                    elif npr.iloc[t]['racename'] in age3_OP:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GIII: 
                        kijun = 650
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GII:
                        kijun = 700
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GI:
                        kijun = 800
                    elif 'L' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_L:
                        kijun = 600
                    elif 'OP' in npr.iloc[t]['racename']and npr.iloc[t]['racename'] not in age3_OP:
                        kijun = 600                                                                             
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝' in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300          
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]                

            else:        

                base_number = []
                for t in range(3):                

                    if npr.iloc[t]['place'] in jra and 'GIII' in npr.iloc[t]['racename']:  
                        kijun = 650
                    elif npr.iloc[t]['place'] in jra and 'GII' in npr.iloc[t]['racename']:
                        kijun = 700
                    elif npr.iloc[t]['place'] in jra and 'GI' in npr.iloc[t]['racename']:
                        kijun = 800
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename']:
                        kijun = 600
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename']:
                        kijun = 600
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '1600' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝'in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1000' in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300  
                    elif npr.iloc[t]['place'] in jra and '500' in npr.iloc[t]['racename']:
                        kijun = 300           
                    elif npr.iloc[t]['place'] not in jra and 'GIII' in npr.iloc[t]['racename']:  
                        kijun = 500
                    elif npr.iloc[t]['place'] not in jra  and 'GII' in npr.iloc[t]['racename']:  
                        kijun = 600
                    elif npr.iloc[t]['place'] not in jra  and 'GI' in npr.iloc[t]['racename']:  
                        kijun = 700
                    else:
                        kijun = 200
                    base_number.append(kijun)                   

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

            #着差係数
            chakusa = []
            for u in range(3):

                if npr.iloc[u]['difference'] < -0.7:
                    race_chakusa = 1.5
                elif -0.7 <= npr.iloc[u]['difference'] < -0.5:
                    race_chakusa = 1.3    
                elif -0.5 <= npr.iloc[u]['difference'] < -0.3:
                    race_chakusa = 1.2
                elif -0.3 <= npr.iloc[u]['difference'] <= 0.5:
                    race_chakusa = 1.0
                elif 0.5 < npr.iloc[u]['difference'] <= 1.0:
                    race_chakusa = 0.8
                elif 1.0 < npr.iloc[u]['difference'] <= 2.0:
                    race_chakusa = 0.5
                else:
                    race_chakusa = 0.2
                chakusa.append(race_chakusa)

            a, b, c = chakusa[0], chakusa[1], chakusa[2]

            #連勝係数    
            if npr.iloc[0]['result'] == "1" and npr.iloc[1]['result'] == "1" and npr.iloc[2]['result'] == "1":
                rensho = (npr.iloc[0]['difference'] + npr.iloc[1]['difference'] + npr.iloc[2]['difference']) / 3
                if rensho < -0.7:
                    e = 1.25
                elif -0.7 <= rensho < -0.5:
                    e = 1.20    
                elif -0.5 <= rensho < -0.3:
                    e = 1.15
                else:
                    e = 1.10
            elif npr.iloc[0]['result'] == "1" and npr.iloc[1]['result'] == "1": #and npr.iloc[2]['result'] != "1":
                rensho = (npr.iloc[0]['difference'] + npr.iloc[1]['difference'] + npr.iloc[2]['difference']) / 3
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
            if 1000 <= race_distance <= 1400:
                if all(L3) =='牝':
                    f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.1166 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.1166 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.1166 * (max(hyo2['weight']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.0833 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.0833 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.0833 * (max(hyo2['weight']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15])) 



            #休養係数
            if td(weeks = 0) < (race_date - npr.iloc[0]['date']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (race_date - npr.iloc[0]['date']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (race_date - npr.iloc[0]['date']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (race_date - npr.iloc[0]['date']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (race_date - npr.iloc[0]['date']):
                g = 0.8
            else:
                g = 1.0                


            #距離係数                
            av_dist = (npr.iloc[0]['distance'] + npr.iloc[1]['distance'] + npr.iloc[2]['distance']) / 3 
            if 1000 <= race_distance <= 1400:
                if abs(race_distance - npr.iloc[0]['distance']) > 200 and abs(race_distance - av_dist) > 200:
                    h = 0.9
                else:
                    h = 1.0
            elif 1400 < race_distance <= 1800:
                if abs(race_distance - npr.iloc[0]['distance']) > 300 and abs(race_distance - av_dist) > 300:
                    h = 0.9
                else:
                    h = 1.0
            elif 1800 < race_distance <= 2400:
                if abs(race_distance - npr.iloc[0]['distance']) > 400 and abs(race_distance - av_dist) > 400:
                    h = 0.9
                else:
                    h = 1.0
            elif 2400 < race_distance:
                if abs(race_distance - npr.iloc[0]['distance']) > 500 and av_dist < 2000:
                    h = 0.9
                else:
                    h = 1.0

            #コース係数
            if race_course == 'ダ':
                if npr.iloc[0]['course'] == '芝' and npr.iloc[1]['course'] == '芝' and npr.iloc[2]['course'] == '芝':
                    i = 0.7
                else:
                    i = 1.0
            elif race_course == '芝':
                if npr.iloc[0]['course'] == 'ダ' and npr.iloc[1]['course'] == 'ダ' and npr.iloc[2]['course'] == 'ダ':
                    i = 0.7
                else:
                    i = 1.0



            ts = ((kijun1 * 2.4 * a + kijun2 * b * 1.1 + kijun3 * c * 1.0) + f) * e * g * h * i
            tekito_shisu = int(ts)
            tekito_shisu_list.append(tekito_shisu)


        #3歳、4戦以上、皐月賞前
        else:
            if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 4, 30):

                base_number = []
                for t in range(4):

                    if 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):  
                        kijun = 430
                    elif 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):  
                        kijun = 300        
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 480
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 315 
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 550
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 350    
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝' in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300           
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]    

            #3歳、4戦以上、皐月賞後
            elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 5, 1):

                base_number = []
                for t in range(4):

                    if 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):  
                        kijun = 300                                                    
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 315
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 350
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename'] \
                        and npr.iloc[t]['date'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['racename'] in age3_GIII:
                        kijun = 530
                    elif npr.iloc[t]['racename'] in age3_GII:
                        kijun = 580
                    elif npr.iloc[t]['racename'] in age3_GI:
                        if int(npr.iloc[t]['result']) <= 5:  
                            kijun = 800
                        elif float(npr.iloc[t]['difference']) <= 0.5:  
                            kijun = 800
                        else:
                            kijun = 650
                    elif npr.iloc[t]['racename'] in age3_L:
                        kijun = 500   
                    elif npr.iloc[t]['racename'] in age3_OP:
                        kijun = 500
                    elif 'GIII' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GIII: 
                        kijun = 650
                    elif 'GII' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GII:
                        kijun = 700
                    elif 'GI' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_GI:
                        kijun = 800
                    elif 'L' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_L:
                        kijun = 600
                    elif 'OP' in npr.iloc[t]['racename'] and npr.iloc[t]['racename'] not in age3_OP:
                        kijun = 600                                                                             
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝' in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300          
                    else:
                        kijun = 200

                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 


            #古馬混合戦の指数
            else:
                base_number = []
                for t in range(4):

                    if npr.iloc[t]['course'] == '障' and 'J.GIII' in npr.iloc[t]['racename']:  
                        kijun = 600      
                    elif npr.iloc[t]['course'] == '障' and 'J.GII' in npr.iloc[t]['racename']:  
                        kijun = 700
                    elif npr.iloc[t]['course'] == '障' and 'J.GI' in npr.iloc[t]['racename']:  
                        kijun = 800          
                    elif npr.iloc[t]['course'] == '障' and 'OP' in npr.iloc[t]['racename']:  
                        kijun = 500           
                    elif npr.iloc[t]['course'] == '障' and '未勝利' in npr.iloc[t]['racename']:  
                        kijun = 400           
                    elif npr.iloc[t]['place'] in jra and 'GIII' in npr.iloc[t]['racename']:  
                        kijun = 650
                    elif npr.iloc[t]['place'] in jra and 'GII' in npr.iloc[t]['racename']:
                        kijun = 700
                    elif npr.iloc[t]['place'] in jra and 'GI' in npr.iloc[t]['racename']:
                        kijun = 800
                    elif npr.iloc[t]['place'] in jra and 'L' in npr.iloc[t]['racename']:
                        kijun = 600
                    elif npr.iloc[t]['place'] in jra and 'OP' in npr.iloc[t]['racename']:
                        kijun = 600
                    elif npr.iloc[t]['place'] in jra and '3勝' in npr.iloc[t]['racename']:
                        kijun = 500
                    elif npr.iloc[t]['place'] in jra and '2勝'in npr.iloc[t]['racename']:
                        kijun = 400
                    elif npr.iloc[t]['place'] in jra and '1勝' in npr.iloc[t]['racename']:
                        kijun = 300 
                    elif npr.iloc[t]['place'] not in jra and 'GIII' in npr.iloc[t]['racename']:  
                        kijun = 500
                    elif npr.iloc[t]['place'] not in jra  and 'GII' in npr.iloc[t]['racename']:  
                        kijun = 600
                    elif npr.iloc[t]['place'] not in jra  and 'GI' in npr.iloc[t]['racename']:  
                        kijun = 700
                    else:
                        kijun = 200

                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 

            #着差係数

            chakusa = []
            for u in range(4):

                if npr.iloc[u]['difference'] < -0.7:
                    race_chakusa = 1.5
                elif -0.7 <= npr.iloc[u]['difference'] < -0.5:
                    race_chakusa = 1.3    
                elif -0.5 <= npr.iloc[u]['difference'] < -0.3:
                    race_chakusa = 1.2
                elif -0.3 <= npr.iloc[u]['difference'] <= 0.5:
                    race_chakusa = 1.0
                elif 0.5 < npr.iloc[u]['difference'] <= 1.0:
                    race_chakusa = 0.8
                elif 1.0 < npr.iloc[u]['difference'] <= 2.0:
                    race_chakusa = 0.5
                else:
                    race_chakusa = 0.2
                chakusa.append(race_chakusa)

            a, b, c, d = chakusa[0], chakusa[1], chakusa[2], chakusa[3]                    

            #連勝係数    
            if npr.iloc[0]['result'] == "1" and npr.iloc[1]['result'] == "1" and npr.iloc[2]['result'] == "1" and npr.iloc[3]['result'] == "1":
                rensho = (npr.iloc[0]['difference'] + npr.iloc[1]['difference'] + npr.iloc[2]['difference'] + npr.iloc[3]['difference']) / 4
                if rensho < -0.7:
                    e = 1.35
                elif -0.7 <= rensho < -0.5:
                    e = 1.30    
                elif -0.5 <= rensho < -0.3:
                    e = 1.25
                else:
                    e = 1.20
            elif npr.iloc[0]['result'] == "1" and npr.iloc[1]['result'] == "1" and npr.iloc[2]['result'] == "1": #and npr.iloc[3]['result'] != 1:
                rensho = (npr.iloc[0]['difference'] + npr.iloc[1]['difference'] + npr.iloc[2]['difference'] + npr.iloc[3]['difference']) / 4
                if rensho < -0.7:
                    e = 1.25
                elif -0.7 <= rensho < -0.5:
                    e = 1.20   
                elif -0.5 <= rensho < -0.3:
                    e = 1.15
                else:
                    e = 1.10
            elif npr.iloc[0]['result'] == "1" and npr.iloc[1]['result'] == "1": #and npr.iloc[2]['result'] != 1 and npr.iloc[3]['result'] != 1:
                rensho = (npr.iloc[0]['difference'] + npr.iloc[1]['difference'] + npr.iloc[2]['difference'] + npr.iloc[3]['difference']) / 4
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
            if 1000 <= race_distance <= 1400:
                if all(L3) =='牝':
                    f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.1166 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.1166 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.1166 * (max(hyo2['weight']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.0833 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.0833 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.0833 * (max(hyo2['weight']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))                              


            #休養係数
            if td(weeks = 0) < (race_date - npr.iloc[0]['date']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (race_date - npr.iloc[0]['date']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (race_date - npr.iloc[0]['date']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (race_date - npr.iloc[0]['date']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (race_date - npr.iloc[0]['date']):
                g = 0.8
            else:
                g = 1.0

            #距離係数                
            av_dist = (npr.iloc[0]['distance'] + npr.iloc[1]['distance'] + npr.iloc[2]['distance'] + npr.iloc[3]['distance']) / 4 
            if 1000 <= race_distance <= 1400:
                if abs(race_distance - npr.iloc[0]['distance']) > 200 and abs(race_distance - av_dist) > 200:
                    h = 0.9
                else:
                    h = 1.0
            elif 1400 < race_distance <= 1800:
                if abs(race_distance - npr.iloc[0]['distance']) > 300 and abs(race_distance - av_dist) > 300:
                    h = 0.9
                else:
                    h = 1.0
            elif 1800 < race_distance <= 2400:
                if abs(race_distance - npr.iloc[0]['distance']) > 400 and abs(race_distance - av_dist) > 400:
                    h = 0.9
                else:
                    h = 1.0
            elif 2400 < race_distance:
                if abs(race_distance - npr.iloc[0]['distance']) > 500 and av_dist < 2000:
                    h = 0.9
                else:
                    h = 1.0

            #コース係数
            if race_course == 'ダ':
                if npr.iloc[0]['course'] == '芝' and npr.iloc[1]['course'] == '芝' and npr.iloc[2]['course'] == '芝':
                    i = 0.7
                else:
                    i = 1.0
            elif race_course == '芝':
                if npr.iloc[0]['course'] == 'ダ' and npr.iloc[1]['course'] == 'ダ' and npr.iloc[2]['course'] == 'ダ':
                    i = 0.7
                else:
                    i = 1.0
            else:
                i = 1.0



            ts = ((kijun1 * a * 1.3 + kijun2 * b * 1.2 + kijun3 * c *1.1+ kijun4 * d *1.0) + f) * e * g * h * i
            tekito_shisu = int(ts)
            tekito_shisu_list.append(tekito_shisu)

    hyo2['TS'] = tekito_shisu_list

    
    past_weight_list = []
    for horse in  syusso_list:
        time.sleep(1)
        url3 = 'https://db.netkeiba.com/horse/result/' + horse[:10]
        pr_for_w = pd.read_html(url3, header = 0, encoding='EUC-JP')[0].head(3)
        pr_for_w.columns = ['prfw1', 'prfw2','prfw3','prfw4','prfw5','prfw6','prfw7','prfw8','prfw9','prfw10','prfw11','prfw12','prfw13','prfw14',\
                           'prfw15','prfw16','prfw17','prfw18','prfw19','prfw20','prfw21','prfw22','prfw23','prfw24','prfw25','prfw26','prfw27','prfw28']
        pw = pr_for_w['prfw14'][0]
        past_weight_list.append(pw)


    s = pd.Series(past_weight_list)
    hyo2['weightgap']= hyo2['weight']-s

    starion_list = []
    owner_list = []
    for uma_b in L1:
        time.sleep(1)
        url_b = 'https://db.netkeiba.com/horse/' + uma_b
        uma_data = pd.read_html(url_b, encoding='euc-jp')[1]
        starion = uma_data[uma_data[0].str.contains('生産者')].iat[0,1][:4]
        owner = uma_data[uma_data[0].str.contains('馬主')].iat[0,1][:4]
        starion_list.append(starion)
        owner_list.append(owner)

    hyo2['starion'] = starion_list
    hyo2['owner'] = owner_list

    #騎手補正：三着内率＝X、50≦X＜60は1.30, 40≦X＜50は1.20, 30≦X＜40は1.10, 20≦X＜30は1.00, 10≦X＜20は0.90, 0≦X＜10は0.80

    #三着内率50%以上
    hyo2.loc[hyo2['jockey'] == 'マーフィ', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == 'レーン', 'TS'] = hyo2['TS'] * 1.30
    hyo2.loc[hyo2['jockey'] == 'ルメール', 'TS'] = hyo2['TS'] * 1.30
    hyo2.loc[hyo2['jockey'] == 'モレイラ', 'TS'] = hyo2['TS'] * 1.30    
    hyo2.loc[hyo2['jockey'] == '川田', 'TS'] = hyo2['TS'] * 1.30
    hyo2.loc[hyo2['jockey'] == 'Ｃデムーロ', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == '伴', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '平沢', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == 'ムーア', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == 'マーカンド', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == 'Ｈドイル', 'TS'] = hyo2['TS'] * 1.00
    
    #三着内率40-50%
    hyo2.loc[hyo2['jockey'] == '高田', 'TS'] = hyo2['TS'] * 1.10 
    hyo2.loc[hyo2['jockey'] == '横山武', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == 'Ｍデムーロ', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '福永', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == '石神', 'TS'] = hyo2['TS'] * 1.20    
    hyo2.loc[hyo2['jockey'] == '北沢', 'TS'] = hyo2['TS'] * 1.10

    #三着内率30-40%
    hyo2.loc[hyo2['jockey'] == '西谷誠', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '小野寺', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '戸崎圭', 'TS'] = hyo2['TS'] * 1.20
    hyo2.loc[hyo2['jockey'] == '武豊', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '横山典', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '岩田望', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '熊沢', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '森一', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '岩田康', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '藤岡佑', 'TS'] = hyo2['TS'] * 1.10   

    #三着内率20-30%
    hyo2.loc[hyo2['jockey'] == '松山', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '五十嵐', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '吉田隼', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '坂井', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '藤岡康', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '三浦', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '菅原明', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '横山和', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '池添', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '西村淳', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '北村友', 'TS'] = hyo2['TS'] * 1.00            
    hyo2.loc[hyo2['jockey'] == '田辺', 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['jockey'] == '鮫島克', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '菱田', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '石橋脩', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '内田博', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '幸', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '浜中', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '荻野極', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '丹内', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '石川', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '和田竜', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '岡田', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '難波', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '松本', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '団野', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '北村宏', 'TS'] = hyo2['TS'] * 0.90


    hyo2.loc[hyo2['jockey'] == '古川奈', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '古川吉', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '今村', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '松若', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '角田和', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '富田', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '秋山真', 'TS'] = hyo2['TS'] * 0.90  
    hyo2.loc[hyo2['jockey'] == '秋山稔', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '白浜', 'TS'] = hyo2['TS'] * 1.00    
    hyo2.loc[hyo2['jockey'] == '川須', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '水口', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '高倉', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '植野', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '宮崎', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '大野', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '勝浦', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '田中勝', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '横山琉', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '黒岩', 'TS'] = hyo2['TS'] * 1.00 
    hyo2.loc[hyo2['jockey'] == '上野', 'TS'] = hyo2['TS'] * 0.90     
    hyo2.loc[hyo2['jockey'] == '松田', 'TS'] = hyo2['TS'] * 0.90     
    hyo2.loc[hyo2['jockey'] == '永野', 'TS'] = hyo2['TS'] * 0.90     
    hyo2.loc[hyo2['jockey'] == '斎藤', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '丸山', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '角田河', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '武藤', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '伊藤', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '柴田大', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '泉谷', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '太宰', 'TS'] = hyo2['TS'] * 0.90  
    hyo2.loc[hyo2['jockey'] == '国分恭', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '松岡', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '吉田豊', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '津村', 'TS'] = hyo2['TS'] * 1.00
    hyo2.loc[hyo2['jockey'] == '小牧加', 'TS'] = hyo2['TS'] * 1.10    
    hyo2.loc[hyo2['jockey'] == '小崎', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '永島', 'TS'] = hyo2['TS'] * 0.90  
    hyo2.loc[hyo2['jockey'] == '草野', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '原', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '川又', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '小坂', 'TS'] = hyo2['TS'] * 1.00      
    hyo2.loc[hyo2['jockey'] == '小沢', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '野中', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '菊沢', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '亀田', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '柴山', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '酒井', 'TS'] = hyo2['TS'] * 0.90      
    hyo2.loc[hyo2['jockey'] == '長岡', 'TS'] = hyo2['TS'] * 0.90      
    hyo2.loc[hyo2['jockey'] == '森裕', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '藤懸', 'TS'] = hyo2['TS'] * 0.90      
    hyo2.loc[hyo2['jockey'] == '中村', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '竹之下', 'TS'] = hyo2['TS'] * 0.80 
    hyo2.loc[hyo2['jockey'] == '田中健', 'TS'] = hyo2['TS'] * 0.80 
    hyo2.loc[hyo2['jockey'] == '木幡初', 'TS'] = hyo2['TS'] * 0.80   
    hyo2.loc[hyo2['jockey'] == '杉原', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '中井', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '大久保', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '江田照', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '国分優', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '城戸', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '小林脩', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '西塚', 'TS'] = hyo2['TS'] * 0.90 
    hyo2.loc[hyo2['jockey'] == '鷲頭', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '大江原', 'TS'] = hyo2['TS'] * 0.90    
    hyo2.loc[hyo2['jockey'] == '鮫島良', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '服部', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '丸田', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '小林凌', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '黛', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '武士沢', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '加藤', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '川島', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '簑島', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '大庭', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '藤田菜', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '土田', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '嶋田', 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['jockey'] == '山田', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '佐々木', 'TS'] = hyo2['TS'] * 0.90   
    hyo2.loc[hyo2['jockey'] == '木幡巧', 'TS'] = hyo2['TS'] * 0.90      
    hyo2.loc[hyo2['jockey'] == '岩部', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '小牧太', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '木幡育', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '荻野琢', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '的場', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '江田勇', 'TS'] = hyo2['TS'] * 0.90     
    hyo2.loc[hyo2['jockey'] == '水沼', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '原田', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '井上', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '田村', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '和田翼', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '金子', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '菅原隆', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '柴田未', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '西村', 'TS'] = hyo2['TS'] * 0.80 
    hyo2.loc[hyo2['jockey'] == '鈴木', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '川端', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '柴田善', 'TS'] = hyo2['TS'] * 0.90

    hyo2.loc[hyo2['jockey'] == '高野', 'TS'] = hyo2['TS'] * 0.80
    hyo2.loc[hyo2['jockey'] == '大塚', 'TS'] = hyo2['TS'] * 0.80





    #前走からの斤量増減補正

    hyo2.loc[hyo2['weightgap'] == -6.0, 'TS'] = hyo2['TS'] * 1.20    
    hyo2.loc[hyo2['weightgap'] == -5.5, 'TS'] = hyo2['TS'] * 1.18    
    hyo2.loc[hyo2['weightgap'] == -5.0, 'TS'] = hyo2['TS'] * 1.16
    hyo2.loc[hyo2['weightgap'] == -4.5, 'TS'] = hyo2['TS'] * 1.14    
    hyo2.loc[hyo2['weightgap'] == -4.0, 'TS'] = hyo2['TS'] * 1.12
    hyo2.loc[hyo2['weightgap'] == -3.5, 'TS'] = hyo2['TS'] * 1.10
    hyo2.loc[hyo2['weightgap'] == -3.0, 'TS'] = hyo2['TS'] * 1.08 
    hyo2.loc[hyo2['weightgap'] == -2.5, 'TS'] = hyo2['TS'] * 1.06 
    hyo2.loc[hyo2['weightgap'] == -2.0, 'TS'] = hyo2['TS'] * 1.04 
    hyo2.loc[hyo2['weightgap'] == -1.5, 'TS'] = hyo2['TS'] * 1.02
    hyo2.loc[hyo2['weightgap'] == -1.0, 'TS'] = hyo2['TS'] * 1.0
    hyo2.loc[hyo2['weightgap'] == -0.5, 'TS'] = hyo2['TS'] * 1.0
    hyo2.loc[hyo2['weightgap'] == 0.0, 'TS'] = hyo2['TS'] * 1.0
    hyo2.loc[hyo2['weightgap'] == 0.5, 'TS'] = hyo2['TS'] * 1.0
    hyo2.loc[hyo2['weightgap'] == 1.0, 'TS'] = hyo2['TS'] * 1.0
    hyo2.loc[hyo2['weightgap'] == 1.5, 'TS'] = hyo2['TS'] * 0.98
    hyo2.loc[hyo2['weightgap'] == 2.0, 'TS'] = hyo2['TS'] * 0.96
    hyo2.loc[hyo2['weightgap'] == 2.5, 'TS'] = hyo2['TS'] * 0.94
    hyo2.loc[hyo2['weightgap'] == 3.0, 'TS'] = hyo2['TS'] * 0.92
    hyo2.loc[hyo2['weightgap'] == 3.5, 'TS'] = hyo2['TS'] * 0.90
    hyo2.loc[hyo2['weightgap'] == 4.0, 'TS'] = hyo2['TS'] * 0.88
    hyo2.loc[hyo2['weightgap'] == 4.5, 'TS'] = hyo2['TS'] * 0.86
    hyo2.loc[hyo2['weightgap'] == 5.0, 'TS'] = hyo2['TS'] * 0.84
    hyo2.loc[hyo2['weightgap'] == 5.5, 'TS'] = hyo2['TS'] * 0.82
    hyo2.loc[hyo2['weightgap'] == 6.0, 'TS'] = hyo2['TS'] * 0.80   

    #生産者補正
    hyo2.loc[hyo2['owner'] == 'シルクレ', 'TS'] = hyo2['TS'] * 1.05
    hyo2.loc[hyo2['owner'] == 'キャロッ', 'TS'] = hyo2['TS'] * 1.05
    hyo2.loc[hyo2['owner'] == 'サンデー', 'TS'] = hyo2['TS'] * 1.05

    #馬主補正
    hyo2.loc[hyo2['starion'] == 'ノーザン', 'TS'] = hyo2['TS'] * 1.05


    hyo2['TS']= hyo2['TS'].astype(int)
    final_shisu = hyo2['TS'].to_list()

    import numpy as np

    ave = np.average(final_shisu)
    std = np.std(final_shisu)

    deviation = []
    for i in final_shisu:
      deviation_value = '{:.1f}'.format(float((i - ave) / std * 10 + 50), 1)
      deviation.append(deviation_value)

    hyo2['deviation'] = deviation


    hyo2['rank'] = hyo2['TS'].rank(ascending=False).astype(int)    
    hyo3 = hyo2[['rank','umaban','name','TS','deviation','jockey','stable', 'gender', 'age', 'starion','owner']]
    hyo4 = hyo3.sort_values('rank')

    st.write(race_name[:-21])
    st.dataframe(hyo4)

else:
    st.write('・・・・・・・・')
    

