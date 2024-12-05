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

jra = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉', ]

age2_G1 = ['ホープフルＳ(ＧⅠ)', '阪神ＪＦ(ＧⅠ)', '朝日杯ＦＳ(ＧⅠ)']

age2_G2 = ['京王杯２歳Ｓ(ＧⅡ)', 'デイリー２Ｓ(ＧⅡ)', '東スポ２歳Ｓ(ＧⅡ)']

age2_G3 = ['函館２歳Ｓ(ＧⅢ)', '新潟２歳Ｓ(ＧⅢ)', '札幌２歳Ｓ(ＧⅢ)', '小倉２歳Ｓ(ＧⅢ)', 'サウジＲＣ(ＧⅢ)',\
           'アルテミスＳ(ＧⅢ)', 'ファンタジー(ＧⅢ)', '京都２歳Ｓ(ＧⅢ)']

age2_OP = ['アイビーＳ(Ｌ)', '萩ステークス(Ｌ)', 'すずらん賞(OP)', 'クローバー賞(OP)', 'ききょうＳ(OP)', '野路菊Ｓ(OP)',\
           'カンナＳ(OP)', '芙蓉Ｓ(OP)', 'もみじＳ(OP)', '中京２歳Ｓ(OP)', '福島２歳Ｓ(OP)', 'カトレアＳ(OP)']

age3_G1 = ['皐月賞(ＧⅠ)', '東京優駿(ＧⅠ)', '菊花賞(ＧⅠ)', '桜花賞(ＧⅠ)', '優駿牝馬(ＧⅠ)', '秋華賞(ＧⅠ)',\
           'ＮＨＫマイル(ＧⅠ)', 'ジャパンＤＣ(ＧⅠ)', '東京ダービー(ＧⅠ)']
age3_G2 = ['神戸新聞杯(ＧⅡ)', 'ローズＳ(ＧⅡ)', 'チューリップ(ＧⅡ)', '青葉賞(ＧⅡ)', 'セントライト(ＧⅡ)',\
           'フローラＳ(ＧⅡ)', '京都新聞杯(ＧⅡ)', '	ＮＺＴ(ＧⅡ)', 'スプリングＳ(ＧⅡ)', 'ディープ記念(ＧⅡ)',\
           'Ｆレビュー(ＧⅡ)', '紫苑Ｓ(ＧⅡ)']
age3_G3 = ['フェアリーＳ(ＧⅢ)', '共同通信杯(ＧⅢ)', 'ラジＮＩＫ賞(ＧⅢ)', 'シンザン記念(ＧⅢ)', '毎日杯(ＧⅢ)',\
           'クイーンＣ(ＧⅢ)', 'アーリントン(ＧⅢ)', 'ファルコンＳ(ＧⅢ)', 'きさらぎ賞(ＧⅢ)', '共同通信杯(ＧⅢ)',\
           '京成杯(ＧⅢ)', 'ユニコーンＳ(ＧⅢ)', 'フラワーＣ(ＧⅢ)', 'レパードＳ(ＧⅢ)', '葵ステークス(ＧⅢ)']
age3_OP = ['ジュニアＣ(Ｌ)', '紅梅Ｓ(Ｌ)', '若駒Ｓ(Ｌ)', 'クロッカスＳ(Ｌ)', 'エルフィンＳ(Ｌ)', 'ヒヤシンスＳ(Ｌ)',\
           'すみれＳ(Ｌ)', 'マーガレット(Ｌ)', 'アネモネＳ(Ｌ)', '若葉Ｓ(Ｌ)', '忘れな草賞(Ｌ)', 'スイートピー(Ｌ)',\
           'プリンシパル(Ｌ)', '橘ステークス(Ｌ)', '鳳雛Ｓ(Ｌ)', '白百合Ｓ(Ｌ)','バイオレット(OP)', '青竜Ｓ(OP)',\
           '端午Ｓ(OP)', '昇竜Ｓ(OP)', '伏竜Ｓ(OP)']

age2_Jpn1 = ['全日本２歳優(ＧⅠ)']
age2_Jpn2 = ['兵庫ＪＧＰ(ＧⅡ)']
age2_Jpn3 = ['エーデルワイ(ＧⅢ)', 'ＪＢＣ２歳優(ＧⅢ)', '']

age3_Jpn1 = ['羽田盃(ＧⅠ)', 'ジャパンＤＣ(ＧⅠ)', '東京ダービー(ＧⅠ)']
age3_Jpn2 = ['関東オークス(ＧⅡ)', '不来方賞(ＧⅡ)', '兵庫ＣＳ(ＧⅡ)', '京浜盃(ＧⅡ)', ]
age3_Jpn3 = ['雲取賞(ＧⅢ)', 'ブルーバード(ＧⅢ)', '北海道ＳＣ(ＧⅢ)', 'マリーンＣ(ＧⅢ)']

Jpn1 = ['ＪＢＣスプリ(ＧⅠ)', 'さきたま杯(ＧⅠ)', 'かしわ記念(ＧⅠ)', 'ＪＢＣレディ(ＧⅠ)', '帝王賞(ＧⅠ)',\
        '川崎記念(ＧⅠ)', '東京大賞典(ＧⅠ)', 'ＭＣＳ南部杯(ＧⅠ)', 'ＪＢＣクラシ(ＧⅠ)']
Jpn2 = ['東京盃(ＧⅡ)', 'レディスプレ(ＧⅡ)', 'エンプレス杯(ＧⅡ)', 'ダイオライト(ＧⅡ)', '名古屋ＧＰ(ＧⅡ)',\
        '日本テレビ盃(ＧⅡ)', '浦和記念(ＧⅡ)', '']
Jpn3 = ['黒船賞(ＧⅢ)', 'かきつばた記(ＧⅢ)', '東京スプリン(ＧⅢ)', 'クラスターＣ(ＧⅢ)', 'サマーチャン(ＧⅢ)',\
        'オーバルスプ(ＧⅢ)', '兵庫ＧＴ(ＧⅢ)', '佐賀記念(ＧⅢ)', 'スパーキング(ＧⅢ)', '兵庫女王盃(ＧⅢ)',\
        'クイーン賞(ＧⅢ)', 'マーキュリＣ(ＧⅢ)', 'ブリーダーズ(ＧⅢ)', '白山大賞典(ＧⅢ)', '名古屋大賞典(ＧⅢ)']

Obs_G1 = ['中山ＧＪ(ＧⅠ)', '中山大障害(ＧⅠ)']

Obs_G2 = ['東京ハイＪ(ＧⅡ)', '阪神スプリＪ(ＧⅡ)', '京都ハイＪ(ＧⅡ)']

Obs_G3 = ['東京ジャンプ(ＧⅢ)', '阪神ジャンプ(ＧⅢ)', '京都ジャンプ(ＧⅢ)', '新潟ジャンプ(ＧⅢ)', '小倉サマーＪ(ＧⅢ)']

Obs_OP = ['ペガサスＪＳ(OP)', '春麗ジャンプ(OP)', 'イルミネＪＳ(OP)', '清秋ジャンプ(OP)', '清秋ジャンプ(OP)',\
          '中山新春ＪＳ(OP)', '秋陽ジャンプ(OP)', '三木ホースＪ(OP)', '牛若丸ＪＳ(OP)']

# 競馬ラボにアクセスできるようにするコード
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


st.title('テキトー指数研究所＠WEB')
st.header('JRA版')
st.subheader('めでたく復活version')

st.write('   ')
#st.info('【南関東版】\https://azzukky-n24.streamlit.app/')
#st.info('【地方交流版】\https://azzukky-k24.streamlit.app/')
st.write('   ')
st.write('   ')
st.write('クラスが上がるほど、良く当たる傾向があります。')
st.write('３歳戦はあまりあてになりません。')
st.write('過去３走していない馬の指数はゼロになります。')
st.write('   ')
st.write('   ')

# 開催場所を数字に変換
basho = st.radio('開催場所？', ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉'])

if basho == '札幌':
    place = "01"
elif basho == '函館':
    place = "02"
elif basho == '福島':
    place = "03"
elif basho == '新潟':
    place = "04"
elif basho == '東京':
    place = "05"
elif basho == '中山':
    place = "06"
elif basho == '中京':
    place = "07"
elif basho == '京都':
    place = "08"
elif basho == '阪神':
    place = "09"
elif basho == '小倉':
    place = "10"
else:
    place = "0"

# タイムゾーンを指定して、年月日を作成
utc_time = dt.now(timezone('Asia/Tokyo'))
kotoshi = utc_time.year

jst_date_today = utc_time.strftime('%Y%m%d')
jst_time_tomorrow = utc_time + td(days = 1)
jst_date_tomorrow = jst_time_tomorrow.strftime('%Y%m%d')

yosoubi = st.radio('いつのレース？', ['今日', '明日', '日付入力'])

if yosoubi == '今日':
    nengappi = jst_date_today
elif yosoubi == '明日':
    nengappi = jst_date_tomorrow
elif yosoubi == '日付入力':
    nengappi = str(kotoshi) + st.text_input('レースの日付を入力：例0628')

# レース番号を入力
race = st.number_input('【半角数字】レース番号？', 1, 12, 11)

# 指数を計算するレースのURLを取得
url = 'https://www.keibalab.jp/db/race/' + nengappi + place + str(str(race).zfill(2)) + '/syutsuba.html'


st.write('   ')
st.write('計算するときはチェックボックスをチェック！')
st.write('次のレースを計算する前にチェックを外す！')

push = st.checkbox('チェック！！')

if push == True:
    
    st.write('計算には約1分かかります。しばらくお待ちください。')

    html = requests.get(url, headers = headers) #出走表を競馬ラボから取得
    html.encoding = 'UTF-8'
    shutsubahyo = pd.read_html(StringIO(html.text))
    df_s = shutsubahyo[0]
    df_s['性'] = df_s['性齢'].str[0]
    df_s['齢'] = df_s['性齢'].str[1:].astype(int)
    df_s['馬番'] = df_s['馬']
    df_s.drop(['マイ印', 'α', 'β', 'Ω', 'Ω指数', '血統', '性齢', '馬'], axis = 1, inplace = True)
    
    soup = BeautifulSoup(html.text, "html.parser")
    
    horse_id_list = [] #競馬ラボの馬IDを使って出走馬のリストを作成
    for horse_id in soup.find_all('a', href=True):
        match = re.search(r'/db/horse/(20\d+)/', horse_id['href'])
        if match:
            horse_id_list.append(match.group(1))
    
    L2 = [] #出走馬の斤量リストを作成
    for weight in df_s['斤量']:
        L2.append(str(weight))
    
    L3 = [] #出走馬の性別リストを作成
    for sei in df_s['性']:
        L3.append(sei)
    
    L4 = [] #出走馬の年齢リストを作成
    for rei in df_s['齢']:
        L4.append(str(rei))
    
    #出走馬のIDと斤量、性別、年齢を結合したリストを作成
    syusso_list = [x1 + ' ' + x2 +  ' ' + x3 + ' ' + x4  for (x1, x2, x3, x4) in zip(horse_id_list, L2, L3, L4)]
    
    #指数を計算するレース名を取得
    today_race = soup.find('h1', class_="raceTitle fL").get_text().replace('\n', '').replace('\t', '')
    
    #指数を計算するレース日を取得
    racedate1 = nengappi
    racedate2 = dt.strptime(racedate1, "%Y%m%d")
    racedate2 = racedate2.date() #指数を計算するレースの日付
    
    #指数を計算するレース番号を取得
    racenumber = str(str(race).zfill(2)) + 'R'
    
    race_kind = soup.find('ul', class_ = "classCourseSyokin clearfix").get_text()
    race_kind = re.findall('障.*m', race_kind) or re.findall('芝.*m', race_kind) or re.findall('ダ.*m', race_kind)
    race_distance = "".join(race_kind)[1:5]
    race_distance = int(race_distance) #指数を計算するレースの距離
    race_course = "".join(race_kind)[0] #指数を計算するレースの種類
    
    
    #出走馬の過去成績を取得し、不要なレースを削除
    horse_results = {}                       
    for horse_id2 in syusso_list:
        url2 = 'https://www.keibalab.jp/db/horse/' + horse_id2[:10] + '/'
        html2 = requests.get(url2, headers = headers)
        html2.encoding = 'UTF-8'
        horse_results[horse_id2] = pd.read_html(StringIO(html2.text))[2].head(30)
        horse_results[horse_id2] = horse_results[horse_id2][horse_results[horse_id2].index % 2 == 0]
        horse_results[horse_id2]['course'] = horse_results[horse_id2]['コース'].str[0] #過去レースの芝、ダ、障を分類
        horse_results[horse_id2]['distance'] = horse_results[horse_id2]['コース'].str[1:].astype(int) #過去レースの距離
        string_to_remove = '香港|ア首|オー|アメ|韓国|サウ' #海外レースを除去
        horse_results[horse_id2] = horse_results[horse_id2][~horse_results[horse_id2]['場'].str.contains(string_to_remove, na=False)]
        horse_results[horse_id2] = horse_results[horse_id2][(horse_results[horse_id2]['着 差'] < 3.6)] #着差3.6秒以上を除去
        horse_results[horse_id2]['past_date'] = pd.to_datetime(horse_results[horse_id2]['年月日']).dt.date #過去レースの日付
        horse_results[horse_id2]['place'] = horse_results[horse_id2]['場'].str.replace(r"\d+回", "", regex=True)
        horse_results[horse_id2]['place'] = horse_results[horse_id2]['place'].str.replace(r"\d+", "", regex=True) #過去レースの場所
        horse_results[horse_id2]['racename'] = horse_results[horse_id2]['レース'] #過去レースの名前
        horse_results[horse_id2]['pastweight'] = horse_results[horse_id2]['斤量'] #過去レースの斤量
        horse_results[horse_id2]['difference'] = horse_results[horse_id2]['着 差'] #過去レースの着差
        horse_results[horse_id2]['result'] = horse_results[horse_id2]['着'].astype(int) #過去レースの着順   
        horse_results[horse_id2] = horse_results[horse_id2].drop(columns = ['着 差', '斤量', '年月日', 'レース', '場', 'コース', '天 気', '馬 場', '人 気', '着', '騎手', '頭 数', '枠 番', '馬 番', 'タイム', 'ペース', '上り', 'B', '馬体重', '通過順位', '勝ち馬 (2着馬)'])
        horse_results[horse_id2] = horse_results[horse_id2].reset_index()
        horse_results[horse_id2] = horse_results[horse_id2].drop(columns = ['index'])
        time.sleep(1)
    
    past_results = copy.deepcopy(horse_results)
    syusso_hyo = copy.deepcopy(df_s)
    npr = past_results
    
    
    #テキトー指数を計算
    tekito_shisu_list = []
    for horse in syusso_list:
    
        if len(npr[horse]) < 3:
            tekito_shisu = 0
            tekito_shisu_list.append(tekito_shisu)
    
    #3歳春、3戦のみ
        elif len(npr[horse]) == 3:
            if int(horse[18:]) == 3 and racedate2 <= date(kotoshi, 5, 31):
    
                base_number = []
                for t in range(3):
    
                    if npr[horse].iloc[t]['racename'] in age3_G1: #3歳春のJRA GI
                        kijun = 500
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn1: #3歳春のJpnI
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G1:  #2歳秋のJRA GI
                        kijun = 350
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn1:  #2歳秋のJpnI
                        kijun = 300
    
                    elif npr[horse].iloc[t]['racename'] in age3_G2: #3歳春のJRA GII
                        kijun = 430
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn2:  #3歳春のJpnII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age2_G2: #2歳秋のJRA GII
                        kijun = 300
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn2:  #2歳秋のJpnII
                        kijun = 270                    
    
                    elif npr[horse].iloc[t]['racename'] in age3_G3: #3歳春のJRA GIII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn3:  #3歳春のJpnIII
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G3: #2歳秋のJRA GIII
                        kijun = 270
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn3:  #2歳秋のJpnIII
                        kijun = 250
                    
                    elif npr[horse].iloc[t]['racename'] in age3_OP: ##3歳春のOP
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_OP:  #2歳秋のOP
                        kijun = 250
    
                    elif '2勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 400                
                    elif '1勝' in npr[horse].iloc[t]['racename']: #3歳春の1勝クラス
                        kijun = 300                  
                    
                    else:
                        kijun = 200
                        
                    base_number.append(kijun)
    
                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]
    
    #3歳夏以降、3戦のみ
            elif int(horse[18:]) == 3 and race_date >= date(kotoshi, 6, 1):
    
                base_number = []
                for t in range(3):
    
                    if npr[horse].iloc[t]['racename'] in age3_G1: #3歳春のJRA GI
                        kijun = 500
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn1: #3歳春のJpnI
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G1:  #2歳秋のJRA GI
                        kijun = 350
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn1:  #2歳秋のJpnI
                        kijun = 300
    
                    elif npr[horse].iloc[t]['racename'] in age3_G2: #3歳春のJRA GII
                        kijun = 430
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn2:  #3歳春のJpnII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age2_G2: #2歳秋のJRA GII
                        kijun = 300
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn2:  #2歳秋のJpnII
                        kijun = 270                    
    
                    elif npr[horse].iloc[t]['racename'] in age3_G3: #3歳春のJRA GIII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn3:  #3歳春のJpnIII
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G3: #2歳秋のJRA GIII
                        kijun = 270
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn3:  #2歳秋のJpnIII
                        kijun = 250
                    
                    elif npr[horse].iloc[t]['racename'] in age3_OP: ##3歳春のOP
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_OP:  #2歳秋のOP
                        kijun = 250
    
                    elif '3勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 500   
                    elif '2勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 400                
                    elif '1勝' in npr[horse].iloc[t]['racename']: #3歳春の1勝クラス
                        kijun = 300                  
                    
                    else:
                        kijun = 200
                        
                    base_number.append(kijun)
    
                kijun1, kijun2, kijun3 = base_number[0], base_number[1], base_number[2]         
    
    #3歳夏以降、3戦のみ        
            else:        
                base_number = []
                for t in range(3):                
    
                    if npr[horse].iloc[t]['place'] in jra and 'ＧⅠ' in npr[horse].iloc[t]['racename']: #G1 
                        kijun = 800
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅠ' in npr[horse].iloc[t]['racename']: #Jpn1 
                        kijun = 700             
                    elif npr[horse].iloc[t]['place'] in jra and 'ＧⅡ' in npr[horse].iloc[t]['racename']: #G2
                        kijun = 700
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅡ' in npr[horse].iloc[t]['racename']: #Jpn2
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and 'ＧⅢ' in npr[horse].iloc[t]['racename']: #G3
                        kijun = 650
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅢ' in npr[horse].iloc[t]['racename']: #Jpn3
                        kijun = 500
                    elif npr[horse].iloc[t]['place'] in jra and 'Ｌ' in npr[horse].iloc[t]['racename']:
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename']:
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                        kijun = 500
                    elif npr[horse].iloc[t]['place'] in jra and '2勝'in npr[horse].iloc[t]['racename']:
                        kijun = 400
                    elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                        kijun = 300  
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
            if npr[horse].iloc[0]['result'] == 1 and npr[horse].iloc[1]['result'] == 1 and npr[horse].iloc[2]['result'] == 1:
                rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']) / 3
                if rensho < -0.7:
                    e = 1.25
                elif -0.7 <= rensho < -0.5:
                    e = 1.20  
                elif -0.5 <= rensho < -0.3:
                    e = 1.15
                else:
                    e = 1.10
            elif npr[horse].iloc[0]['result'] == 1 and npr[horse].iloc[1]['result'] == 1:
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
                    f = kijun1 * 0.15 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(df_s['斤量']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.1166 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.1166 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.1166 * (max(df_s['斤量']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.0833 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.0833 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.0833 * (max(df_s['斤量']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(df_s['斤量']) - float(horse[11:15])) 
    
    
    
            #休養係数
            if td(weeks = 0) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (racedate2 - npr[horse].iloc[0]['past_date']):
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
    
    
    
            ts = ((kijun1 * 2.4 * a * 1.1 + kijun2 * b + kijun3 * c * 1.0) + f) * e * g * h * i
            tekito_shisu = int(ts)
            tekito_shisu_list.append(tekito_shisu)
    
    #4戦以上
        else:
    #3歳春、4戦以上
            if int(horse[18:]) == 3 and racedate2 <= date(kotoshi, 5, 31):
                base_number = []
                for t in range(4):
    
                    if npr[horse].iloc[t]['racename'] in age3_G1: #3歳春のJRA GI
                        kijun = 500
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn1: #3歳春のJpnI
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G1:  #2歳秋のJRA GI
                        kijun = 350
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn1:  #2歳秋のJpnI
                        kijun = 300
    
                    elif npr[horse].iloc[t]['racename'] in age3_G2: #3歳春のJRA GII
                        kijun = 430
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn2:  #3歳春のJpnII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age2_G2: #2歳秋のJRA GII
                        kijun = 300
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn2:  #2歳秋のJpnII
                        kijun = 270                    
    
                    elif npr[horse].iloc[t]['racename'] in age3_G3: #3歳春のJRA GIII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn3:  #3歳春のJpnIII
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G3: #2歳秋のJRA GIII
                        kijun = 270
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn3:  #2歳秋のJpnIII
                        kijun = 250
                    
                    elif npr[horse].iloc[t]['racename'] in age3_OP: ##3歳春のOP
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_OP:  #2歳秋のOP
                        kijun = 250
    
                    elif '2勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 400                
                    elif '1勝' in npr[horse].iloc[t]['racename']: #3歳春の1勝クラス
                        kijun = 300                  
                    
                    else:
                        kijun = 200
                        
                    base_number.append(kijun)
    
                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]             
                
    #3歳夏以降、4戦以上
            elif int(horse[18:]) == 3 and racedate2 >= date(kotoshi, 6, 1):
    
                base_number = []
                for t in range(4):
    
                    if npr[horse].iloc[t]['racename'] in age3_G1: #3歳春のJRA GI
                        kijun = 500
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn1: #3歳春のJpnI
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G1:  #2歳秋のJRA GI
                        kijun = 350
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn1:  #2歳秋のJpnI
                        kijun = 300
    
                    elif npr[horse].iloc[t]['racename'] in age3_G2: #3歳春のJRA GII
                        kijun = 430
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn2:  #3歳春のJpnII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age2_G2: #2歳秋のJRA GII
                        kijun = 300
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn2:  #2歳秋のJpnII
                        kijun = 270                    
    
                    elif npr[horse].iloc[t]['racename'] in age3_G3: #3歳春のJRA GIII
                        kijun = 415
                    elif npr[horse].iloc[t]['racename'] in age3_Jpn3:  #3歳春のJpnIII
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_G3: #2歳秋のJRA GIII
                        kijun = 270
                    elif npr[horse].iloc[t]['racename'] in age2_Jpn3:  #2歳秋のJpnIII
                        kijun = 250
                    
                    elif npr[horse].iloc[t]['racename'] in age3_OP: ##3歳春のOP
                        kijun = 400
                    elif npr[horse].iloc[t]['racename'] in age2_OP:  #2歳秋のOP
                        kijun = 250
    
                    elif '3勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 500   
                    elif '2勝' in npr[horse].iloc[t]['racename']: #3歳春の2勝クラス
                        kijun = 400                
                    elif '1勝' in npr[horse].iloc[t]['racename']: #3歳春の1勝クラス
                        kijun = 300                  
                    
                    else:
                        kijun = 200
                        
                    base_number.append(kijun)
    
                kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]
    
    #古馬混合戦の指数
            else:
                base_number = []
                for t in range(4):
    
                    if npr[horse].iloc[t]['racename'] in Obs_G1: #障害G1
                        kijun = 800
                    elif npr[horse].iloc[t]['racename'] in Obs_G2: #障害G2
                        kijun = 700
                    elif npr[horse].iloc[t]['racename'] in Obs_G3: #障害G3
                        kijun = 600                
                    elif npr[horse].iloc[t]['racename'] in Obs_OP: #障害OP
                        kijun = 500                
                    elif npr[horse].iloc[t]['course'] == '障' and '未勝利' in npr.iloc[t]['racename']: #障害未勝利
                        kijun = 400      
    
                    if npr[horse].iloc[t]['place'] in jra and 'ＧⅠ' in npr[horse].iloc[t]['racename']: #G1 
                        kijun = 800
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅠ' in npr[horse].iloc[t]['racename']: #Jpn1 
                        kijun = 700             
                    elif npr[horse].iloc[t]['place'] in jra and 'ＧⅡ' in npr[horse].iloc[t]['racename']: #G2
                        kijun = 700
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅡ' in npr[horse].iloc[t]['racename']: #Jpn2
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and 'ＧⅢ' in npr[horse].iloc[t]['racename']: #G3
                        kijun = 650
                    elif npr[horse].iloc[t]['place'] not in jra and 'ＧⅢ' in npr[horse].iloc[t]['racename']: #Jpn3
                        kijun = 500
                    elif npr[horse].iloc[t]['place'] in jra and 'Ｌ' in npr[horse].iloc[t]['racename']:
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and 'OP' in npr[horse].iloc[t]['racename']:
                        kijun = 600
                    elif npr[horse].iloc[t]['place'] in jra and '3勝' in npr[horse].iloc[t]['racename']:
                        kijun = 500
                    elif npr[horse].iloc[t]['place'] in jra and '2勝'in npr[horse].iloc[t]['racename']:
                        kijun = 400
                    elif npr[horse].iloc[t]['place'] in jra and '1勝' in npr[horse].iloc[t]['racename']:
                        kijun = 300  
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
            if npr[horse].iloc[0]['result'] == 1 and npr[horse].iloc[1]['result'] == 1 and npr[horse].iloc[2]['result'] == 1\
            and npr[horse].iloc[3]['result'] == 1:
                rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']\
                          + npr[horse].iloc[3]['difference']) / 4
                if rensho < -0.7:
                    e = 1.35
                elif -0.7 <= rensho < -0.5:
                    e = 1.30   
                elif -0.5 <= rensho < -0.3:
                    e = 1.25
                else:
                    e = 1.20
            elif npr[horse].iloc[0]['result'] == 1 and npr[horse].iloc[1]['result'] == 1 and npr[horse].iloc[2]['result'] == 1:
                rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']\
                          + npr[horse].iloc[3]['difference']) / 4
                if rensho < -0.7:
                    e = 1.25
                elif -0.7 <= rensho < -0.5:
                    e = 1.20
                elif -0.5 <= rensho < -0.3:
                    e = 1.15
                else:
                    e = 1.10
            elif npr[horse].iloc[0]['result'] == 1 and npr[horse].iloc[1]['result'] == 1: #2連勝
                rensho = (npr[horse].iloc[0]['difference'] + npr[horse].iloc[1]['difference'] + npr[horse].iloc[2]['difference']\
                          + npr.iloc[3]['difference']) / 4
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
                    f = kijun1 * 0.15 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.15 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.15 * (max(df_s['斤量']) - float(horse[11:15]))                
            elif 1400 < race_distance <= 1800:
                if all(L3) =='牝':
                    f = kijun1 * 0.1166 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.1166 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.1166 * (max(df_s['斤量']) - float(horse[11:15]))                            
            elif 1800 < race_distance <= 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.0833 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.0833 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.0833 * (max(df_s['斤量']) - float(horse[11:15]))            
            elif race_distance > 2400:
                if all(L3) =='牝':
                    f = kijun1 * 0.05 * (max(df_s['斤量']) - float(horse[11:15]))
                else:
                    if '牝' in horse:
                        f = kijun1 * 0.05 * (max(df_s['斤量']) -2.0 - float(horse[11:15]))
                    else:
                        f = kijun1 * 0.05 * (max(df_s['斤量']) - float(horse[11:15]))                              
    
    
            #休養係数
            if td(weeks = 0) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 4):
                g = 0.95
            elif td(weeks = 4) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 16):
                g = 1.0
            elif td(weeks = 16) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 36):
                g = 0.9
            elif td(weeks = 36) < (racedate2 - npr[horse].iloc[0]['past_date']) <= td(weeks = 48):
                g = 0.85                
            elif td(weeks = 48) < (racedate2 - npr[horse].iloc[0]['past_date']):
                g = 0.8
            else:
                g = 1.0
    
            #距離係数                
            av_dist = (npr[horse].iloc[0]['distance'] + npr[horse].iloc[1]['distance']\
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
    
    #指数計算結果を出走表に追加
    syusso_hyo['指数'] = tekito_shisu_list
    
    #前走の斤量リストを作成
    past_weight_list = []
    for horse in syusso_list:
        pw = npr[horse]['pastweight'][0] 
        past_weight_list.append(pw)
    
    #今走と前走の斤量差を計算し、出走表に追加
    gap = pd.Series(past_weight_list)
    syusso_hyo['斤量増減']= syusso_hyo['斤量']-gap
    
    #生産者とオーナーのリストを作成し、出走表に追加
    breeder_list = []
    owner_list = []
    for uma_b in horse_id_list:
        time.sleep(1)
        url_b = 'https://www.keibalab.jp/db/horse/' + uma_b
        html3 = requests.get(url_b, headers = headers)
        html3.encoding = 'UTF-8'
        owner_breeder = pd.read_html(StringIO(html3.text))[0]
        breeder = owner_breeder[1][4]
        owner = owner_breeder[1][3]
        breeder_list.append(breeder)
        owner_list.append(owner)
    
    syusso_hyo['馬主'] = owner_list
    syusso_hyo['生産者'] = breeder_list
    
    
    #騎手補正：三着内率＝X、50≦X＜60は1.30, 40≦X＜50は1.20, 30≦X＜40は1.10, 20≦X＜30は1.00, 10≦X＜20は0.90, 0≦X＜10は0.80
    
    #三着内率50%以上
    syusso_hyo.loc[syusso_hyo['騎手'] == 'ルメー', '指数'] = round(syusso_hyo['指数'] * 1.30)
    syusso_hyo.loc[syusso_hyo['騎手'] == '川田将', '指数'] = round(syusso_hyo['指数'] * 1.30)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'モレイ', '指数'] = round(syusso_hyo['指数'] * 1.30)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '森一馬', '指数'] = round(syusso_hyo['指数'] * 1.30)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '小牧加', '指数'] = round(syusso_hyo['指数'] * 1.30)  
    syusso_hyo.loc[syusso_hyo['騎手'] == 'Cデム', '指数'] = round(syusso_hyo['指数'] * 1.30)
    
    syusso_hyo.loc[syusso_hyo['騎手'] == 'マーフ', '指数'] = round(syusso_hyo['指数'] * 1.30)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'レーン', '指数'] = round(syusso_hyo['指数'] * 1.30)
    
    
    #三着内率40-50%
    syusso_hyo.loc[syusso_hyo['騎手'] == '西谷誠', '指数'] = round(syusso_hyo['指数'] * 1.20)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '戸崎圭', '指数'] = round(syusso_hyo['指数'] * 1.20)
    syusso_hyo.loc[syusso_hyo['騎手'] == '坂井瑠', '指数'] = round(syusso_hyo['指数'] * 1.20)   
    syusso_hyo.loc[syusso_hyo['騎手'] == 'ムーア', '指数'] = round(syusso_hyo['指数'] * 1.20)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'ビュイ', '指数'] = round(syusso_hyo['指数'] * 1.20)
    
    #三着内率30-40%
    syusso_hyo.loc[syusso_hyo['騎手'] == '高田潤', '指数'] = round(syusso_hyo['指数'] * 1.10) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '武豊', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '松山弘', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '小坂忠', '指数'] = round(syusso_hyo['指数'] * 1.10)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '横山武', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'マーカ', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '上野翔', '指数'] = round(syusso_hyo['指数'] * 1.10)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '岩田望', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '鮫島克', '指数'] = round(syusso_hyo['指数'] * 1.10)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '藤岡佑', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '三浦皇', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'Mデム', '指数'] = round(syusso_hyo['指数'] * 1.10)
    
    #三着内率20-30%
    syusso_hyo.loc[syusso_hyo['騎手'] == '石神深', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '佐々木', '指数'] = round(syusso_hyo['指数'] * 1.00)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '田辺裕', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '北村友', '指数'] = round(syusso_hyo['指数'] * 1.00)                   
    syusso_hyo.loc[syusso_hyo['騎手'] == '五十嵐', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '菅原明', '指数'] = round(syusso_hyo['指数'] * 1.00)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '西村淳', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '大江原', '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['騎手'] == '丹内祐', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '池添謙', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '横山典', '指数'] = round(syusso_hyo['指数'] * 1.00)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '浜中俊', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '団野大', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '横山和', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '金子光', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '津村明', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '伴啓太', '指数'] = round(syusso_hyo['指数'] * 1.00)  
    syusso_hyo.loc[syusso_hyo['騎手'] == '坂口智', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '岩田康', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '中村将', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '田村太', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '斎藤新', '指数'] = round(syusso_hyo['指数'] * 1.00) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '西塚洸', '指数'] = round(syusso_hyo['指数'] * 1.00) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '和田竜', '指数'] = round(syusso_hyo['指数'] * 1.00)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '高杉吏', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '石川裕', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '菱田裕', '指数'] = round(syusso_hyo['指数'] * 1.00)
    syusso_hyo.loc[syusso_hyo['騎手'] == '北村宏', '指数'] = round(syusso_hyo['指数'] * 1.00)
    
    #三着内率10-20%
    syusso_hyo.loc[syusso_hyo['騎手'] == '水口優', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '大野拓', '指数'] = round(syusso_hyo['指数'] * 0.90) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '吉村誠', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '荻野極', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '江田勇', '指数'] = round(syusso_hyo['指数'] * 0.90)  
    syusso_hyo.loc[syusso_hyo['騎手'] == '幸英明', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '吉田隼', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '田口貫', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '吉田豊', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '菊沢一', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '亀田温', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '丸山元', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '石橋脩', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '藤懸貴', '指数'] = round(syusso_hyo['指数'] * 0.90)      
    syusso_hyo.loc[syusso_hyo['騎手'] == '柴田善', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '国分恭', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '草野太', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '川又賢', '指数'] = round(syusso_hyo['指数'] * 0.90)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '角田和', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '秋山稔', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '松若風', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '中井裕', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '黒岩悠', '指数'] = round(syusso_hyo['指数'] * 0.90) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '難波剛', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '岡田祥', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '小林美', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '酒井学', '指数'] = round(syusso_hyo['指数'] * 0.90)      
    syusso_hyo.loc[syusso_hyo['騎手'] == '長浜鴻', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '杉原誠', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '松岡正', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '横山琉', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '柴田裕', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '小沢大', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '荻野琢', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '原優介', '指数'] = round(syusso_hyo['指数'] * 0.90)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '長岡禎', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '木幡初', '指数'] = round(syusso_hyo['指数'] * 0.90)  
    syusso_hyo.loc[syusso_hyo['騎手'] == '永島ま', '指数'] = round(syusso_hyo['指数'] * 0.90)  
    syusso_hyo.loc[syusso_hyo['騎手'] == '小林勝', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == 'ドイル', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '太宰啓', '指数'] = round(syusso_hyo['指数'] * 0.90)  
    syusso_hyo.loc[syusso_hyo['騎手'] == '鮫島良', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '松本大', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '武藤雅', '指数'] = round(syusso_hyo['指数'] * 0.90)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '富田暁', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '木幡巧', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '井上敏', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '加藤祥', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '小崎綾', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '川端海', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '蓑島靖', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '古川吉', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '丸田恭', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '野中悠', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '内田博', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '嶋田純', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '木幡育', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '黛弘人', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '今村聖', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '泉谷楓', '指数'] = round(syusso_hyo['指数'] * 0.90)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '小林脩', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '古川奈', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '国分優', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '鷲頭虎', '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['騎手'] == '宮崎北', '指数'] = round(syusso_hyo['指数'] * 0.90) 
    
    #三着内率10%以下
    syusso_hyo.loc[syusso_hyo['騎手'] == '小野寺', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '白浜雄', '指数'] = round(syusso_hyo['指数'] * 0.80)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '川須栄', '指数'] = round(syusso_hyo['指数'] * 0.80)   
    syusso_hyo.loc[syusso_hyo['騎手'] == '高倉稜', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '伊藤工', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '柴田大', '指数'] = round(syusso_hyo['指数'] * 0.80)    
    syusso_hyo.loc[syusso_hyo['騎手'] == '森裕太', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '田中健', '指数'] = round(syusso_hyo['指数'] * 0.80) 
    syusso_hyo.loc[syusso_hyo['騎手'] == '大久保', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '江田照', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '城戸義', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '小林凌', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '土田真', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '岩部純', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '的場勇', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '水沼元', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '原田和', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '和田翼', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '菅原隆', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '鈴木祐', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '大塚海', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '佐藤翔', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '橋木太', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '河原田', '指数'] = round(syusso_hyo['指数'] * 0.80)
    syusso_hyo.loc[syusso_hyo['騎手'] == '石田拓', '指数'] = round(syusso_hyo['指数'] * 0.80)
    
    
    #前走からの斤量増減補正
    
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -6.0, '指数'] = round(syusso_hyo['指数'] * 1.20)    
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -5.5, '指数'] = round(syusso_hyo['指数'] * 1.18)    
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -5.0, '指数'] = round(syusso_hyo['指数'] * 1.16)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -4.5, '指数'] = round(syusso_hyo['指数'] * 1.14)    
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -4.0, '指数'] = round(syusso_hyo['指数'] * 1.12)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -3.5, '指数'] = round(syusso_hyo['指数'] * 1.10)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -3.0, '指数'] = round(syusso_hyo['指数'] * 1.08) 
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -2.5, '指数'] = round(syusso_hyo['指数'] * 1.06) 
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -2.0, '指数'] = round(syusso_hyo['指数'] * 1.04) 
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -1.5, '指数'] = round(syusso_hyo['指数'] * 1.02)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -1.0, '指数'] = round(syusso_hyo['指数'] * 1.0)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == -0.5, '指数'] = round(syusso_hyo['指数'] * 1.0)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 0.0, '指数'] = round(syusso_hyo['指数'] * 1.0)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 0.5, '指数'] = round(syusso_hyo['指数'] * 1.0)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 1.0, '指数'] = round(syusso_hyo['指数'] * 1.0)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 1.5, '指数'] = round(syusso_hyo['指数'] * 0.98)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 2.0, '指数'] = round(syusso_hyo['指数'] * 0.96)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 2.5, '指数'] = round(syusso_hyo['指数'] * 0.94)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 3.0, '指数'] = round(syusso_hyo['指数'] * 0.92)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 3.5, '指数'] = round(syusso_hyo['指数'] * 0.90)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 4.0, '指数'] = round(syusso_hyo['指数'] * 0.88)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 4.5, '指数'] = round(syusso_hyo['指数'] * 0.86)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 5.0, '指数'] = round(syusso_hyo['指数'] * 0.84)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 5.5, '指数'] = round(syusso_hyo['指数'] * 0.82)
    syusso_hyo.loc[syusso_hyo['斤量増減'] == 6.0, '指数'] = round(syusso_hyo['指数'] * 0.80)   
    
    #馬主補正
    syusso_hyo.loc[syusso_hyo['馬主'].str.contains('シルクレ', na=False), '指数'] = round(syusso_hyo['指数'] * 1.05)
    syusso_hyo.loc[syusso_hyo['馬主'].str.contains('サンデー', na=False), '指数'] = round(syusso_hyo['指数'] * 1.05)
    syusso_hyo.loc[syusso_hyo['馬主'].str.contains('キャロッ', na=False), '指数'] = round(syusso_hyo['指数'] * 1.05)
    syusso_hyo.loc[syusso_hyo['馬主'].str.contains('ゴドルフ', na=False), '指数'] = round(syusso_hyo['指数'] * 1.03)
    
    #馬主補正
    syusso_hyo.loc[syusso_hyo['生産者'].str.contains('ノーザン', na=False), '指数'] = round(syusso_hyo['指数'] * 1.05)
    syusso_hyo.loc[syusso_hyo['生産者'].str.contains('社台', na=False), '指数'] = round(syusso_hyo['指数'] * 1.05)
    
    #偏差値計算
    final_shisu = syusso_hyo['指数'].to_list()
    ave = np.average(final_shisu)
    std = np.std(final_shisu)
    
    deviation = []
    for i in final_shisu:
      deviation_value = '{:.1f}'.format(float((i - ave) / std * 10 + 50), 1)
      deviation.append(deviation_value)
    
    #偏差値を出走表に追加
    syusso_hyo['偏差値'] = deviation
    
    #指数順位を出走表に追加
    syusso_hyo['順位'] = syusso_hyo['指数'].rank(ascending=False).astype(int)
    
    #出走表を必要な要素のみに簡素化
    syusso_hyo_final = syusso_hyo[['順位','馬番','馬名', '騎手', '指数','偏差値']]
    
    #出走表を順位で並べ替え
    syusso_hyo_final = syusso_hyo_final.sort_values('順位')

    #出走表を表示
    st.write(racedate2, racenumber, today_race)
    st.dataframe(syusso_hyo_final)
    
else:
    st.write("・・・・・・・")

