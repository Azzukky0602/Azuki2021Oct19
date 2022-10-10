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

# タイムゾーンを指定して、日時を作成.
utc_time = dt.now(timezone('Asia/Tokyo'))
kotoshi = utc_time.year

jra = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
nankan = ['浦和', '船橋', '大井', '川崎']
hyogo = ['園田', '姫路']
others = ['門別', '盛岡', '水沢', '金沢', '名古屋', '高知', '佐賀']

age3_GI = ['皐月賞(G1)', '東京優駿(G1)', '菊花賞(G1)', '桜花賞(G1)', '優駿牝馬(G1)',
           '秋華賞(G1)', 'NHKマイルC(G1)', 'ジャパンダートダービ(G1)']
age3_GII = ['神戸新聞杯(G2)', '関西TVローズS(G2)', 'チューリップ賞(G2)', 'テレビ東京杯青葉賞(G2)', '朝日セントライト記念(G2)',
            'サンスポ賞フローラS(G2)', '京都新聞杯(G2)', 'ニュージーランドT(G2)', 'フジTVスプリングS(G2)', '報知弥生ディープ記念(G2)',
            'フィリーズレビュー(G2)']
age3_GIII = ['フェアリーS(G3)', '共同通信杯(G3)', 'ラジオNIKKEI賞(G3)', '日刊スポシンザン記念(G3)', '毎日杯(G3)',
             'デイリー杯クイーンC(G3)', 'アーリントンC(G3)', '中スポ賞ファルコンS(G3)', 'きさらぎ賞(G3)',
            '共同通信杯(G3)', '京成杯(G3)', 'ユニコーンS(G3)', 'フラワーC(G3)', '紫苑S(G3)', 'レパードS(G3)']
age3_L = ['若葉S(L)', '若駒S(L)', 'クロッカスS(L)', 'ジュニアC(L)', '葵S(G)', 'プリンシパルS(L)', '鳳雛S(L)', 'ヒヤシンスS(L)',
         '紅梅S(L)', 'エルフィンS(L)', 'アネモネS(L)', 'スイートピーS(L)', '忘れな草賞(L)']
age3_OP = ['すみれS(OP)', '青竜S(OP)', '端午S(OP)', '青竜S(OP)', '伏竜S(OP)']


st.title('テキトー指数研究所＠WEB')
st.header('JRA 永久版')

st.write('   ')
st.info('【参考】テキトー指数の使い方  \nhttps://note.com/tekito_lab/n/n3342d6531772')
st.info('開催回、開催日を確認してください  \nhttps://www.jra.go.jp/')

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
    hyo = pd.read_html(url)[0]
    hyo.columns = hyo.columns.droplevel(0)
    hyo.columns = ['waku', 'umaban', 'noneed1', 'name', 'age', 'weight', 'jockey', 'stable', 'bodyweight', 'noneed1', 'odds', 'noneed2', 'noneed3']    
    hyo.drop(columns=['waku', 'noneed1', 'noneed2', 'noneed3', 'bodyweight', 'odds'], inplace=True)
    
    
    hyo2 = copy.deepcopy(hyo)
    hyo2['性'] = hyo2['age'].str[0]
    hyo2['年齢'] = hyo2['age'].str[1:].astype(int)


    html = requests.get(url)
    html.encoding = 'EUC-JP'
    soup = BeautifulSoup(html.text, "html.parser")

    time.sleep(1)
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
    for sei in hyo2['性']:
        L3.append(sei)

    L4 = []
    for rei in hyo2['年齢']:
        L4.append(str(rei))

    syusso_list = [x1 + ' ' + x2 +  ' ' + x3 + ' ' + x4  for (x1, x2, x3, x4) in zip(L1, L2, L3, L4)]


    tekito_shisu_list = []
    past_weight_list = []
    for horse in  syusso_list:
        url2 = 'https://db.netkeiba.com/horse/result/' + horse[:10]
        past_results = pd.read_html(url2, header = 0, encoding='EUC-JP')[0].head(10)
        past_results.columns = ['col1', 'col2','col3','col4','col5','col6','col7','col8','col9','col10','col11','col12','col13','col14',\
                       'col15','col16','col17','col18','col19','col20','col21','col22','col23','col24','col25','col26','col27','col28']
        past_results['日付2'] = [dt.strptime(i, "%Y/%m/%d") for i in past_results['col1']]
        past_results['着順'] = past_results['col12'].astype(str)
        past_results['コース'] = past_results['col15'].str[0]
        past_results['距離2'] = past_results['col15'].str[1:].astype(int)
        past_results['開催2'] = past_results['col2'].str.extract('(\D+)')
        past_results['過去斤量'] = past_results['col14']
        past_results['着差'] = past_results['col19']
        past_results['レース名'] = past_results['col15']
        npr = past_results.loc[:, ['日付2', '開催2', 'レース名', 'コース', '距離2', '着順', '着差', '過去斤量']].dropna()
        npr = npr[(npr['着差'] < 3.5)] 
        npr = npr[~npr['着順'].str.contains('降')]
        npr['着順'] = npr['着順'].astype(int)
        npr.reset_index()

        past_weight_list.append(npr[0]['過去斤量'])

        if len(npr) < 3:
            tekito_shisu = 0
            tekito_shisu_list.append(tekito_shisu)

        #3歳、3戦のみ
        elif len(npr) == 3:
            if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):

                base_number = []
                for t in range(3):

                    if 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):  
                        kijun = 500
                    elif 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                        kijun = 350        
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 430
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300 
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 415
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300    
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝' in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300           
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]


            elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 6, 1):

                base_number = []
                for t in range(3):

                    if npr.iloc[t]['レース名'] in age3_GI:  
                        kijun = 600
                    elif 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                        kijun = 350                                                    
                    elif npr.iloc[t]['レース名'] in age3_GII:
                        kijun = 530
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['レース名'] in age3_GIII:
                        kijun = 515
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['レース名'] in age3_L:
                        kijun = 500   
                    elif npr.iloc[t]['レース名'] in age3_OP:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GI: 
                        kijun = 800
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GII:
                        kijun = 700
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GIII:
                        kijun = 650
                    elif 'L' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_L:
                        kijun = 600
                    elif 'OP' in npr.iloc[t]['レース名']and npr.iloc[t]['レース名'] not in age3_OP:
                        kijun = 600                                                                             
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝' in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300          
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]                

            else:        

                base_number = []
                for t in range(3):                

                    if npr.iloc[t]['開催2'] in jra and 'G1' in npr.iloc[t]['レース名']:  
                        kijun = 800
                    elif npr.iloc[t]['開催2'] in jra and 'G2' in npr.iloc[t]['レース名']:
                        kijun = 700
                    elif npr.iloc[t]['開催2'] in jra and 'G3' in npr.iloc[t]['レース名']:
                        kijun = 650
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名']:
                        kijun = 600
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名']:
                        kijun = 600
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '1600' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝'in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1000' in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300  
                    elif npr.iloc[t]['開催2'] in jra and '500' in npr.iloc[t]['レース名']:
                        kijun = 300           
                    elif npr.iloc[t]['開催2'] not in jra and 'G1' in npr.iloc[t]['レース名']:  
                        kijun = 700
                    elif npr.iloc[t]['開催2'] not in jra  and 'G2' in npr.iloc[t]['レース名']:  
                        kijun = 600
                    elif npr.iloc[t]['開催2'] not in jra  and 'G3' in npr.iloc[t]['レース名']:  
                        kijun = 500
                    else:
                        kijun = 200
                    base_number.append(kijun)                   

                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

            #着差係数
            chakusa = []
            for u in range(3):

                if npr.iloc[u]['着差'] < -0.7:
                    race_chakusa = 1.5
                elif -0.7 <= npr.iloc[u]['着差'] < -0.5:
                    race_chakusa = 1.3    
                elif -0.5 <= npr.iloc[u]['着差'] < -0.3:
                    race_chakusa = 1.2
                elif -0.3 <= npr.iloc[u]['着差'] <= 0.5:
                    race_chakusa = 1.0
                elif 0.5 < npr.iloc[u]['着差'] <= 1.0:
                    race_chakusa = 0.8
                elif 1.0 < npr.iloc[u]['着差'] <= 2.0:
                    race_chakusa = 0.5
                else:
                    race_chakusa = 0.2
                chakusa.append(race_chakusa)

            a, b, c = chakusa[0], chakusa[1], chakusa[2]

            #連勝係数    
            if npr.iloc[0]['着順'] == "1" and npr.iloc[1]['着順'] == "1" and npr.iloc[2]['着順'] == "1":
                rensho = (npr.iloc[0]['着差'] + npr.iloc[1]['着差'] + npr.iloc[2]['着差']) / 3
                if rensho < -0.7:
                    e = 1.4
                elif -0.7 <= rensho < -0.5:
                    e = 1.3    
                elif -0.5 <= rensho < -0.3:
                    e = 1.2
                else:
                    e = 1.1
            elif npr.iloc[0]['着順'] == "1" and npr.iloc[1]['着順'] == "1": #and npr.iloc[2]['着順'] != "1":
                rensho = (npr.iloc[0]['着差'] + npr.iloc[1]['着差'] + npr.iloc[2]['着差']) / 3
                if rensho < -0.7:
                    e = 1.3
                elif -0.7 <= rensho < -0.5:
                    e = 1.2    
                elif -0.5 <= rensho < -0.3:
                    e = 1.1
                else:
                    e = 1.05
            else:
                e = 1.0

            #斤量補正
            if 1000 <= race_distance <= 1400:
                if all(L3) =='牝':
                    f = kijun1 * 0.20 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.20 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.20 * (max(hyo2['weight']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.10 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.10 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.10 * (max(hyo2['weight']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15])) 



            #休養係数
            if td(weeks = 0) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (race_date - npr.iloc[0]['日付2']):
                g = 0.8
            else:
                g = 1.0                


            #距離係数                
            av_dist = (npr.iloc[0]['距離2'] + npr.iloc[1]['距離2'] + npr.iloc[2]['距離2']) / 3 
            if 1000 <= race_distance <= 1400:
                if abs(race_distance - npr.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                    h = 0.9
                else:
                    h = 1.0
            elif 1400 < race_distance <= 1800:
                if abs(race_distance - npr.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                    h = 0.9
                else:
                    h = 1.0
            elif 1800 < race_distance <= 2400:
                if abs(race_distance - npr.iloc[0]['距離2']) > 400 and abs(race_distance - av_dist) > 400:
                    h = 0.9
                else:
                    h = 1.0
            elif 2400 < race_distance:
                if abs(race_distance - npr.iloc[0]['距離2']) > 500 and av_dist < 2000:
                    h = 0.9
                else:
                    h = 1.0

            #コース係数
            if race_course == 'ダ':
                if npr.iloc[0]['コース'] == '芝' and npr.iloc[1]['コース'] == '芝' and npr.iloc[2]['コース'] == '芝':
                    i = 0.7
                else:
                    i = 1.0
            elif race_course == '芝':
                if npr.iloc[0]['コース'] == 'ダ' and npr.iloc[1]['コース'] == 'ダ' and npr.iloc[2]['コース'] == 'ダ':
                    i = 0.7
                else:
                    i = 1.0



            ts = ((kijun1 * 2 * a * 2 + kijun2 * b + kijun3 * c) + f) * e * g * h * i
            tekito_shisu = int(ts)
            tekito_shisu_list.append(tekito_shisu)


        #3歳　春　補正　4戦以上
        else:
            if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):

                base_number = []
                for t in range(4):

                    if 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):  
                        kijun = 500
                    elif 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                        kijun = 350        
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 430
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300 
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 415
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300    
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                    and npr.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝' in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300           
                    else:
                        kijun = 200
                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]    

    #3歳　秋　補正　4戦以上
            elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 6, 1):

                base_number = []
                for t in range(4):

                    if 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                        kijun = 350                                                    
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名'] \
                        and npr.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                        kijun = 300

                    elif npr.iloc[t]['レース名'] in age3_GI:
                        if int(npr.iloc[t]['着順']) <= 5:  
                            kijun = 800
                        elif float(npr.iloc[t]['着差']) <= 0.5:  
                            kijun = 800
                        else:
                            kijun = 600

                    elif npr.iloc[t]['レース名'] in age3_GII:
                        kijun = 530
                    elif npr.iloc[t]['レース名'] in age3_GIII:
                        kijun = 515
                    elif npr.iloc[t]['レース名'] in age3_L:
                        kijun = 500   
                    elif npr.iloc[t]['レース名'] in age3_OP:
                        kijun = 500
                    elif 'G1' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GI: 
                        kijun = 800
                    elif 'G2' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GII:
                        kijun = 700
                    elif 'G3' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_GIII:
                        kijun = 650
                    elif 'L' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_L:
                        kijun = 600
                    elif 'OP' in npr.iloc[t]['レース名'] and npr.iloc[t]['レース名'] not in age3_OP:
                        kijun = 600                                                                             
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝' in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300          
                    else:
                        kijun = 200

                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 


        #古馬混合戦の指数
            else:
                base_number = []
                for t in range(4):

                    if npr.iloc[t]['コース'] == '障' and 'J.G1' in npr.iloc[t]['レース名']:  
                        kijun = 800            
                    elif npr.iloc[t]['コース'] == '障' and 'J.G2' in npr.iloc[t]['レース名']:  
                        kijun = 700
                    elif npr.iloc[t]['コース'] == '障' and 'J.G3' in npr.iloc[t]['レース名']:  
                        kijun = 600            
                    elif npr.iloc[t]['コース'] == '障' and 'OP' in npr.iloc[t]['レース名']:  
                        kijun = 500            
                    elif npr.iloc[t]['コース'] == '障' and '未勝利' in npr.iloc[t]['レース名']:  
                        kijun = 400            
                    elif npr.iloc[t]['開催2'] in jra and 'G1' in npr.iloc[t]['レース名']:  
                        kijun = 800
                    elif npr.iloc[t]['開催2'] in jra and 'G2' in npr.iloc[t]['レース名']:
                        kijun = 700
                    elif npr.iloc[t]['開催2'] in jra and 'G3' in npr.iloc[t]['レース名']:
                        kijun = 650
                    elif npr.iloc[t]['開催2'] in jra and 'L' in npr.iloc[t]['レース名']:
                        kijun = 600
                    elif npr.iloc[t]['開催2'] in jra and 'OP' in npr.iloc[t]['レース名']:
                        kijun = 600
                    elif npr.iloc[t]['開催2'] in jra and '3勝' in npr.iloc[t]['レース名']:
                        kijun = 500
                    elif npr.iloc[t]['開催2'] in jra and '2勝'in npr.iloc[t]['レース名']:
                        kijun = 400
                    elif npr.iloc[t]['開催2'] in jra and '1勝' in npr.iloc[t]['レース名']:
                        kijun = 300  
                    elif npr.iloc[t]['開催2'] not in jra and 'G1' in npr.iloc[t]['レース名']:  
                        kijun = 700
                    elif npr.iloc[t]['開催2'] not in jra  and 'G2' in npr.iloc[t]['レース名']:  
                        kijun = 600
                    elif npr.iloc[t]['開催2'] not in jra  and 'G3' in npr.iloc[t]['レース名']:  
                        kijun = 500
                    else:
                        kijun = 200

                    base_number.append(kijun)

                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 

            #着差係数

            chakusa = []
            for u in range(4):

                if npr.iloc[u]['着差'] < -0.7:
                    race_chakusa = 1.5
                elif -0.7 <= npr.iloc[u]['着差'] < -0.5:
                    race_chakusa = 1.3    
                elif -0.5 <= npr.iloc[u]['着差'] < -0.3:
                    race_chakusa = 1.2
                elif -0.3 <= npr.iloc[u]['着差'] <= 0.5:
                    race_chakusa = 1.0
                elif 0.5 < npr.iloc[u]['着差'] <= 1.0:
                    race_chakusa = 0.8
                elif 1.0 < npr.iloc[u]['着差'] <= 2.0:
                    race_chakusa = 0.5
                else:
                    race_chakusa = 0.2
                chakusa.append(race_chakusa)

            a, b, c, d = chakusa[0], chakusa[1], chakusa[2], chakusa[3]                    

            #連勝係数    
            if npr.iloc[0]['着順'] == "1" and npr.iloc[1]['着順'] == "1" and npr.iloc[2]['着順'] == "1" and npr.iloc[3]['着順'] == "1":
                rensho = (npr.iloc[0]['着差'] + npr.iloc[1]['着差'] + npr.iloc[2]['着差'] + npr.iloc[3]['着差']) / 4
                if rensho < -0.7:
                    e = 1.5
                elif -0.7 <= rensho < -0.5:
                    e = 1.4    
                elif -0.5 <= rensho < -0.3:
                    e = 1.3
                else:
                    e = 1.2
            elif npr.iloc[0]['着順'] == "1" and npr.iloc[1]['着順'] == "1" and npr.iloc[2]['着順'] == "1": #and npr.iloc[3]['着順'] != 1:
                rensho = (npr.iloc[0]['着差'] + npr.iloc[1]['着差'] + npr.iloc[2]['着差'] + npr.iloc[3]['着差']) / 4
                if rensho < -0.7:
                    e = 1.4
                elif -0.7 <= rensho < -0.5:
                    e = 1.3   
                elif -0.5 <= rensho < -0.3:
                    e = 1.2
                else:
                    e = 1.1
            elif npr.iloc[0]['着順'] == "1" and npr.iloc[1]['着順'] == "1": #and npr.iloc[2]['着順'] != 1 and npr.iloc[3]['着順'] != 1:
                rensho = (npr.iloc[0]['着差'] + npr.iloc[1]['着差'] + npr.iloc[2]['着差'] + npr.iloc[3]['着差']) / 4
                if rensho < -0.7:
                    e = 1.3
                elif -0.7 <= rensho < -0.5:
                    e = 1.2
                elif -0.5 <= rensho < -0.3:
                    e = 1.1
                else:
                    e = 1.05                       
            else:
                e = 1.0


            #斤量補正
            if 1000 <= race_distance <= 1400:
                if all(L3) =='牝':
                    f = kijun1 * 0.20 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.20 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.20 * (max(hyo2['weight']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(hyo2['weight']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.10 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.10 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.10 * (max(hyo2['weight']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(hyo2['weight']) - float(horse[11:15]))                              


            #休養係数
            if td(weeks = 0) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (race_date - npr.iloc[0]['日付2']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (race_date - npr.iloc[0]['日付2']):
                g = 0.8
            else:
                g = 1.0

            #距離係数                
            av_dist = (npr.iloc[0]['距離2'] + npr.iloc[1]['距離2'] + npr.iloc[2]['距離2'] + npr.iloc[3]['距離2']) / 4 
            if 1000 <= race_distance <= 1400:
                if abs(race_distance - npr.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                    h = 0.9
                else:
                    h = 1.0
            elif 1400 < race_distance <= 1800:
                if abs(race_distance - npr.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                    h = 0.9
                else:
                    h = 1.0
            elif 1800 < race_distance <= 2400:
                if abs(race_distance - npr.iloc[0]['距離2']) > 400 and abs(race_distance - av_dist) > 400:
                    h = 0.9
                else:
                    h = 1.0
            elif 2400 < race_distance:
                if abs(race_distance - npr.iloc[0]['距離2']) > 500 and av_dist < 2000:
                    h = 0.9
                else:
                    h = 1.0

            #コース係数
            if race_course == 'ダ':
                if npr.iloc[0]['コース'] == '芝' and npr.iloc[1]['コース'] == '芝' and npr.iloc[2]['コース'] == '芝':
                    i = 0.7
                else:
                    i = 1.0
            elif race_course == '芝':
                if npr.iloc[0]['コース'] == 'ダ' and npr.iloc[1]['コース'] == 'ダ' and npr.iloc[2]['コース'] == 'ダ':
                    i = 0.7
                else:
                    i = 1.0
            else:
                i = 1.0



            ts = ((kijun1 * 2 *a + kijun2 * 2 * b + kijun3 * c + kijun4 * d) + f) * e * g * h * i
            tekito_shisu = int(ts)
            tekito_shisu_list.append(tekito_shisu)

#計算した指数をリスト化
    hyo2['指数'] = tekito_shisu_list

#前走からの斤量増減   
    s = pd.Series(past_weight_list)
    hyo2['斤量増減']= hyo2['weight']-s

#馬主、生産者係数    
    starion_list = []
    owner_list = []
    for uma_b in L1:
        time.sleep(1)
        url_b = 'https://db.netkeiba.com/horse/' + uma_b
        uma_data = pd.read_html(url_b)[1]
        starion = uma_data[uma_data[0].str.contains('生産者')].iat[0,1][:4]
        owner = uma_data[uma_data[0].str.contains('馬主')].iat[0,1][:4]
        starion_list.append(starion)
        owner_list.append(owner)
    
    hyo2['生産者'] = starion_list
    hyo2['馬主'] = owner_list

#生産者補正
    hyo2.loc[hyo2['馬主'] == 'シルクレ', '指数'] = hyo2['指数'] * 1.05
    hyo2.loc[hyo2['馬主'] == 'キャロッ', '指数'] = hyo2['指数'] * 1.05
    hyo2.loc[hyo2['馬主'] == 'サンデー', '指数'] = hyo2['指数'] * 1.05

#馬主補正
    hyo2.loc[hyo2['生産者'] == 'ノーザン', '指数'] = hyo2['指数'] * 1.05
    

    
#jockey補正：連対率45%以上は1.125, 40%以上は1.1, 35-40%は1.075, 30-35%:1.05, 25-30%:1.025, 20-25%:1.00, 15-20%:0.975, 10-15%:0.95, 5-10%:0.925, 0-5%:0.90

    #三着内率50%以上
    hyo2.loc[hyo2['jockey'] == 'マーフィ', '指数'] = hyo2['指数'] * 1.10 #
    hyo2.loc[hyo2['jockey'] == 'レーン', '指数'] = hyo2['指数'] * 1.075 #
    hyo2.loc[hyo2['jockey'] == 'ルメール', '指数'] = hyo2['指数'] * 1.075 #
    hyo2.loc[hyo2['jockey'] == '川田', '指数'] = hyo2['指数'] * 1.125 #
    hyo2.loc[hyo2['jockey'] == 'Ｃデムーロ', '指数'] = hyo2['指数'] * 1.125 #
    hyo2.loc[hyo2['jockey'] == '伴', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '平沢', '指数'] = hyo2['指数'] * 1.025 #
    
    #三着内率40-50%
    hyo2.loc[hyo2['jockey'] == '高田', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '横山武', '指数'] = hyo2['指数'] * 1.05 #
    hyo2.loc[hyo2['jockey'] == 'Ｍデムーロ', '指数'] = hyo2['指数'] * 1.025 #
    hyo2.loc[hyo2['jockey'] == '福永', '指数'] = hyo2['指数'] * 1.025 #
    hyo2.loc[hyo2['jockey'] == '石神', '指数'] = hyo2['指数'] * 1.025 #   
    hyo2.loc[hyo2['jockey'] == '北沢', '指数'] = hyo2['指数'] * 1.050 #

    #三着内率30-40%
    hyo2.loc[hyo2['jockey'] == '西谷誠', '指数'] = hyo2['指数'] * 1.00 #    
    hyo2.loc[hyo2['jockey'] == '小野寺', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '戸崎圭', '指数'] = hyo2['指数'] * 1.05 #
    hyo2.loc[hyo2['jockey'] == '武豊', '指数'] = hyo2['指数'] * 1.025 #
    hyo2.loc[hyo2['jockey'] == '横山典', '指数'] = hyo2['指数'] * 1.025 #    
    hyo2.loc[hyo2['jockey'] == '岩田望', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '熊沢', '指数'] = hyo2['指数'] * 1.05 #
    hyo2.loc[hyo2['jockey'] == '森一', '指数'] = hyo2['指数'] * 1.025 #    
    hyo2.loc[hyo2['jockey'] == '岩田康', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '藤岡佑', '指数'] = hyo2['指数'] * 0.975 #  

    #三着内率20-30%
    hyo2.loc[hyo2['jockey'] == '松山', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '五十嵐', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '吉田隼', '指数'] = hyo2['指数'] * 1.00 #   
    hyo2.loc[hyo2['jockey'] == '坂井', '指数'] = hyo2['指数'] * 1.00 #   
    hyo2.loc[hyo2['jockey'] == '藤岡康', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '三浦', '指数'] = hyo2['指数'] * 1.00 #    
    hyo2.loc[hyo2['jockey'] == '菅原明', '指数'] = hyo2['指数'] * 0.975 #   
    hyo2.loc[hyo2['jockey'] == '横山和', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '池添', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '西村淳', '指数'] = hyo2['指数'] * 1.00 #    
    hyo2.loc[hyo2['jockey'] == '北村友', '指数'] = hyo2['指数'] * 0.975 #           
    hyo2.loc[hyo2['jockey'] == '田辺', '指数'] = hyo2['指数'] * 1.025 #
    hyo2.loc[hyo2['jockey'] == '鮫島克', '指数'] = hyo2['指数'] * 0.975 #    
    hyo2.loc[hyo2['jockey'] == '菱田', '指数'] = hyo2['指数'] * 0.975 #
    hyo2.loc[hyo2['jockey'] == '石橋脩', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '内田博', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '幸', '指数'] = hyo2['指数'] * 0.975 #    
    hyo2.loc[hyo2['jockey'] == '浜中', '指数'] = hyo2['指数'] * 1.00 #
    hyo2.loc[hyo2['jockey'] == '荻野極', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '丹内', '指数'] = hyo2['指数'] * 0.975 #    
    hyo2.loc[hyo2['jockey'] == '石川', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '和田竜', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '岡田', '指数'] = hyo2['指数'] * 0.925 #   
    hyo2.loc[hyo2['jockey'] == '難波', '指数'] = hyo2['指数'] * 1.00 #    
    hyo2.loc[hyo2['jockey'] == '松本', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '団野', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '北村宏', '指数'] = hyo2['指数'] * 0.95 #
     

    hyo2.loc[hyo2['jockey'] == '古川奈', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '古川吉', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '今村', '指数'] = hyo2['指数'] * 0.975 #  
    hyo2.loc[hyo2['jockey'] == '松若', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '角田和', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '富田', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '秋山真', '指数'] = hyo2['指数'] * 0.95 #  
    hyo2.loc[hyo2['jockey'] == '秋山稔', '指数'] = hyo2['指数'] * 0.925 #
    hyo2.loc[hyo2['jockey'] == '白浜', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '川須', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '水口', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '高倉', '指数'] = hyo2['指数'] * 0.925 #     
    hyo2.loc[hyo2['jockey'] == '植野', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['jockey'] == '宮崎', '指数'] = hyo2['指数'] * 0.925 #     
    hyo2.loc[hyo2['jockey'] == '大野', '指数'] = hyo2['指数'] * 0.925 # 
    hyo2.loc[hyo2['jockey'] == '勝浦', '指数'] = hyo2['指数'] * 0.95 # 
    hyo2.loc[hyo2['jockey'] == '田中勝', '指数'] = hyo2['指数'] * 0.95 # 
    hyo2.loc[hyo2['jockey'] == '横山琉', '指数'] = hyo2['指数'] * 0.925 #     
    hyo2.loc[hyo2['jockey'] == '黒岩', '指数'] = hyo2['指数'] * 1.00 # 
    hyo2.loc[hyo2['jockey'] == '上野', '指数'] = hyo2['指数'] * 0.95 #     
    hyo2.loc[hyo2['jockey'] == '松田', '指数'] = hyo2['指数'] * 0.925 #   
    hyo2.loc[hyo2['jockey'] == '永野', '指数'] = hyo2['指数'] * 0.95 #     
    hyo2.loc[hyo2['jockey'] == '斎藤', '指数'] = hyo2['指数'] * 0.95 # 
    hyo2.loc[hyo2['jockey'] == '丸山', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '角田河', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '武藤', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '伊藤', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '柴田大', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '泉谷', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '太宰', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '国分恭', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '松岡', '指数'] = hyo2['指数'] * 0.925 #
    hyo2.loc[hyo2['jockey'] == '吉田豊', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '津村', '指数'] = hyo2['指数'] * 0.95 #
    hyo2.loc[hyo2['jockey'] == '小牧加', '指数'] = hyo2['指数'] * 1.025 #    
    hyo2.loc[hyo2['jockey'] == '小崎', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '永島', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '草野', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '原', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '川又', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '小坂', '指数'] = hyo2['指数'] * 0.95 #      
    hyo2.loc[hyo2['jockey'] == '小沢', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '野中', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '菊沢', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '亀田', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '柴山', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '酒井', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '長岡', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '森裕', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '藤懸', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '中村', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '竹之下', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '田中健', '指数'] = hyo2['指数'] * 0.900 #      
    hyo2.loc[hyo2['jockey'] == '木幡初', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '杉原', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '中井', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '大久保', '指数'] = hyo2['指数'] * 0.900 #  
    hyo2.loc[hyo2['jockey'] == '江田照', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '国分優', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '城戸', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '小林脩', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '西塚', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '鷲頭', '指数'] = hyo2['指数'] * 0.925 #  
    hyo2.loc[hyo2['jockey'] == '大江原', '指数'] = hyo2['指数'] * 0.95 #    
    hyo2.loc[hyo2['jockey'] == '鮫島良', '指数'] = hyo2['指数'] * 0.925 #   
    hyo2.loc[hyo2['jockey'] == '服部', '指数'] = hyo2['指数'] * 0.925 #
    hyo2.loc[hyo2['jockey'] == '丸田', '指数'] = hyo2['指数'] * 0.925 #    
    hyo2.loc[hyo2['jockey'] == '小林凌', '指数'] = hyo2['指数'] * 0.925 # 
    hyo2.loc[hyo2['jockey'] == '黛', '指数'] = hyo2['指数'] * 0.925 # 
    hyo2.loc[hyo2['jockey'] == '武士沢', '指数'] = hyo2['指数'] * 0.900 # 
    hyo2.loc[hyo2['jockey'] == '加藤', '指数'] = hyo2['指数'] * 0.925 #     
    hyo2.loc[hyo2['jockey'] == '川島', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['jockey'] == '簑島', '指数'] = hyo2['指数'] * 0.900 #     
    hyo2.loc[hyo2['jockey'] == '大庭', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['jockey'] == '藤田菜', '指数'] = hyo2['指数'] * 0.900 #  
    hyo2.loc[hyo2['jockey'] == '土田', '指数'] = hyo2['指数'] * 0.900 #      
    hyo2.loc[hyo2['jockey'] == '嶋田', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '山田', '指数'] = hyo2['指数'] * 0.900 #      
    hyo2.loc[hyo2['jockey'] == '佐々木', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '木幡巧', '指数'] = hyo2['指数'] * 0.950 #      
    hyo2.loc[hyo2['jockey'] == '岩部', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['jockey'] == '小牧太', '指数'] = hyo2['指数'] * 0.900 #
    hyo2.loc[hyo2['jockey'] == '木幡育', '指数'] = hyo2['指数'] * 0.925 #      
    hyo2.loc[hyo2['jockey'] == '荻野琢', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['jockey'] == '的場', '指数'] = hyo2['指数'] * 0.900 
    hyo2.loc[hyo2['jockey'] == '江田勇', '指数'] = hyo2['指数'] * 0.925 #     
    hyo2.loc[hyo2['jockey'] == '水沼', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['jockey'] == '原田', '指数'] = hyo2['指数'] * 0.900 #    
    hyo2.loc[hyo2['jockey'] == '井上', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '田村', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '和田翼', '指数'] = hyo2['指数'] * 0.900
    hyo2.loc[hyo2['jockey'] == '金子', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '菅原隆', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '柴田未', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '西村', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '鈴木', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '川端', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['jockey'] == '柴田善', '指数'] = hyo2['指数'] * 0.925 #    

    hyo2.loc[hyo2['jockey'] == '高野', '指数'] = hyo2['指数'] * 0.900
    hyo2.loc[hyo2['jockey'] == '大塚', '指数'] = hyo2['指数'] * 0.900
    
    
    
    
#前走からの斤量増減補正

    hyo2.loc[hyo2['斤量増減'] == -6.0, '指数'] = hyo2['指数'] * 1.20    
    hyo2.loc[hyo2['斤量増減'] == -5.5, '指数'] = hyo2['指数'] * 1.18    
    hyo2.loc[hyo2['斤量増減'] == -5.0, '指数'] = hyo2['指数'] * 1.16
    hyo2.loc[hyo2['斤量増減'] == -4.5, '指数'] = hyo2['指数'] * 1.14    
    hyo2.loc[hyo2['斤量増減'] == -4.0, '指数'] = hyo2['指数'] * 1.12
    hyo2.loc[hyo2['斤量増減'] == -3.5, '指数'] = hyo2['指数'] * 1.10
    hyo2.loc[hyo2['斤量増減'] == -3.0, '指数'] = hyo2['指数'] * 1.08 
    hyo2.loc[hyo2['斤量増減'] == -2.5, '指数'] = hyo2['指数'] * 1.06 
    hyo2.loc[hyo2['斤量増減'] == -2.0, '指数'] = hyo2['指数'] * 1.04 
    hyo2.loc[hyo2['斤量増減'] == -1.5, '指数'] = hyo2['指数'] * 1.02
    hyo2.loc[hyo2['斤量増減'] == -1.0, '指数'] = hyo2['指数'] * 1.0
    hyo2.loc[hyo2['斤量増減'] == -0.5, '指数'] = hyo2['指数'] * 1.0
    hyo2.loc[hyo2['斤量増減'] == 0.0, '指数'] = hyo2['指数'] * 1.0
    hyo2.loc[hyo2['斤量増減'] == 0.5, '指数'] = hyo2['指数'] * 1.0
    hyo2.loc[hyo2['斤量増減'] == 1.0, '指数'] = hyo2['指数'] * 1.0
    hyo2.loc[hyo2['斤量増減'] == 1.5, '指数'] = hyo2['指数'] * 0.98
    hyo2.loc[hyo2['斤量増減'] == 2.0, '指数'] = hyo2['指数'] * 0.96
    hyo2.loc[hyo2['斤量増減'] == 2.5, '指数'] = hyo2['指数'] * 0.94
    hyo2.loc[hyo2['斤量増減'] == 3.0, '指数'] = hyo2['指数'] * 0.92
    hyo2.loc[hyo2['斤量増減'] == 3.5, '指数'] = hyo2['指数'] * 0.90
    hyo2.loc[hyo2['斤量増減'] == 4.0, '指数'] = hyo2['指数'] * 0.88
    hyo2.loc[hyo2['斤量増減'] == 4.5, '指数'] = hyo2['指数'] * 0.86
    hyo2.loc[hyo2['斤量増減'] == 5.0, '指数'] = hyo2['指数'] * 0.84
    hyo2.loc[hyo2['斤量増減'] == 5.5, '指数'] = hyo2['指数'] * 0.82
    hyo2.loc[hyo2['斤量増減'] == 6.0, '指数'] = hyo2['指数'] * 0.80    
            
    
    hyo2['指数']= hyo2['指数'].astype(int)

#偏差値計算    
    final_shisu = hyo2['指数'].to_list()
    ave = np.average(final_shisu)
    std = np.std(final_shisu)

    deviation = []
    for i in final_shisu:
      deviation_value = '{:.1f}'.format(float((i - ave) / std * 10 + 50), 1)
      deviation.append(deviation_value)

    hyo2['偏差値'] = deviation
    
    
    
    
    hyo2['weight']= hyo2['weight'].astype(str)
    hyo2['順位'] = hyo2['指数'].rank(ascending=False).astype(int)
    hyo2['馬番'] = hyo2['umaban']
    hyo2['騎手'] = hyo2['jockey']
    hyo2['厩舎'] = hyo2['stable']
    hyo3 = hyo2[['順位','umaban','指数','偏差値','jockey','stable', '性', '年齢', '生産者','馬主']]
    hyo4 = hyo3.sort_values('順位')
    hyo4.set_index("順位", inplace=True)
    
    st.write(race_name[:-26])
    st.table(hyo4)


else:
    st.write('・・・・・・・・')
    

