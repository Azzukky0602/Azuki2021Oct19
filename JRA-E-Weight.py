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
from datetime import timezone
import copy
import numpy as np



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

utc_time = dt.now(timezone.utc)
jst_time_today = utc_time.astimezone(timezone(td(hours=+9)))
kotoshi = jst_time_today.year


push = st.button('計算！')
if push == True:
   
    st.write('計算には約1分かかります。しばらくお待ちください。')
    
    url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + str(kotoshi) + race_for_keisan + '&rf=race_submenu'
    hyo = pd.read_html(url, header = 1)[0]

    hyo2 = copy.deepcopy(hyo)
    hyo2['性'] = hyo2['性齢'].map(lambda x:str(x)[0])
    hyo2['年齢'] = hyo2['性齢'].map(lambda x:str(x)[1:]).astype(int)
    hyo2.drop(['印', '登録', 'メモ', '人気', '馬体重(増減)', '性齢'], axis = 1, inplace = True)


    html = requests.get(url)
    html.encoding = 'EUC-JP'
    soup = BeautifulSoup(html.text, "html.parser")

    time.sleep(1)
    syusso = soup.find('table').find_all('a', attrs = {'href': re.compile('^https://db.netkeiba.com/horse/')})
    syusso2 = soup.select('td:nth-of-type(6)')
    seirei = soup.select('td.Barei')


    if bool(syusso) == False:
        print('該当レースはありません')       
        
        
    else:
        day_css = soup.select('#RaceList_DateList > dd.Active > a')[0]
        rd = re.findall((r'\d+'), day_css['href'])[0]
        race_date = pd.Timestamp(rd)
        race_name = soup.find('title').text
        race_course = soup.find_all(class_='RaceData01')[0].text.strip()[10]  #20201219 netkeibaのWEB変更を受けて修正
        race_distance = int(soup.find_all(class_='RaceData01')[0].text.strip()[11:15]) #20201219 netkeibaのWEB変更を受けて修正

        L1 = []
        for uma in syusso:
            horse_id = re.findall(r'\d+', uma['href'])[0]
            L1.append(horse_id)

        L2 = []
        for weight in hyo2['斤量']:
            L2.append(str(weight))

        L3 = []
        for sei in hyo2['性']:
            L3.append(sei)

        L4 = []
        for rei in hyo2['年齢']:
            L4.append(str(rei))

        syusso_list = [x1 + ' ' + x2 +  ' ' + x3 + ' ' + x4  for (x1, x2, x3, x4) in zip(L1, L2, L3, L4)]


        horse_results = {}                                  
        for horse_id in syusso_list:
            try:                
                time.sleep(1)
                url2 = 'https://db.netkeiba.com/horse/result/' + horse_id[:10]    
                horse_results[horse_id] = pd.read_html(url2)[0]#.head(10)
            except:
                pass

        past_results = copy.deepcopy(horse_results)   #個々から下のコードに影響されないhorse_resultsのコピーを作る。

        processed_horse_results = {}
        for horse_id, df in past_results.items():

            df['日付2'] = [dt.strptime(i, "%Y/%m/%d") for i in df['日付']]
            df['着順2'] = df['着順'].map(lambda x:str(x).split('(')[0])
            df['コース'] = df['距離'].map(lambda x:str(x)[0])
            df['距離2'] = df['距離'].map(lambda x:str(x)[1:]).astype(int)
            df['開催2'] = df['開催'].str.extract('(\D+)')
            df['過去斤量'] = df['斤量']

            df.drop(['天気', '映像', '頭数', '枠番', 'ﾀｲﾑ指数', '通過', 'ペース', '上り','騎手', 'R', '馬場指数', '斤量', 'オッズ', '人気', '馬体重', '厩舎ｺﾒﾝﾄ', '備考', '賞金', '勝ち馬(2着馬)', '日付', '距離', '馬番', '開催', '着順'], axis = 1, inplace = True)

            df = df.loc[:, ['日付2', '開催2', 'レース名', '馬場', 'コース', '距離2', '着順2', '着差', 'タイム']].dropna()
            df = df[(df['着差'] < 3.5)]

            processed_horse_results[horse_id] = df




    def shisu(processed_horse_results):
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




        tekito_shisu = {}
        for horse_id, p_df in processed_horse_results.items():  #p_dfはprocessed dafa frame
            if len(p_df) < 3:
                tekito_shisu[horse_id] = 0
            
    #3歳、3戦のみ
            elif len(p_df) == 3:
                if int(horse_id[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):

                    base_number = []
                    for t in range(3):

                        if 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):  
                            kijun = 500
                        elif 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                            kijun = 350        
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 430
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300 
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 415
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300    
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300           
                        else:
                            kijun = 200
                        base_number.append(kijun)

                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

                    
                elif int(horse_id[18:]) == 3 and race_date >= dt(kotoshi, 6, 1):

                    base_number = []
                    for t in range(3):

                        if p_df.iloc[t]['レース名'] in age3_GI:  
                            kijun = 600
                        elif 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                            kijun = 350                                                    
                        elif p_df.iloc[t]['レース名'] in age3_GII:
                            kijun = 530
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['レース名'] in age3_GIII:
                            kijun = 515
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['レース名'] in age3_L:
                            kijun = 500   
                        elif p_df.iloc[t]['レース名'] in age3_OP:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GI: 
                            kijun = 800
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GII:
                            kijun = 700
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GIII:
                            kijun = 650
                        elif 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_L:
                            kijun = 600
                        elif 'OP' in p_df.iloc[t]['レース名']and p_df.iloc[t]['レース名'] not in age3_OP:
                            kijun = 600                                                                             
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300          
                        else:
                            kijun = 200
                        base_number.append(kijun)

                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

                else:        

                    base_number = []
                    for t in range(3):                

                        if p_df.iloc[t]['開催2'] in jra and 'G1' in p_df.iloc[t]['レース名']:  
                            kijun = 800
                        elif p_df.iloc[t]['開催2'] in jra and 'G2' in p_df.iloc[t]['レース名']:
                            kijun = 700
                        elif p_df.iloc[t]['開催2'] in jra and 'G3' in p_df.iloc[t]['レース名']:
                            kijun = 650
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名']:
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名']:
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '1600' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝'in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1000' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300  
                        elif p_df.iloc[t]['開催2'] in jra and '500' in p_df.iloc[t]['レース名']:
                            kijun = 300           
                        elif p_df.iloc[t]['開催2'] not in jra and 'G1' in p_df.iloc[t]['レース名']:  
                            kijun = 700
                        elif p_df.iloc[t]['開催2'] not in jra  and 'G2' in p_df.iloc[t]['レース名']:  
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] not in jra  and 'G3' in p_df.iloc[t]['レース名']:  
                            kijun = 500
                        else:
                            kijun = 200
                        base_number.append(kijun)                   

                    kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]

                #着差係数
                chakusa = []
                for u in range(3):

                    if p_df.iloc[u]['着差'] < -0.7:
                        race_chakusa = 1.5
                    elif -0.7 <= p_df.iloc[u]['着差'] < -0.5:
                        race_chakusa = 1.3    
                    elif -0.5 <= p_df.iloc[u]['着差'] < -0.3:
                        race_chakusa = 1.2
                    elif -0.3 <= p_df.iloc[u]['着差'] <= 0.5:
                        race_chakusa = 1.0
                    elif 0.5 < p_df.iloc[u]['着差'] <= 1.0:
                        race_chakusa = 0.8
                    elif 1.0 < p_df.iloc[u]['着差'] <= 2.0:
                        race_chakusa = 0.5
                    else:
                        race_chakusa = 0.2
                    chakusa.append(race_chakusa)

                a, b, c = chakusa[0], chakusa[1], chakusa[2]

                #連勝係数    
                if p_df.iloc[0]['着順2'] == "1" and p_df.iloc[1]['着順2'] == "1" and p_df.iloc[2]['着順2'] == "1":
                    rensho = (p_df.iloc[0]['着差'] + p_df.iloc[1]['着差'] + p_df.iloc[2]['着差']) / 4
                    if rensho < -0.7:
                        e = 1.4
                    elif -0.7 <= rensho < -0.5:
                        e = 1.3    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.2
                    else:
                        e = 1.1
                elif p_df.iloc[0]['着順2'] == "1" and p_df.iloc[1]['着順2'] == "1": #and p_df.iloc[2]['着順2'] != "1":
                    rensho = (p_df.iloc[0]['着差'] + p_df.iloc[1]['着差'] + p_df.iloc[2]['着差']) / 4
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
                        f = kijun1 * 0.30 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.30 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.30 * (max(hyo2['斤量']) - float(horse_id[11:15]))                
                elif 1400 < race_distance <= 1800:
                    if all(L3) =='牝':
                        f = kijun1 * 0.20 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.20 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.20 * (max(hyo2['斤量']) - float(horse_id[11:15]))                            
                elif 1800 < race_distance <= 2400:
                    if all(L3) =='牝':
                        f = kijun1 * 0.10 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.10 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.10 * (max(hyo2['斤量']) - float(horse_id[11:15]))            
                elif race_distance > 2400:
                    if all(L3) =='牝':
                        f = kijun1 * 0.15 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.15 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.15 * (max(hyo2['斤量']) - float(horse_id[11:15]))            

                            
                #休養係数
                if td(weeks = 0) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 4):
                    g = 0.95
                elif td(weeks = 4) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 16):
                    g = 1.0
                elif td(weeks = 16) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (race_date - p_df.iloc[0]['日付2']):
                    g = 0.8
                else:
                    g = 1.0

                #距離係数                
                av_dist = (p_df.iloc[0]['距離2'] + p_df.iloc[1]['距離2'] + p_df.iloc[2]['距離2']) / 3 
                if 1000 <= race_distance <= 1400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance <= 2400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 400 and abs(race_distance - av_dist) > 400:
                        h = 0.9
                    else:
                        h = 1.0
                elif 2400 < race_distance:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 500 and av_dist < 2000:
                        h = 0.9
                    else:
                        h = 1.0

                #コース係数
                if race_course == 'ダ':
                    if p_df.iloc[0]['コース'] == '芝' and p_df.iloc[1]['コース'] == '芝' and p_df.iloc[2]['コース'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0
                elif race_course == '芝':
                    if p_df.iloc[0]['コース'] == 'ダ' and p_df.iloc[1]['コース'] == 'ダ' and p_df.iloc[2]['コース'] == 'ダ':
                        i = 0.7
                    else:
                        i = 1.0



                ts = ((kijun1 * 2 * a * 2 + kijun2 * b + kijun3 * c) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts) 
            
    #3歳　春　補正　4戦以上
            else:
                if int(horse_id[18:]) == 3 and race_date <= dt(kotoshi, 5, 31):

                    base_number = []
                    for t in range(4):

                        if 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):  
                            kijun = 500
                        elif 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):  
                            kijun = 350        
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 430
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300 
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 415
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300    
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] > dt(kotoshi, 1, 1):
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300           
                        else:
                            kijun = 200
                        base_number.append(kijun)

                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 
                
    #3歳　秋　補正　4戦以上
                elif int(horse_id[18:]) == 3 and race_date >= dt(dt.now().year, 6, 1):

                    base_number = []
                    for t in range(4):

                        if 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(dt.now().year, 1, 1):  
                            kijun = 350                                                    
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(dt.now().year, 1, 1):
                            kijun = 300
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(dt.now().year, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(dt.now().year, 1, 1):
                            kijun = 300
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['日付2'] < dt(dt.now().year, 1, 1):
                            kijun = 300

                        elif p_df.iloc[t]['レース名'] in age3_GI:
                            if int(p_df.iloc[t]['着順2']) <= 5:  
                                kijun = 800
                            elif float(p_df.iloc[t]['着差']) <= 0.5:  
                                kijun = 800
                            else:
                                kijun = 600

                        elif p_df.iloc[t]['レース名'] in age3_GII:
                            kijun = 530
                        elif p_df.iloc[t]['レース名'] in age3_GIII:
                            kijun = 515
                        elif p_df.iloc[t]['レース名'] in age3_L:
                            kijun = 500   
                        elif p_df.iloc[t]['レース名'] in age3_OP:
                            kijun = 500
                        elif 'G1' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GI: 
                            kijun = 800
                        elif 'G2' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GII:
                            kijun = 700
                        elif 'G3' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_GIII:
                            kijun = 650
                        elif 'L' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_L:
                            kijun = 600
                        elif 'OP' in p_df.iloc[t]['レース名'] and p_df.iloc[t]['レース名'] not in age3_OP:
                            kijun = 600                                                                             
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300          
                        else:
                            kijun = 200

                        base_number.append(kijun)

                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]
                        
                else:
                #elif int(horse_id[18:]) != 3 :   #古馬混合戦の指数         
                    base_number = []
                    for t in range(4):

                        if p_df.iloc[t]['コース'] == '障' and 'J.G1' in p_df.iloc[t]['レース名']:  
                            kijun = 800            
                        elif p_df.iloc[t]['コース'] == '障' and 'J.G2' in p_df.iloc[t]['レース名']:  
                            kijun = 700
                        elif p_df.iloc[t]['コース'] == '障' and 'J.G3' in p_df.iloc[t]['レース名']:  
                            kijun = 600            
                        elif p_df.iloc[t]['コース'] == '障' and 'OP' in p_df.iloc[t]['レース名']:  
                            kijun = 500            
                        elif p_df.iloc[t]['コース'] == '障' and '未勝利' in p_df.iloc[t]['レース名']:  
                            kijun = 400                                                   

                        elif p_df.iloc[t]['開催2'] in jra and 'G1' in p_df.iloc[t]['レース名']:  
                            kijun = 800
                        elif p_df.iloc[t]['開催2'] in jra and 'G2' in p_df.iloc[t]['レース名']:
                            kijun = 700
                        elif p_df.iloc[t]['開催2'] in jra and 'G3' in p_df.iloc[t]['レース名']:
                            kijun = 650
                        elif p_df.iloc[t]['開催2'] in jra and 'L' in p_df.iloc[t]['レース名']:
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] in jra and 'OP' in p_df.iloc[t]['レース名']:
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] in jra and '3勝' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '1600' in p_df.iloc[t]['レース名']:
                            kijun = 500
                        elif p_df.iloc[t]['開催2'] in jra and '2勝'in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1000' in p_df.iloc[t]['レース名']:
                            kijun = 400
                        elif p_df.iloc[t]['開催2'] in jra and '1勝' in p_df.iloc[t]['レース名']:
                            kijun = 300  
                        elif p_df.iloc[t]['開催2'] in jra and '500' in p_df.iloc[t]['レース名']:
                            kijun = 300           
                        elif p_df.iloc[t]['開催2'] not in jra and 'G1' in p_df.iloc[t]['レース名']:  
                            kijun = 700
                        elif p_df.iloc[t]['開催2'] not in jra  and 'G2' in p_df.iloc[t]['レース名']:  
                            kijun = 600
                        elif p_df.iloc[t]['開催2'] not in jra  and 'G3' in p_df.iloc[t]['レース名']:  
                            kijun = 500
                        else:
                            kijun = 200

                        base_number.append(kijun)

                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3] 

                #着差係数

                chakusa = []
                for u in range(4):

                    if p_df.iloc[u]['着差'] < -0.7:
                        race_chakusa = 1.5
                    elif -0.7 <= p_df.iloc[u]['着差'] < -0.5:
                        race_chakusa = 1.3    
                    elif -0.5 <= p_df.iloc[u]['着差'] < -0.3:
                        race_chakusa = 1.2
                    elif -0.3 <= p_df.iloc[u]['着差'] <= 0.5:
                        race_chakusa = 1.0
                    elif 0.5 < p_df.iloc[u]['着差'] <= 1.0:
                        race_chakusa = 0.8
                    elif 1.0 < p_df.iloc[u]['着差'] <= 2.0:
                        race_chakusa = 0.5
                    else:
                        race_chakusa = 0.2
                    chakusa.append(race_chakusa)

                a, b, c, d = chakusa[0], chakusa[1], chakusa[2], chakusa[3]                    


                #連勝係数    
                if p_df.iloc[0]['着順2'] == "1" and p_df.iloc[1]['着順2'] == "1" and p_df.iloc[2]['着順2'] == "1" and p_df.iloc[3]['着順2'] == "1":
                    rensho = (p_df.iloc[0]['着差'] + p_df.iloc[1]['着差'] + p_df.iloc[2]['着差'] + p_df.iloc[3]['着差']) / 4
                    if rensho < -0.7:
                        e = 1.5
                    elif -0.7 <= rensho < -0.5:
                        e = 1.4    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.3
                    else:
                        e = 1.2
                elif p_df.iloc[0]['着順2'] == "1" and p_df.iloc[1]['着順2'] == "1" and p_df.iloc[2]['着順2'] == "1": #and p_df.iloc[3]['着順2'] != 1:
                    rensho = (p_df.iloc[0]['着差'] + p_df.iloc[1]['着差'] + p_df.iloc[2]['着差'] + p_df.iloc[3]['着差']) / 4
                    if rensho < -0.7:
                        e = 1.4
                    elif -0.7 <= rensho < -0.5:
                        e = 1.3   
                    elif -0.5 <= rensho < -0.3:
                        e = 1.2
                    else:
                        e = 1.1
                elif p_df.iloc[0]['着順2'] == "1" and p_df.iloc[1]['着順2'] == "1": #and p_df.iloc[2]['着順2'] != 1 and p_df.iloc[3]['着順2'] != 1:
                    rensho = (p_df.iloc[0]['着差'] + p_df.iloc[1]['着差'] + p_df.iloc[2]['着差'] + p_df.iloc[3]['着差']) / 4
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

                if 1000 <= race_distance <= 1400:
                    if all(L3) =='牝':
                        f = kijun1 * 0.30 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.30 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.30 * (max(hyo2['斤量']) - float(horse_id[11:15]))                
                elif 1400 < race_distance <= 1800:
                    if all(L3) =='牝':
                        f = kijun1 * 0.20 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.20 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.20 * (max(hyo2['斤量']) - float(horse_id[11:15]))                            
                elif 1800 < race_distance <= 2400:
                    if all(L3) =='牝':
                        f = kijun1 * 0.10 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.10 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.10 * (max(hyo2['斤量']) - float(horse_id[11:15]))            
                elif race_distance > 2400:
                    if all(L3) =='牝':
                        f = kijun1 * 0.15 * (max(hyo2['斤量']) - float(horse_id[11:15]))
                    else:
                        if '牝' in horse_id:
                            f = kijun1 * 0.15 * (max(hyo2['斤量']) -2.0 - float(horse_id[11:15]))
                        else:
                            f = kijun1 * 0.15 * (max(hyo2['斤量']) - float(horse_id[11:15]))            
                            
                #休養係数
                if td(weeks = 0) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 4):
                    g = 0.95
                elif td(weeks = 4) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 16):
                    g = 1.0
                elif td(weeks = 16) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 36):
                    g = 0.9
                elif td(weeks = 36) < (race_date - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    g = 0.85                
                elif td(weeks = 48) < (race_date - p_df.iloc[0]['日付2']):
                    g = 0.8
                else:
                    g = 1.0

                #距離係数                
                av_dist = (p_df.iloc[0]['距離2'] + p_df.iloc[1]['距離2'] + p_df.iloc[2]['距離2'] + p_df.iloc[3]['距離2']) / 4 
                if 1000 <= race_distance <= 1400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 200 and abs(race_distance - av_dist) > 200:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1400 < race_distance <= 1800:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 300 and abs(race_distance - av_dist) > 300:
                        h = 0.9
                    else:
                        h = 1.0
                elif 1800 < race_distance <= 2400:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 400 and abs(race_distance - av_dist) > 400:
                        h = 0.9
                    else:
                        h = 1.0
                elif 2400 < race_distance:
                    if abs(race_distance - p_df.iloc[0]['距離2']) > 500 and av_dist < 2000:
                        h = 0.9
                    else:
                        h = 1.0

                #コース係数
                if race_course == 'ダ':
                    if p_df.iloc[0]['コース'] == '芝' and p_df.iloc[1]['コース'] == '芝' and p_df.iloc[2]['コース'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0
                elif race_course == '芝':
                    if p_df.iloc[0]['コース'] == 'ダ' and p_df.iloc[1]['コース'] == 'ダ' and p_df.iloc[2]['コース'] == 'ダ':
                        i = 0.7
                    else:
                        i = 1.0
                else:
                    i = 1.0



                ts = ((kijun1 * 2 *a + kijun2 * 2 * b + kijun3 * c + kijun4 * d) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts)

        return tekito_shisu

    kekka = shisu(processed_horse_results)
    hyo2['指数'] = kekka.values()

#前走からの斤量増減        
    past_weight_list = []
    for xxx, kr in horse_results.items():
        kkr = (kr['斤量'][0])
        past_weight_list.append(kkr)
    s = pd.Series(past_weight_list)

    hyo2['斤量増減']= hyo2['斤量']-s

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
    

    
#騎手補正：連対率45%以上は1.125, 40%以上は1.1, 35-40%は1.075, 30-35%:1.05, 25-30%:1.025, 20-25%:1.00, 15-20%:0.975, 10-15%:0.95, 5-10%:0.925, 0-5%:0.90

    #三着内率50%以上
    hyo2.loc[hyo2['騎手'] == 'マーフィー', '指数'] = hyo2['指数'] * 1.10
    hyo2.loc[hyo2['騎手'] == 'レーン', '指数'] = hyo2['指数'] * 1.075
    hyo2.loc[hyo2['騎手'] == 'ルメール', '指数'] = hyo2['指数'] * 1.10
    hyo2.loc[hyo2['騎手'] == '川田', '指数'] = hyo2['指数'] * 1.125
    hyo2.loc[hyo2['騎手'] == 'Ｃデムーロ', '指数'] = hyo2['指数'] * 1.125
    hyo2.loc[hyo2['騎手'] == '伴', '指数'] = hyo2['指数'] * 1.05
    hyo2.loc[hyo2['騎手'] == '平沢', '指数'] = hyo2['指数'] * 1.075    
    
    #三着内率40-50%
    hyo2.loc[hyo2['騎手'] == '高田', '指数'] = hyo2['指数'] * 1.00  
    hyo2.loc[hyo2['騎手'] == '横山武', '指数'] = hyo2['指数'] * 1.05
    hyo2.loc[hyo2['騎手'] == 'Ｍデムーロ', '指数'] = hyo2['指数'] * 1.025
    hyo2.loc[hyo2['騎手'] == '福永', '指数'] = hyo2['指数'] * 1.025
    hyo2.loc[hyo2['騎手'] == '石神', '指数'] = hyo2['指数'] * 1.075    
    hyo2.loc[hyo2['騎手'] == '北沢', '指数'] = hyo2['指数'] * 1.075

    #三着内率30-40%
    hyo2.loc[hyo2['騎手'] == '西谷誠', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '小野寺', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '戸崎圭', '指数'] = hyo2['指数'] * 1.025
    hyo2.loc[hyo2['騎手'] == '武豊', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '横山典', '指数'] = hyo2['指数'] * 1.025    
    hyo2.loc[hyo2['騎手'] == '岩田望', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '熊沢', '指数'] = hyo2['指数'] * 1.05
    hyo2.loc[hyo2['騎手'] == '森一', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '岩田康', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '藤岡佑', '指数'] = hyo2['指数'] * 0.975   

    #三着内率20-30%
    hyo2.loc[hyo2['騎手'] == '松山', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '五十嵐', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '吉田隼', '指数'] = hyo2['指数'] * 1.00    
    hyo2.loc[hyo2['騎手'] == '坂井', '指数'] = hyo2['指数'] * 1.00    
    hyo2.loc[hyo2['騎手'] == '藤岡康', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '三浦', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '菅原明', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '横山和', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '池添', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '西村淳', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '北村友', '指数'] = hyo2['指数'] * 1.00            
    hyo2.loc[hyo2['騎手'] == '田辺', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '鮫島克', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '菱田', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '石橋脩', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '内田博', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '幸', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '浜中', '指数'] = hyo2['指数'] * 1.00
    hyo2.loc[hyo2['騎手'] == '荻野極', '指数'] = hyo2['指数'] * 0.95
    hyo2.loc[hyo2['騎手'] == '丹内', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '石川', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '和田竜', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '岡田', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '難波', '指数'] = hyo2['指数'] * 0.975    
    hyo2.loc[hyo2['騎手'] == '松本', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '団野', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '北村宏', '指数'] = hyo2['指数'] * 0.975
     

    hyo2.loc[hyo2['騎手'] == '古川奈', '指数'] = hyo2['指数'] * 0.975
    hyo2.loc[hyo2['騎手'] == '古川吉', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '今村', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '松若', '指数'] = hyo2['指数'] * 0.95
    hyo2.loc[hyo2['騎手'] == '角田和', '指数'] = hyo2['指数'] * 0.95
    hyo2.loc[hyo2['騎手'] == '富田', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '秋山真', '指数'] = hyo2['指数'] * 0.95  
    hyo2.loc[hyo2['騎手'] == '秋山稔', '指数'] = hyo2['指数'] * 0.95
    hyo2.loc[hyo2['騎手'] == '白浜', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '川須', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '水口', '指数'] = hyo2['指数'] * 0.95    
    hyo2.loc[hyo2['騎手'] == '高倉', '指数'] = hyo2['指数'] * 0.95     
    hyo2.loc[hyo2['騎手'] == '植野', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['騎手'] == '宮崎', '指数'] = hyo2['指数'] * 0.95     
    hyo2.loc[hyo2['騎手'] == '大野', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['騎手'] == '勝浦', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['騎手'] == '田中勝', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['騎手'] == '横山琉', '指数'] = hyo2['指数'] * 0.95     
    hyo2.loc[hyo2['騎手'] == '黒岩', '指数'] = hyo2['指数'] * 0.95 
    hyo2.loc[hyo2['騎手'] == '上野', '指数'] = hyo2['指数'] * 0.95     
    hyo2.loc[hyo2['騎手'] == '松田', '指数'] = hyo2['指数'] * 0.925     
    hyo2.loc[hyo2['騎手'] == '永野', '指数'] = hyo2['指数'] * 0.925     
    hyo2.loc[hyo2['騎手'] == '斎藤', '指数'] = hyo2['指数'] * 0.925 
    hyo2.loc[hyo2['騎手'] == '丸山', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '角田河', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '武藤', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '伊藤', '指数'] = hyo2['指数'] * 0.925
    hyo2.loc[hyo2['騎手'] == '柴田大', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '泉谷', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '太宰', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '国分恭', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '松岡', '指数'] = hyo2['指数'] * 0.925
    hyo2.loc[hyo2['騎手'] == '吉田豊', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '津村', '指数'] = hyo2['指数'] * 0.925
    hyo2.loc[hyo2['騎手'] == '小牧加', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '小崎', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '永島', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '草野', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '原', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '川又', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '小坂', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '小沢', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '野中', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '菊沢', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '亀田', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '柴山', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '酒井', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '長岡', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '森裕', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '藤懸', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '中村', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '竹之下', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '田中健', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '木幡初', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '杉原', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '中井', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '大久保', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '江田照', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '国分優', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '城戸', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '小林脩', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '西塚', '指数'] = hyo2['指数'] * 0.925      
    hyo2.loc[hyo2['騎手'] == '鷲頭', '指数'] = hyo2['指数'] * 0.925  
    hyo2.loc[hyo2['騎手'] == '大江原', '指数'] = hyo2['指数'] * 0.925    
    hyo2.loc[hyo2['騎手'] == '鮫島良', '指数'] = hyo2['指数'] * 0.90    
    hyo2.loc[hyo2['騎手'] == '服部', '指数'] = hyo2['指数'] * 0.90
    hyo2.loc[hyo2['騎手'] == '丸田', '指数'] = hyo2['指数'] * 0.90    
    hyo2.loc[hyo2['騎手'] == '小林凌', '指数'] = hyo2['指数'] * 0.900 
    hyo2.loc[hyo2['騎手'] == '黛', '指数'] = hyo2['指数'] * 0.900 
    hyo2.loc[hyo2['騎手'] == '武士沢', '指数'] = hyo2['指数'] * 0.900 
    hyo2.loc[hyo2['騎手'] == '加藤', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '川島', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '簑島', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '大庭', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '藤田菜', '指数'] = hyo2['指数'] * 0.900  
    hyo2.loc[hyo2['騎手'] == '土田', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '嶋田', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '山田', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '佐々木', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '木幡巧', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '岩部', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '小牧太', '指数'] = hyo2['指数'] * 0.900
    hyo2.loc[hyo2['騎手'] == '木幡育', '指数'] = hyo2['指数'] * 0.900      
    hyo2.loc[hyo2['騎手'] == '荻野琢', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '的場', '指数'] = hyo2['指数'] * 0.900 
    hyo2.loc[hyo2['騎手'] == '江田勇', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '水沼', '指数'] = hyo2['指数'] * 0.900     
    hyo2.loc[hyo2['騎手'] == '原田', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '井上', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '田村', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '和田翼', '指数'] = hyo2['指数'] * 0.900
    hyo2.loc[hyo2['騎手'] == '金子', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '菅原隆', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '柴田未', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '西村', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '鈴木', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '川端', '指数'] = hyo2['指数'] * 0.900    
    hyo2.loc[hyo2['騎手'] == '柴田善', '指数'] = hyo2['指数'] * 0.900    

    hyo2.loc[hyo2['騎手'] == '高野', '指数'] = hyo2['指数'] * 0.900
    hyo2.loc[hyo2['騎手'] == '大塚', '指数'] = hyo2['指数'] * 0.900
    
    
    
    
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
    
    
    
    
    hyo2['斤量']= hyo2['斤量'].astype(str)
    hyo2['順位'] = hyo2['指数'].rank(ascending=False).astype(int)    
    hyo3 = hyo2.iloc[:,[14,1,2,9,13,3,4,7,8,5,11,12]]
    hyo4 = hyo3.sort_values('順位')
    hyo4.set_index("順位", inplace=True)
    
    st.write(race_name[:-26])
    st.table(hyo4)

else:
    st.write('・・・・・・・・')
    

