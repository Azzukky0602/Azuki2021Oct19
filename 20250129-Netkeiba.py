#!/usr/bin/env python
# coding: utf-8

# In[1]:



import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
import lxml.html
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date
from pytz import timezone
import copy
from io import StringIO
import numpy as np

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
st.info('【南関東版】\https://azzukky-nankan.streamlit.app/')
st.info('【地方交流版】\https://azzukky-jpn.streamlit.app/')
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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://race.netkeiba.com/"
}

st.write('   ')
st.subheader('計算するときはチェックボックスをチェック！')
st.subheader('次のレースを計算する前にチェックを外す！')

push = st.checkbox('チェック！！')
if push == True:
   
    st.write('計算には約1分かかります。しばらくお待ちください。')
    
    url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + str(kotoshi) + race_for_keisan + '&rf=race_submenu'
    
    # HTMLを取得
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        exit()
    
    # エンコーディングを明示的に設定
    response.encoding = response.apparent_encoding  # サーバーから推測されたエンコーディングを設定
    html = response.text
    
    # HTMLから表を抽出
    try:
        hyo = pd.read_html(StringIO(html))[0]  # HTML内のすべての表を取得
    except ValueError:
        print("表が見つかりませんでした。")
        exit()
    
    hyo.columns = hyo.columns.droplevel(0)
    hyo.columns = ['waku', 'umaban', 'noneed1', 'name', 'seirei', 'weight', 'jockey', 'stable', 'bodyweight', 'noneed1', 'odds', 'noneed2', 'noneed3', 'noneed4']
    hyo.drop(columns=['waku', 'noneed1', 'noneed2', 'noneed3', 'bodyweight', 'odds', 'noneed4'], inplace=True)
    
    hyo2 = copy.deepcopy(hyo)
    hyo2['gender'] = hyo2['seirei'].str[0]
    hyo2['age'] = hyo2['seirei'].str[1:].astype(int)
    
    soup = BeautifulSoup(html, "html.parser")
    syusso = soup.find('table').find_all('a', attrs = {'href': re.compile('^https://db.netkeiba.com/horse/')})
    
    L1 = [re.search(r'https://db\.netkeiba\.com/horse/(\d+)', a['href']).group(1) for a in syusso]
    
    day_css = soup.select('#RaceList_DateList > dd.Active > a')[0]
    rd = re.findall((r'\d+'), day_css['href'])[0]
    race_date = pd.Timestamp(rd).date()
    race_name = soup.find('title').text
    race_course = soup.find_all(class_='RaceData01')[0].text.strip()[10]  #20201219 netkeibaのWEB変更を受けて修正
    race_distance = int(soup.find_all(class_='RaceData01')[0].text.strip()[11:15]) #20201219 netkeibaのWEB変更を受けて修正
    
    
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

    horse_results = {}
    for horse in syusso_list:
        url2 = 'https://db.netkeiba.com/horse/' + horse[:10] + '/'
        html2 = requests.get(url2, headers = headers)
        html2.encoding = html2.apparent_encoding  # サーバーから推測されたエンコーディングを設定
        html2 = html2.text
        horse_results[horse] = pd.read_html(StringIO(html2))[2].head(30)
        horse_results[horse] = horse_results[horse].drop(columns = ['天 気', 'R', '映 像', '枠 番', '馬 番', 'オ ッ ズ', '人 気', '騎手',\
                                            '馬 場', 'タイム', 'ペース', '通過', '馬体重', '上り', '厩舎 ｺﾒﾝﾄ', \
                                            '勝ち馬 (2着馬)', '賞金', '頭 数', 'ﾀｲﾑ 指数', '備考', '馬場 指数'])
        horse_results[horse] = horse_results[horse][horse_results[horse]["着差"].replace("", None).notna()]
        horse_results[horse] = horse_results[horse][(horse_results[horse]['着差'] < 3.6)]
        horse_results[horse]['place'] = [re.search(r"[一-龥]+", item).group() for item in horse_results[horse]['開催']]
        horse_results[horse]['result'] = horse_results[horse]['着 順'].astype(str)
        horse_results[horse]['course'] = horse_results[horse]['距離'].str[0]
        horse_results[horse]['distance'] = horse_results[horse]['距離'].str[1:].astype("int64") #過去レースの距離
        horse_results[horse]['pastweight'] = horse_results[horse]['斤 量']
        horse_results[horse]['date'] = pd.to_datetime(horse_results[horse]['日付']).dt.date #過去レースの日付
        horse_results[horse]['racename'] = horse_results[horse]['レース名']
        horse_results[horse]['difference'] = horse_results[horse]['着差']
        horse_results[horse] = horse_results[horse].drop(columns = ['開催', '着 順', '距離', '斤 量', '日付', 'レース名', '着差'])
        horse_results[horse] = horse_results[horse].reset_index()
        horse_results[horse] = horse_results[horse].drop(columns = ['index'])
        time.sleep(1)
    
    past_results = copy.deepcopy(horse_results)
    npr = past_results


    
    tekito_shisu_list = []
    for horse in syusso_list:
        
        try:
    
            if npr[horse].empty == True:
                tekito_shisu = 0
                tekito_shisu_list.append(tekito_shisu)            
                    
            elif len(npr[horse]) < 3:
                tekito_shisu = 0
                tekito_shisu_list.append(tekito_shisu)
        
            #3歳、3戦のみ
            elif len(npr[horse]) == 3:
                if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):
        
                    base_number = []
                    for t in range(3):
        
                        if 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):  
                            kijun = 415
                        elif 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):  
                            kijun = 300        
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 430
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 315 
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 500
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 350    
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝' in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300           
                        else:
                            kijun = 200
                        base_number.append(kijun)
        
                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]
        
        
                elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 6, 1):
        
                    base_number = []
                    for t in range(3):
        
                        if npr[horse].iloc[t]['racename'] in age3_GIII:
                            kijun = 515
                        elif 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['racename'] in age3_GII:
                            kijun = 530
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 315                                
                        elif npr[horse].iloc[t]['racename'] in age3_GI:  
                            kijun = 600
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):  
                            kijun = 350                                                   
                        elif npr[horse].iloc[t]['racename'] in age3_L:
                            kijun = 500   
                        elif npr[horse].iloc[t]['racename'] in age3_OP:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GIII: 
                            kijun = 650
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GII:
                            kijun = 700
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GI:
                            kijun = 800
                        elif 'L' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_L:
                            kijun = 600
                        elif 'OP' in npr[horse].iloc[t]['racename']and npr[horse].iloc[t]['racename'] not in age3_OP:
                            kijun = 600                                                                             
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝' in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300          
                        else:
                            kijun = 200
                        base_number.append(kijun)
        
                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]                
        
                else:        
        
                    base_number = []
                    for t in range(3):                
        
                        if npr[horse].iloc[t]['place'] in jra and 'GIII' in npr[horse].iloc[t]['racename']:
                            kijun = 650
                        elif npr[horse].iloc[t]['place'] in jra and 'GII' in npr[horse].iloc[t]['racename']:
                            kijun = 700                
                        elif npr[horse].iloc[t]['place'] in jra and 'GI' in npr[horse].iloc[t]['racename']:  
                            kijun = 800
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename']:
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename']:
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '1600' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝'in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1000' in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300  
                        elif npr[horse].iloc[t]['place'] in jra and '500' in npr[horse].iloc[t]['racename']:
                            kijun = 300           
                        elif npr[horse].iloc[t]['place'] not in jra and 'GIII' in npr[horse].iloc[t]['racename']:  
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] not in jra  and 'GII' in npr[horse].iloc[t]['racename']:  
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] not in jra  and 'GI' in npr[horse].iloc[t]['racename']:  
                            kijun = 700
                        else:
                            kijun = 200
                        base_number.append(kijun)                   
        
                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]
        
                #着差係数
                chakusa = []
                for u in range(3):
        
                    if npr[horse].iloc[u]['difference'] < -0.7:
                        race_chakusa = 1.5
                    elif -0.7 <= npr[horse].iloc[u]['difference'] < -0.5:
                        race_chakusa = 1.3    
                    elif -0.5 <= npr[horse].iloc[u]['difference'] < -0.3:
                        race_chakusa = 1.2
                    elif -0.3 <= npr[horse].iloc[u]['difference'] <= 0.5:
                        race_chakusa = 1.0
                    elif 0.5 < npr[horse].iloc[u]['difference'] <= 1.0:
                        race_chakusa = 0.8
                    elif 1.0 < npr[horse].iloc[u]['difference'] <= 2.0:
                        race_chakusa = 0.5
                    else:
                        race_chakusa = 0.2
                    chakusa.append(race_chakusa)
        
                a, b, c = chakusa[0], chakusa[1], chakusa[2]
        
                #連勝係数    
                if npr[horse].iloc[0]['result'] == "1" and npr[horse].iloc[1]['result'] == "1" and npr[horse].iloc[2]['result'] == "1":
                    rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']) / 3
                    if rensho < -0.7:
                        e = 1.25
                    elif -0.7 <= rensho < -0.5:
                        e = 1.20   
                    elif -0.5 <= rensho < -0.3:
                        e = 1.15
                    else:
                        e = 1.10
                elif npr[horse].iloc[0]['result'] == "1" and npr[horse].iloc[1]['result'] == "1": #and npr[horse].iloc[2]['result'] != "1":
                    rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']) / 3
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
                if td(weeks = 0) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 4):
                    g = 0.95
                elif td(weeks = 4) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 16):
                    g = 1.0
                elif td(weeks = 16) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (race_date - npr[horse].iloc[0]['date']):
                    g = 0.8
                else:
                    g = 1.0                
        
        
                #距離係数                
                av_dist = (npr[horse].iloc[0]['distance'] + npr[horse].iloc[1]['distance'] + npr[horse].iloc[2]['distance']) / 3 
                if 1000 <= race_distance <= 1400:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance <= 2400:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 400 and abs(race_distance - av_dist) > 400:
                        h = 0.9
                    else:
                        h = 1.0
                elif 2400 < race_distance:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 500 and av_dist < 2000:
                        h = 0.9
                    else:
                        h = 1.0
        
                #コース係数
                if race_course == 'ダ':
                    if npr[horse].iloc[0]['course'] == '芝' and npr[horse].iloc[1]['course'] == '芝' and npr[horse].iloc[2]['course'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0
                elif race_course == '芝':
                    if npr[horse].iloc[0]['course'] == 'ダ' and npr[horse].iloc[1]['course'] == 'ダ' and npr[horse].iloc[2]['course'] == 'ダ':
                        i = 0.7
                    else:
                        i = 1.0
        
        
        
                ts = ((kijun1 * a * 2.0 + kijun2 * b *1.1 + kijun3 * c *1.0) + f) * e * g * h * i
                tekito_shisu = int(ts)
                tekito_shisu_list.append(tekito_shisu)
        
                
            #3歳　春　補正　4戦以上
            else:
                if int(horse[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):
        
                    base_number = []
                    for t in range(4):
        
                        if 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):  
                            kijun = 415
                        elif 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):  
                            kijun = 300        
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 430
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 315 
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 500
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 350    
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                        and npr[horse].iloc[t]['date'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝' in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300           
                        else:
                            kijun = 200
                        base_number.append(kijun)
        
                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]    
        
            #3歳　秋　補正　4戦以上
                elif int(horse[18:]) == 3 and race_date >= dt(kotoshi, 6, 1):
        
                    base_number = []
                    for t in range(4):
        
                        if 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):  
                            kijun = 300                                                    
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 315
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 350
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename'] \
                            and npr[horse].iloc[t]['date'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif npr[horse].iloc[t]['racename'] in age3_GIII:
                            kijun = 515
                        elif npr[horse].iloc[t]['racename'] in age3_GII:
                            kijun = 530
                        elif npr[horse].iloc[t]['racename'] in age3_GI:
                            if int(npr[horse].iloc[t]['result']) <= 5:  
                                kijun = 800
                            elif float(npr[horse].iloc[t]['difference']) <= 0.5:  
                                kijun = 800
                            else:
                                kijun = 600
                        elif npr[horse].iloc[t]['racename'] in age3_L:
                            kijun = 500   
                        elif npr[horse].iloc[t]['racename'] in age3_OP:
                            kijun = 500
                        elif 'GIII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GIII:
                            kijun = 650
                        elif 'GII' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GII:
                            kijun = 700
                        elif 'GI' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_GI: 
                            kijun = 800
                        elif 'L' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_L:
                            kijun = 600
                        elif 'OP' in npr[horse].iloc[t]['racename'] and npr[horse].iloc[t]['racename'] not in age3_OP:
                            kijun = 600                                                                             
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝' in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300          
                        else:
                            kijun = 200
        
                        base_number.append(kijun)
        
                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 
        
        
            #古馬混合戦の指数
                else:
                    base_number = []
                    for t in range(4):
        
                        if npr[horse].iloc[t]['course'] == '障' and 'J.GIII' in npr[horse].iloc[t]['racename']:  
                            kijun = 600      
                        elif npr[horse].iloc[t]['course'] == '障' and 'J.GII' in npr[horse].iloc[t]['racename']:  
                            kijun = 700
                        elif npr[horse].iloc[t]['course'] == '障' and 'J.GI' in npr[horse].iloc[t]['racename']:  
                            kijun = 800          
                        elif npr[horse].iloc[t]['course'] == '障' and 'OP' in npr[horse].iloc[t]['racename']:  
                            kijun = 500           
                        elif npr[horse].iloc[t]['course'] == '障' and '未勝利' in npr[horse].iloc[t]['racename']:  
                            kijun = 400           
                        elif npr[horse].iloc[t]['place'] in jra and 'GIII' in npr[horse].iloc[t]['racename']:
                            kijun = 650
                        elif npr[horse].iloc[t]['place'] in jra and 'GII' in npr[horse].iloc[t]['racename']:
                            kijun = 700                                 
                        elif npr[horse].iloc[t]['place'] in jra and 'GI' in npr[horse].iloc[t]['racename']:  
                            kijun = 800
                        elif npr[horse].iloc[t]['place'] in jra and 'L' in npr[horse].iloc[t]['racename']:
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename']:
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] in jra and '2勝'in npr[horse].iloc[t]['racename']:
                            kijun = 400
                        elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                            kijun = 300 
                        elif npr[horse].iloc[t]['place'] not in jra and 'GIII' in npr[horse].iloc[t]['racename']:  
                            kijun = 500
                        elif npr[horse].iloc[t]['place'] not in jra  and 'GII' in npr[horse].iloc[t]['racename']:  
                            kijun = 600
                        elif npr[horse].iloc[t]['place'] not in jra  and 'GI' in npr[horse].iloc[t]['racename']:  
                            kijun = 700
                        else:
                            kijun = 200
        
                        base_number.append(kijun)
        
                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 
        
                #着差係数
        
                chakusa = []
                for u in range(4):
        
                    if npr[horse].iloc[u]['difference'] < -0.7:
                        race_chakusa = 1.5
                    elif -0.7 <= npr[horse].iloc[u]['difference'] < -0.5:
                        race_chakusa = 1.3    
                    elif -0.5 <= npr[horse].iloc[u]['difference'] < -0.3:
                        race_chakusa = 1.2
                    elif -0.3 <= npr[horse].iloc[u]['difference'] <= 0.5:
                        race_chakusa = 1.0
                    elif 0.5 < npr[horse].iloc[u]['difference'] <= 1.0:
                        race_chakusa = 0.8
                    elif 1.0 < npr[horse].iloc[u]['difference'] <= 2.0:
                        race_chakusa = 0.5
                    else:
                        race_chakusa = 0.2
                    chakusa.append(race_chakusa)
        
                a, b, c, d = chakusa[0], chakusa[1], chakusa[2], chakusa[3]                    
        
                #連勝係数    
                if npr[horse].iloc[0]['result'] == "1" and npr[horse].iloc[1]['result'] == "1" \
                and npr[horse].iloc[2]['result'] == "1" and npr[horse].iloc[3]['result'] == "1":
                    rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] \
                              + npr[horse].iloc[2]['difference'] + npr[horse].iloc[3]['difference']) / 4
                    if rensho < -0.7:
                        e = 1.35
                    elif -0.7 <= rensho < -0.5:
                        e = 1.30   
                    elif -0.5 <= rensho < -0.3:
                        e = 1.25
                    else:
                        e = 1.20
                elif npr[horse].iloc[0]['result'] == "1" and npr[horse].iloc[1]['result'] == "1" \
                and npr[horse].iloc[2]['result'] == "1":
                    rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference'] + npr[horse].iloc[3]['difference']) / 4
                    if rensho < -0.7:
                        e = 1.25
                    elif -0.7 <= rensho < -0.5:
                        e = 1.20
                    elif -0.5 <= rensho < -0.3:
                        e = 1.15
                    else:
                        e = 1.10
                elif npr[horse].iloc[0]['result'] == "1" and npr[horse].iloc[1]['result'] == "1":
                    rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference'] + npr[horse].iloc[3]['difference']) / 4
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
                if td(weeks = 0) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 4):
                    g = 0.95
                elif td(weeks = 4) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 16):
                    g = 1.0
                elif td(weeks = 16) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (race_date - npr[horse].iloc[0]['date']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (race_date - npr[horse].iloc[0]['date']):
                    g = 0.8
                else:
                    g = 1.0
        
                #距離係数                
                av_dist = (npr[horse].iloc[0]['distance'] + npr[horse].iloc[1]['distance'] \
                           + npr[horse].iloc[2]['distance'] + npr[horse].iloc[3]['distance']) / 4 
                if 1000 <= race_distance <= 1400:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance <= 2400:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 400 and abs(race_distance - av_dist) > 400:
                        h = 0.9
                    else:
                        h = 1.0
                elif 2400 < race_distance:
                    if abs(race_distance - npr[horse].iloc[0]['distance']) > 500 and av_dist < 2000:
                        h = 0.9
                    else:
                        h = 1.0
        
                #コース係数
                if race_course == 'ダ':
                    if npr[horse].iloc[0]['course'] == '芝' and npr[horse].iloc[1]['course'] == '芝' and npr[horse].iloc[2]['course'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0
                elif race_course == '芝':
                    if npr[horse].iloc[0]['course'] == 'ダ' and npr[horse].iloc[1]['course'] == 'ダ' and npr[horse].iloc[2]['course'] == 'ダ':
                        i = 0.7
                    else:
                        i = 1.0
                else:
                    i = 1.0
        
        
        
                ts = ((kijun1 * 1.3 *a + kijun2 * 1.2 * b + kijun3 * 1.1 * c + kijun4 * 1.0 * d) + f) * e * g * h * i
                tekito_shisu = int(ts)
                tekito_shisu_list.append(tekito_shisu)
    
        
        except KeyError:
            tekito_shisu = 0
            tekito_shisu_list.append(tekito_shisu)  
    
    past_weight_list = []
    for horse in syusso_list:
        zenso_weight = npr[horse]['pastweight'][0].astype('float64')
        past_weight_list.append(zenso_weight)
    
    hyo2['TS'] = tekito_shisu_list
    s = pd.Series(past_weight_list)
    hyo2['weightgap']= hyo2['weight']-s
    
    starion_list = []
    owner_list = []
    for uma_b in L1:
        time.sleep(1)
        url_b = 'https://db.netkeiba.com/horse/' + uma_b + '/'
        html3 = requests.get(url_b, headers = headers)
        html3.encoding = html3.apparent_encoding  # サーバーから推測されたエンコーディングを設定
        html3 = html3.text
        uma_data = pd.read_html(StringIO(html3))[0]
        starion = uma_data[uma_data[0].str.contains('生産者')].iat[0,1][:4]
        owner = uma_data[uma_data[0].str.contains('馬主')].iat[0,1][:4]
        starion_list.append(starion)
        owner_list.append(owner)
    
    hyo2['starion'] = starion_list
    hyo2['owner'] = owner_list
    
    #騎手補正：三着内率＝X%、 X＜20は0.90, 20≦X＜30は1.00, 30≦X＜40は1.10, 40≦X＜50は1.15, 50≦X＜60は1.20
    #2025 01 27時点
    
    #三着内率50%以上
    hyo2.loc[hyo2['jockey'] == 'ルメール', 'TS'] = round(hyo2['TS'] * 1.20)
    hyo2.loc[hyo2['jockey'] == '川田', 'TS'] = round(hyo2['TS'] * 1.20)
    hyo2.loc[hyo2['jockey'] == '小牧加', 'TS'] = round(hyo2['TS'] * 1.20)   
    hyo2.loc[hyo2['jockey'] == '森一', 'TS'] = round(hyo2['TS'] * 1.20) 
    hyo2.loc[hyo2['jockey'] == '西谷誠', 'TS'] = round(hyo2['TS'] * 1.20)  
    
    hyo2.loc[hyo2['jockey'] == 'マーフィ', 'TS'] = round(hyo2['TS'] * 1.20)
    hyo2.loc[hyo2['jockey'] == 'レーン', 'TS'] = round(hyo2['TS'] * 1.20)
    hyo2.loc[hyo2['jockey'] == 'モレイラ', 'TS'] = round(hyo2['TS'] * 1.20)
    
    #三着内率40-50%
    hyo2.loc[hyo2['jockey'] == 'Ｃデムーロ', 'TS'] = round(hyo2['TS'] * 1.15)
    hyo2.loc[hyo2['jockey'] == '戸崎圭', 'TS'] = round(hyo2['TS'] * 1.15)
    hyo2.loc[hyo2['jockey'] == '坂井', 'TS'] = round(hyo2['TS'] * 1.15)
    hyo2.loc[hyo2['jockey'] == 'ビュイック', 'TS'] = round(hyo2['TS'] * 1.15)
    
    #三着内率30-40%
    hyo2.loc[hyo2['jockey'] == 'ムーア', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '高田', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '小坂', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '武豊', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == 'マーカンド', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '松山', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '横山武', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '上野', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == 'Ａルメート', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '鮫島克', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '岩田望', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == 'キング', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == '藤岡佑', 'TS'] = round(hyo2['TS'] * 1.10) 
    hyo2.loc[hyo2['jockey'] == '三浦', 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['jockey'] == 'Ｍデムーロ', 'TS'] = round(hyo2['TS'] * 1.10)
    
    
    #三着内率20-30%
    hyo2.loc[hyo2['jockey'] == '佐々木', 'TS'] = round(hyo2['TS'] * 1.00)     
    hyo2.loc[hyo2['jockey'] == '西村淳', 'TS'] = round(hyo2['TS'] * 1.00)    
    hyo2.loc[hyo2['jockey'] == '田辺', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '五十嵐', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '菅原明', 'TS'] = round(hyo2['TS'] * 1.00)    
    hyo2.loc[hyo2['jockey'] == '北村友', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '浜中', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '石神', 'TS'] = round(hyo2['TS'] * 1.00)    
    hyo2.loc[hyo2['jockey'] == '大江原', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '横山和', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '丹内', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '池添', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '団野', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '横山典', 'TS'] = round(hyo2['TS'] * 1.00)    
    hyo2.loc[hyo2['jockey'] == '津村', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '坂口', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '岩田康', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '金子', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '伴', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '中村', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '江田勇', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '斎藤', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '西塚', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '高杉', 'TS'] = round(hyo2['TS'] * 1.00)      
    hyo2.loc[hyo2['jockey'] == '和田竜', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '石川', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '荻野極', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '菱田', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '水口', 'TS'] = round(hyo2['TS'] * 1.00)
    hyo2.loc[hyo2['jockey'] == '田村', 'TS'] = round(hyo2['TS'] * 1.00)
    
    
    #三着内率　<20%
    hyo2.loc[hyo2['jockey'] == '大野', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '幸', 'TS'] = round(hyo2['TS'] * 0.9)   
    hyo2.loc[hyo2['jockey'] == '北村宏', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '田口', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '吉田豊', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '吉村誠', 'TS'] = round(hyo2['TS'] * 0.9)   
    hyo2.loc[hyo2['jockey'] == '丸山', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '吉田隼', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '中井', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '草野', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '菊沢', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '柴田善', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '石橋脩', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '川又', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '亀田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '角田和', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '鮫島良', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '国分恭', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '松若', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '岡田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '藤懸', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == 'Ｈドイル', 'TS'] = round(hyo2['TS'] * 0.9) 
    hyo2.loc[hyo2['jockey'] == '秋山稔', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '酒井', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '平沢', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '小野寺', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '内田博', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '難波', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '松本', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '古川奈', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '古川吉', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '今村', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '富田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '白浜', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '川須', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '高倉', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '植野', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '宮崎', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '田中勝', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '横山琉', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '黒岩', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '松田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '永野', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '武藤', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '伊藤', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '柴田大', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '泉谷', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '太宰', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '松岡', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '小崎', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '永島', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '原', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '小沢', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '野中', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '柴山', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '長岡', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '森裕', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '藤懸', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '竹之下', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '田中健', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '木幡初', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '杉原', 'TS'] = round(hyo2['TS'] * 0.9) 
    hyo2.loc[hyo2['jockey'] == '大久保', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '江田照', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '国分優', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '城戸', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '小林脩', 'TS'] = round(hyo2['TS'] * 0.9)   
    hyo2.loc[hyo2['jockey'] == '鷲頭', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '丸田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '小林凌', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '黛', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '加藤', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '簑島', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '大庭', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '土田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '嶋田', 'TS'] = round(hyo2['TS'] * 0.9) 
    hyo2.loc[hyo2['jockey'] == '山田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '木幡巧', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '岩部', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '木幡育', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '荻野琢', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '的場', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '水沼', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '原田', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '井上', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '和田翼', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '菅原隆', 'TS'] = round(hyo2['TS'] * 0.9)   
    hyo2.loc[hyo2['jockey'] == '鈴木', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '川端', 'TS'] = round(hyo2['TS'] * 0.9)
    hyo2.loc[hyo2['jockey'] == '大塚', 'TS'] = round(hyo2['TS'] * 0.9)
    
    
    #前走からの斤量増減補正
    
    hyo2.loc[hyo2['weightgap'] == -6.0, 'TS'] = round(hyo2['TS'] * 1.20)    
    hyo2.loc[hyo2['weightgap'] == -5.5, 'TS'] = round(hyo2['TS'] * 1.18)    
    hyo2.loc[hyo2['weightgap'] == -5.0, 'TS'] = round(hyo2['TS'] * 1.16)
    hyo2.loc[hyo2['weightgap'] == -4.5, 'TS'] = round(hyo2['TS'] * 1.14)    
    hyo2.loc[hyo2['weightgap'] == -4.0, 'TS'] = round(hyo2['TS'] * 1.12)
    hyo2.loc[hyo2['weightgap'] == -3.5, 'TS'] = round(hyo2['TS'] * 1.10)
    hyo2.loc[hyo2['weightgap'] == -3.0, 'TS'] = round(hyo2['TS'] * 1.08)
    hyo2.loc[hyo2['weightgap'] == -2.5, 'TS'] = round(hyo2['TS'] * 1.06)
    hyo2.loc[hyo2['weightgap'] == -2.0, 'TS'] = round(hyo2['TS'] * 1.04)
    hyo2.loc[hyo2['weightgap'] == -1.5, 'TS'] = round(hyo2['TS'] * 1.02)
    hyo2.loc[hyo2['weightgap'] == -1.0, 'TS'] = round(hyo2['TS'] * 1.0)
    hyo2.loc[hyo2['weightgap'] == -0.5, 'TS'] = round(hyo2['TS'] * 1.0)
    hyo2.loc[hyo2['weightgap'] == 0.0, 'TS'] = round(hyo2['TS'] * 1.0)
    hyo2.loc[hyo2['weightgap'] == 0.5, 'TS'] = round(hyo2['TS'] * 1.0)
    hyo2.loc[hyo2['weightgap'] == 1.0, 'TS'] = round(hyo2['TS'] * 1.0)
    hyo2.loc[hyo2['weightgap'] == 1.5, 'TS'] = round(hyo2['TS'] * 0.98)
    hyo2.loc[hyo2['weightgap'] == 2.0, 'TS'] = round(hyo2['TS'] * 0.96)
    hyo2.loc[hyo2['weightgap'] == 2.5, 'TS'] = round(hyo2['TS'] * 0.94)
    hyo2.loc[hyo2['weightgap'] == 3.0, 'TS'] = round(hyo2['TS'] * 0.92)
    hyo2.loc[hyo2['weightgap'] == 3.5, 'TS'] = round(hyo2['TS'] * 0.90)
    hyo2.loc[hyo2['weightgap'] == 4.0, 'TS'] = round(hyo2['TS'] * 0.88)
    hyo2.loc[hyo2['weightgap'] == 4.5, 'TS'] = round(hyo2['TS'] * 0.86)
    hyo2.loc[hyo2['weightgap'] == 5.0, 'TS'] = round(hyo2['TS'] * 0.84)
    hyo2.loc[hyo2['weightgap'] == 5.5, 'TS'] = round(hyo2['TS'] * 0.82)
    hyo2.loc[hyo2['weightgap'] == 6.0, 'TS'] = round(hyo2['TS'] * 0.80)   
    
        
    hyo2['TS']= hyo2['TS'].astype(int)
    final_shisu = hyo2['TS'].to_list()
    
    import numpy as np
    
    ave = np.average(final_shisu)
    std = np.std(final_shisu)
    
    deviation = []
    for i in final_shisu:
      deviation_value = float((i - ave) / std * 10 + 50)
      deviation.append(round(deviation_value, 1))
    
    hyo2['deviation'] = deviation
    
    
    hyo2['rank'] = hyo2['TS'].rank(ascending=False).astype(int)    
    hyo3 = hyo2[['rank','umaban','name','TS','deviation','jockey','stable', 'gender', 'age', 'starion','owner']]
    hyo4 = hyo3.sort_values('rank')


    st.write(race_name[:-21])
    st.table(hyo4)

else:
    st.write('・・・・・・・・')
    

