#!/usr/bin/env python
# coding: utf-8

# In[5]:




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


st.title('テキトー指数研究所＠WEB')
st.header('南関東限定版')

st.write('   ')
st.info('【参考】テキトー指数の使い方  \nhttps://note.com/tekito_lab/n/n3342d6531772')
st.info('【参考】南関東競馬の賞金理論  \nhttps://note.com/tekito_lab/n/n9583c0fa9d75')

st.write('   ')
st.write('   ')
st.write('●クラスが上がるほど、良く当たる傾向があります。')
st.write('●３歳戦はあまりあてになりません。')
st.write('●過去３走していない馬の指数はゼロになります。')
st.write('●中央からの転入馬の指数は大きくなりますので、指数よりも状態と騎手を重視してください。')
st.write('●私も原因がつかめないエラーが出るときもあります。')
st.write('   ')
st.write('   ')



utc_time = dt.now(timezone.utc)
jst_time_today = utc_time.astimezone(timezone(td(hours=+9)))
jst_date_today = jst_time_today.strftime('%Y%m%d')
jst_time_tomorrow = jst_time_today + td(days = 1)
jst_date_tomorrow = jst_time_tomorrow.strftime('%Y%m%d')
kotoshi = jst_time_today.year

yosoubi = st.radio('いつのレース？', ['今日', '明日', '日付入力'])

if yosoubi == '今日':
    nengappi = jst_date_today
elif yosoubi == '明日':
    nengappi = jst_date_tomorrow
elif yosoubi == '日付入力':
    nengappi = str(kotoshi) + st.text_input('レースの日付を入力：例0628')

basho = st.radio('開催場所？', ['大井', '船橋', '川崎', '浦和'])

if basho == '大井':
    place = "2015"
elif basho == '船橋':
    place = "1914"
elif basho == '川崎':
    place = "2135"
elif basho == '浦和':
    place = "1813"
else:
    place = "0"    

race = st.number_input('【半角数字】レース番号？', 1, 12, 11)

race_for_keisan = nengappi + place + '00' + '00' + str(str(race).zfill(2))




push = st.button('計算！')

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
        trainer_list = []
        for uma2 in profile:
            uma2_text = uma2.text
            weight = re.findall(r'\S\S+', uma2_text)[2]
            weight_list.append(weight)
            sei = re.findall(r'\S\S+', uma2_text)[0][0]
            gender_list.append(sei)
            rei = re.findall(r'\S\S+', uma2_text)[0][1:]
            age_list.append(rei)        
            trainerX = re.findall(r'\D\D+', uma2_text)[4]
            trainer = ''.join(trainerX.split())[2:]
            trainer_list.append(trainer)
            
            
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
        horse_results[horse_id] = pd.read_html(url2)[1].head(10)

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

        df.drop(['馬場天候', '馬番', '人気', '上3F', 'R', '馬体重', '負担重量', '調教師', 'レース名', '距離', '着順', '日付', '差', '騎手'], axis = 1, inplace = True)

        df = df.loc[:, ['日付2', '競馬場', 'レース名2', 'コース', '距離2', '着順2', '差2', 'タイム']].dropna()
        df = df[(df['差2'] < 4.0)]
        df = df[(df['競馬場'] != '外国')]
        df.reset_index(inplace=True, drop=True)

        processed_horse_results[horse_id] = df

    horse_syokin_list = []
    for horse_id in horse_id_list:
        time.sleep(1)
        url_umasyokin = 'https://keiba.rakuten.co.jp/horse_detail/detail/HORSEID/' + horse_id
        all_money = pd.read_html(url_umasyokin)[2].head(3)
        if all_money.loc[2][10] <= 5000000:
            nar_money = float((all_money.loc[1][10] + all_money.loc[2][10]) / 10000)
        else:
            nar_money = float((all_money.loc[1][10] + all_money.loc[2][10] * 0.6 + 2000000) / 10000)
        horse_syokin_list.append(nar_money)

    syokin = soup.select_one('#raceInfomation > div > div.raceNote > dl').text.split()
    del syokin[0]

    race_syokin = []
    for kane in syokin:
        money = int(re.sub('\d' + '着', '', kane)[:-1].replace(',', ''))
        money_man_en = float(money / 10000)
        race_syokin.append(money_man_en)

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

                    if 'Ｊ' in p_df.iloc[t]['競馬場'] and 'オープン' in p_df.iloc[t]['レース名2']:  
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

                    elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 500
                    elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 700                        
                    elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 450
                    elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 600                        
                    elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 415
                    elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 500                        


                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 350
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 500                        
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 450                         
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                        kijun = 400                         
                    elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2'])\
                      and ('Ｓ' and 'Ａ' and 'Ｂ' and 'Ｃ' not in p_df.iloc[t]['レース名2']) and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30): 
                        kijun = 240
                    elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2'])\
                      and ('Ｓ' and 'Ａ' and 'Ｂ' and 'Ｃ' not in p_df.iloc[t]['レース名2']) and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1): 
                        kijun = 350

                    elif p_df.iloc[t]['競馬場'] in nankan and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                        kijun = 320
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' not in p_df.iloc[t]['レース名2'])): #A2
                        kijun = 300
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' in p_df.iloc[t]['レース名2'])): #A2B1
                        kijun = 270
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])): #B1
                        kijun = 240  
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ｂ２' in p_df.iloc[t]['レース名2'])): #B1B2
                        kijun = 230        
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' and 'Ｂ３' not in p_df.iloc[t]['レース名2'])): #B2  
                        kijun = 220
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ３' in p_df.iloc[t]['レース名2'])):  #B2B3
                        kijun = 210
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｂ２' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])): #B3
                        kijun = 200
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｃ１' in p_df.iloc[t]['レース名2'])): #B3C1
                        kijun = 180
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｂ３' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])): #C1
                        kijun = 160
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｃ２' in p_df.iloc[t]['レース名2'])): #C1C2
                        kijun = 150
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])): #C2
                        kijun = 140
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ３' in p_df.iloc[t]['レース名2'])): #C2C3
                        kijun = 130
                    elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ３' in p_df.iloc[t]['レース名2']) and ('Ｃ２' not in p_df.iloc[t]['レース名2'])): #C3  
                        kijun = 120
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
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2']) / 4   #4戦の馬と比較するから
                    if rensho < -0.7:
                        e = 1.4
                    elif -0.7 <= rensho < -0.5:
                        e = 1.3    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.2
                    else:
                        e = 1.1                
                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1: # and p_df.iloc[2]['着順2'] != 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] +p_df.iloc[2]['差2']) / 4   #4戦の馬と比較するから
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
                if '牝' in horse_id:
                    f = kijun1 * 0.1 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                else:
                    f = kijun1 * 0.1 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))

                #休養係数        
                #if td(weeks = 12) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 24):
                    #g = 0.95
                #elif td(weeks = 24) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    #g = 0.9
                if td(weeks = 8) < (racedate - p_df.iloc[0]['日付2']):
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
                    if p_df.iloc[0]['コース'] == '芝' and p_df.iloc[1]['コース'] == '芝':
                        i = 0.7
                    else:
                        i = 1.0           



                ts = ((kijun1 *2 *a *a1 *2 + kijun2 *b *b1 + kijun3 *c *c1) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts)



            else:
                if int(horse_id[-1]) == 3:   #3歳　補正  

                    base_number = []
                    for t in range(4):

                        if 'Ｊ' in p_df.iloc[t]['競馬場'] and 'オープン' in p_df.iloc[t]['レース名2']:  
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

                        elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                            kijun = 500
                        elif 'Ｊｐｎ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 700                        
                        elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                            kijun = 450
                        elif  'Ｊｐｎ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 600                        
                        elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                            kijun = 415
                        elif  'Ｊｐｎ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 500                        


                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30):  
                            kijun = 350
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ１' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 500                        
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 6, 30):  
                            kijun = 320
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ２' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 450                         
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] < dt(kotoshi, 6, 30):  
                            kijun = 300
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ｓ３' in p_df.iloc[t]['レース名2'] and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1):  
                            kijun = 400                         
                        elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2'])\
                          and ('Ｓ' and 'Ａ' and 'Ｂ' and 'Ｃ' not in p_df.iloc[t]['レース名2']) and p_df.iloc[t]['日付2'] <= dt(kotoshi, 6, 30): 
                            kijun = 240
                        elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2'])\
                          and ('Ｓ' and 'Ａ' and 'Ｂ' and 'Ｃ' not in p_df.iloc[t]['レース名2']) and p_df.iloc[t]['日付2'] >= dt(kotoshi, 7, 1): 
                            kijun = 350
                            
                            
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                            kijun = 320
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' not in p_df.iloc[t]['レース名2'])): #A2
                            kijun = 300
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' in p_df.iloc[t]['レース名2'])): #A2B1
                            kijun = 270
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])): #B1
                            kijun = 240  
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ｂ２' in p_df.iloc[t]['レース名2'])): #B1B2
                            kijun = 230        
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' and 'Ｂ３' not in p_df.iloc[t]['レース名2'])): #B2  
                            kijun = 220
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ３' in p_df.iloc[t]['レース名2'])):  #B2B3
                            kijun = 210
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｂ２' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])): #B3
                            kijun = 200
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｃ１' in p_df.iloc[t]['レース名2'])): #B3C1
                            kijun = 180
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｂ３' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])): #C1
                            kijun = 160
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｃ２' in p_df.iloc[t]['レース名2'])): #C1C2
                            kijun = 150
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])): #C2
                            kijun = 140
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ３' in p_df.iloc[t]['レース名2'])): #C2C3
                            kijun = 130
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ３' in p_df.iloc[t]['レース名2']) and ('Ｃ２' not in p_df.iloc[t]['レース名2'])): #C3  
                            kijun = 120
                        else:
                            kijun = 60

                        base_number.append(kijun)

                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]

    #古馬の指数
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


                        elif '帝王賞' and 'Ｊｐｎ１' in p_df.iloc[t]['レース名2']:  
                            kijun = 800
                        elif '東京大賞典' and 'Ｊｐｎ１' in p_df.iloc[t]['レース名2']:  
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
                        elif p_df.iloc[t]['競馬場'] in nankan and ('オープン' in p_df.iloc[t]['レース名2'])\
                          and ('Ｓ' and 'Ａ' and 'Ｂ' and 'Ｃ' not in p_df.iloc[t]['レース名2']): 
                            kijun = 350 
                        elif p_df.iloc[t]['競馬場'] in nankan and 'Ａ１' in p_df.iloc[t]['レース名2']:  
                            kijun = 320
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' not in p_df.iloc[t]['レース名2'])): #A2
                            kijun = 300
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' in p_df.iloc[t]['レース名2'])): #A2B1
                            kijun = 270
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])): #B1
                            kijun = 240  
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ｂ２' in p_df.iloc[t]['レース名2'])): #B1B2
                            kijun = 230        
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ１' and 'Ｂ３' not in p_df.iloc[t]['レース名2'])): #B2  
                            kijun = 220
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ｂ３' in p_df.iloc[t]['レース名2'])):  #B2B3
                            kijun = 210
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｂ２' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])): #B3
                            kijun = 200
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｂ３' in p_df.iloc[t]['レース名2']) and ('Ｃ１' in p_df.iloc[t]['レース名2'])): #B3C1
                            kijun = 180
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｂ３' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])): #C1
                            kijun = 160
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｃ２' in p_df.iloc[t]['レース名2'])): #C1C2
                            kijun = 150
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])): #C2
                            kijun = 140
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ３' in p_df.iloc[t]['レース名2'])): #C2C3
                            kijun = 130
                        elif p_df.iloc[t]['競馬場'] in nankan and (('Ｃ３' in p_df.iloc[t]['レース名2']) and ('Ｃ２' not in p_df.iloc[t]['レース名2'])): #C3  
                            kijun = 120

                        elif p_df.iloc[t]['競馬場'] in hyogo and ('ＪＲＡ交流' in p_df.iloc[t]['レース名2']):  
                            kijun = 280    
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('重賞' in p_df.iloc[t]['レース名2']):  
                            kijun = 350
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ１' in p_df.iloc[t]['レース名2']) and ('Ａ２' not in p_df.iloc[t]['レース名2'])):  
                            kijun = 280
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ１'and 'Ａ２' in p_df.iloc[t]['レース名2']):  
                            kijun = 260
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ａ２' in p_df.iloc[t]['レース名2']) and ('Ａ１' and 'Ｂ１' not in p_df.iloc[t]['レース名2'])):  
                            kijun = 240
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ａ２' and 'Ｂ１' in p_df.iloc[t]['レース名2']):  
                            kijun = 220
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ１' in p_df.iloc[t]['レース名2']) and ('Ａ２' and 'Ｂ２' not in p_df.iloc[t]['レース名2'])):
                            kijun = 200        
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ１' and 'Ｂ２' in p_df.iloc[t]['レース名2']):  
                            kijun = 180
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｂ２' in p_df.iloc[t]['レース名2']) and ('Ａ１' and 'Ｃ１' not in p_df.iloc[t]['レース名2'])):
                            kijun = 160     
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｂ２' and 'Ｃ１' in p_df.iloc[t]['レース名2']):  
                            kijun = 140
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ１' in p_df.iloc[t]['レース名2']) and ('Ｂ２' and 'Ｃ２' not in p_df.iloc[t]['レース名2'])):  
                            kijun = 120
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ１' and 'Ｃ２' in p_df.iloc[t]['レース名2']):  
                            kijun = 110
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ２' in p_df.iloc[t]['レース名2']) and ('Ｃ１' and 'Ｃ３' not in p_df.iloc[t]['レース名2'])):  
                            kijun = 100
                        elif p_df.iloc[t]['競馬場'] in hyogo and ('Ｃ２' and 'Ｃ３' in p_df.iloc[t]['レース名2']):  
                            kijun = 90   
                        elif p_df.iloc[t]['競馬場'] in hyogo and (('Ｃ３' in p_df.iloc[t]['レース名2']) and ('Ｃ２' not in p_df.iloc[t]['レース名2'])):  
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
                        elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' in p_df.iloc[t]['レース名2']:  
                            kijun = 240
                        elif p_df.iloc[t]['競馬場'] == '門別' and 'Ａ' not in p_df.iloc[t]['レース名2'] and 'Ｂ' in p_df.iloc[t]['レース名2']:  
                            kijun = 180

                        elif p_df.iloc[t]['競馬場'] in others and 'オープン' in p_df.iloc[t]['レース名2'] and 'Ｊｐｎ' not in p_df.iloc[t]['レース名2']:  
                            kijun = 220
                        elif p_df.iloc[t]['競馬場'] in others and 'Ａ' in p_df.iloc[t]['レース名2'] and 'Ｂ' not in p_df.iloc[t]['レース名2']:  
                            kijun = 200

                        else:
                            kijun = 60

                        base_number.append(kijun)

                    kijun1, kijun2, kijun3, kijun4 = base_number[0], base_number[1], base_number[2], base_number[3]


                #着差係数

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
                if p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1 and p_df.iloc[2]['着順2'] == 1 and p_df.iloc[3]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2'] -p_df.iloc[3]['差2']) / 4
                    if rensho < -0.7:
                        e = 1.5
                    elif -0.7 <= rensho < -0.5:
                        e = 1.4    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.3
                    else:
                        e = 1.2                
                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2'] == 1 and p_df.iloc[2]['着順2'] == 1:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] -p_df.iloc[2]['差2'] +p_df.iloc[3]['差2']) / 4    

                    if rensho < -0.7:
                        e = 1.4
                    elif -0.7 <= rensho < -0.5:
                        e = 1.3    
                    elif -0.5 <= rensho < -0.3:
                        e = 1.2
                    else:
                        e = 1.1

                elif p_df.iloc[0]['着順2'] == 1 and p_df.iloc[1]['着順2']:
                    rensho = (-p_df.iloc[0]['差2'] -p_df.iloc[1]['差2'] +p_df.iloc[2]['差2'] +p_df.iloc[3]['差2']) / 4    

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
                if '牝' in horse_id:
                    f = kijun1 * 0.1 * ((float(max(weight_list))) - 2.0 - float(horse_id[10:15].strip()))
                else:
                    f = kijun1 * 0.1 * ((float(max(weight_list))) - float(horse_id[10:15].strip()))

                #休養係数        
                #if td(weeks = 12) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 24):
                    #g = 0.95
                #elif td(weeks = 24) < (racedate - p_df.iloc[0]['日付2']) <= td(weeks = 48):
                    #g = 0.9
                if td(weeks = 8) < (racedate - p_df.iloc[0]['日付2']):
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



                ts = ((kijun1 *2 *a *a1 + kijun2 *2 *b *b1 + kijun3 *c *c1 + kijun4 *d *d1 ) + f) * e * g * h * i
                tekito_shisu[horse_id]= int(ts)

        return tekito_shisu



    kekka = shisu(processed_horse_results)
    hyo = pd.DataFrame({'馬番': umaban, '馬名': horse_name_list})
    hyo1 = copy.deepcopy(hyo)
    hyo1['指数'] = kekka.values()
    hyo1['賞金'] = horse_syokin_list
    hyo1['騎手'] = jockey_list
    hyo1['調教師'] = trainer_list
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

    
#0911時点のデータ    

    hyo1.loc[hyo1['騎手'] == '森泰斗', '指数'] = hyo1['指数'] * 1.20 #騎手補正：連帯率40以上:1.2, 35-40%:1.15, 30-35%:1.1, 25-30%:1.05 
    hyo1.loc[hyo1['騎手'] == '御神訓', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '真島大', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '矢野貴', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '笹川翼', '指数'] = hyo1['指数'] * 1.10
    hyo1.loc[hyo1['騎手'] == '左海誠', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '本田重', '指数'] = hyo1['指数'] * 1.00
    hyo1.loc[hyo1['騎手'] == '山崎誠', '指数'] = hyo1['指数'] * 1.05
    hyo1.loc[hyo1['騎手'] == '吉原寛', '指数'] = hyo1['指数'] * 1.10
    
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
    hyo1['年齢'] = hyo1['年齢'].astype(int)
    hyo1['順位'] = hyo1['指数'].rank(ascending=False).astype(int)


    #出走馬のクラスを算出

    cl_list = []
    for i in range(len(hyo1)):
        if racedate <= dt(kotoshi, 6, 30):

            if hyo1.loc[i]['年齢'] == 3:
                if 0 <= hyo1.loc[i]['賞金'] < 600:
                    present_cl = "ND"
                elif 500 <= hyo1.loc[i]['賞金'] < 1000:
                    present_cl = "B3"
                elif 800 <= hyo1.loc[i]['賞金'] < 1300:
                    present_cl = "B2"
                elif 1100 <= hyo1.loc[i]['賞金'] < 1800:
                    present_cl = "B1"
                elif 1500 <= hyo1.loc[i]['賞金'] < 2600:
                    present_cl = "A2"
                else:
                    present_cl = "A1"                        
            
            if hyo1.loc[i]['年齢'] == 4:
                if 0 <= hyo1.loc[i]['賞金'] < 200:
                    present_cl = "C3"
                elif 200 <= hyo1.loc[i]['賞金'] < 400:
                    present_cl = "C2"
                elif 400 <= hyo1.loc[i]['賞金'] < 700:
                    present_cl = "C1"
                elif 700 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "B3"
                elif 1000 <= hyo1.loc[i]['賞金'] < 1500:
                    present_cl = "B2"
                elif 1400 <= hyo1.loc[i]['賞金'] < 2000:
                    present_cl = "B1"
                elif 1900 <= hyo1.loc[i]['賞金'] < 3300:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] == 5:
                if 0 <= hyo1.loc[i]['賞金'] < 400:
                    present_cl = "C3"
                elif 400 <= hyo1.loc[i]['賞金'] < 700:
                    present_cl = "C2"
                elif 600 <= hyo1.loc[i]['賞金'] < 1000:
                    present_cl = "C1"
                elif 900 <= hyo1.loc[i]['賞金'] < 1400:
                    present_cl = "B3"
                elif 1300 <= hyo1.loc[i]['賞金'] < 1900:
                    present_cl = "B2"
                elif 1800 <= hyo1.loc[i]['賞金'] < 2500:
                    present_cl = "B1"
                elif 2400 <= hyo1.loc[i]['賞金'] < 4200:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] == 6:
                if 0 <= hyo1.loc[i]['賞金'] < 700:
                    present_cl = "C3"
                elif 700 <= hyo1.loc[i]['賞金'] < 1000:
                    present_cl = "C2"
                elif 1000 <= hyo1.loc[i]['賞金'] < 1300:
                    present_cl = "C1"
                elif 1300 <= hyo1.loc[i]['賞金'] < 1700:
                    present_cl = "B3"
                elif 1700 <= hyo1.loc[i]['賞金'] < 2300:
                    present_cl = "B2"
                elif 2300 <= hyo1.loc[i]['賞金'] < 3200:
                    present_cl = "B1"
                elif 3000 <= hyo1.loc[i]['賞金'] < 5000:
                    present_cl = "A2"
                else:
                    present_cl = "A1"             

            elif hyo1.loc[i]['年齢'] == 7:
                if 0 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "C3"
                elif 1100 <= hyo1.loc[i]['賞金'] < 1400:
                    present_cl = "C2"
                elif 1400 <= hyo1.loc[i]['賞金'] < 1700:
                    present_cl = "C1"
                elif 1700 <= hyo1.loc[i]['賞金'] < 2100:
                    present_cl = "B3"
                elif 2100 <= hyo1.loc[i]['賞金'] < 2800:
                    present_cl = "B2"
                elif 2800 <= hyo1.loc[i]['賞金'] < 3800:
                    present_cl = "B1"
                elif 3500 <= hyo1.loc[i]['賞金'] < 5600:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] >= 8:
                if 0 <= hyo1.loc[i]['賞金'] < 1200:
                    present_cl = "C3"
                elif 1200 <= hyo1.loc[i]['賞金'] < 1500:
                    present_cl = "C2"
                elif 1500 <= hyo1.loc[i]['賞金'] < 1900:
                    present_cl = "C1"
                elif 1900 <= hyo1.loc[i]['賞金'] < 2300:
                    present_cl = "B3"
                elif 2400 <= hyo1.loc[i]['賞金'] < 3100:
                    present_cl = "B2"
                elif 3100 <= hyo1.loc[i]['賞金'] < 4200:
                    present_cl = "B1"
                elif 3900 <= hyo1.loc[i]['賞金'] < 6000:
                    present_cl = "A2"
                else:
                    present_cl = "A1"         

            cl_list.append(present_cl)


        if racedate >= dt(kotoshi, 7, 1):
            if hyo1.loc[i]['年齢'] == 3:
                if 0 <= hyo1.loc[i]['賞金'] < 200:
                    present_cl = "C3"
                elif 200 <= hyo1.loc[i]['賞金'] < 400:
                    present_cl = "C2"
                elif 400 <= hyo1.loc[i]['賞金'] < 700:
                    present_cl = "C1"
                elif 700 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "B3"
                elif 1000 <= hyo1.loc[i]['賞金'] < 1500:
                    present_cl = "B2"
                elif 1300 <= hyo1.loc[i]['賞金'] < 2000:
                    present_cl = "B1"
                elif 1700 <= hyo1.loc[i]['賞金'] < 2800:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] == 4:
                if 0 <= hyo1.loc[i]['賞金'] < 300:
                    present_cl = "C3"
                elif 300 <= hyo1.loc[i]['賞金'] < 500:
                    present_cl = "C2"
                elif 500 <= hyo1.loc[i]['賞金'] < 800:
                    present_cl = "C1"
                elif 800 <= hyo1.loc[i]['賞金'] < 1200:
                    present_cl = "B3"
                elif 1100 <= hyo1.loc[i]['賞金'] < 1700:
                    present_cl = "B2"
                elif 1600 <= hyo1.loc[i]['賞金'] < 2200:
                    present_cl = "B1"
                elif 2000 <= hyo1.loc[i]['賞金'] < 3500:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] == 5:
                if 0 <= hyo1.loc[i]['賞金'] < 500:
                    present_cl = "C3"
                elif 500 <= hyo1.loc[i]['賞金'] < 800:
                    present_cl = "C2"
                elif 700 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "C1"
                elif 1000 <= hyo1.loc[i]['賞金'] < 1500:
                    present_cl = "B3"
                elif 1400 <= hyo1.loc[i]['賞金'] < 2100:
                    present_cl = "B2"
                elif 2100 <= hyo1.loc[i]['賞金'] < 2700:
                    present_cl = "B1"
                elif 2500 <= hyo1.loc[i]['賞金'] < 4400:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] == 6:
                if 0 <= hyo1.loc[i]['賞金'] < 800:
                    present_cl = "C3"
                elif 800 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "C2"
                elif 1100 <= hyo1.loc[i]['賞金'] < 1400:
                    present_cl = "C1"
                elif 1400 <= hyo1.loc[i]['賞金'] < 1800:
                    present_cl = "B3"
                elif 1800 <= hyo1.loc[i]['賞金'] < 2500:
                    present_cl = "B2"
                elif 2500 <= hyo1.loc[i]['賞金'] < 3400:
                    present_cl = "B1"
                elif 3100 <= hyo1.loc[i]['賞金'] < 5200:
                    present_cl = "A2"
                else:
                    present_cl = "A1"             

            elif hyo1.loc[i]['年齢'] == 7:
                if 0 <= hyo1.loc[i]['賞金'] < 1100:
                    present_cl = "C3"
                elif 1100 <= hyo1.loc[i]['賞金'] < 1400:
                    present_cl = "C2"
                elif 1400 <= hyo1.loc[i]['賞金'] < 1800:
                    present_cl = "C1"
                elif 1800 <= hyo1.loc[i]['賞金'] < 2200:
                    present_cl = "B3"
                elif 2200 <= hyo1.loc[i]['賞金'] < 3000:
                    present_cl = "B2"
                elif 3000 <= hyo1.loc[i]['賞金'] < 4100:
                    present_cl = "B1"
                elif 3700 <= hyo1.loc[i]['賞金'] < 5900:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            elif hyo1.loc[i]['年齢'] >= 8:
                if 0 <= hyo1.loc[i]['賞金'] < 1200:
                    present_cl = "C3"
                elif 1200 <= hyo1.loc[i]['賞金'] < 1500:
                    present_cl = "C2"
                elif 1500 <= hyo1.loc[i]['賞金'] < 1900:
                    present_cl = "C1"
                elif 1900 <= hyo1.loc[i]['賞金'] < 2300:
                    present_cl = "B3"
                elif 2400 <= hyo1.loc[i]['賞金'] < 3100:
                    present_cl = "B2"
                elif 3200 <= hyo1.loc[i]['賞金'] < 4200:
                    present_cl = "B1"
                elif 3900 <= hyo1.loc[i]['賞金'] < 6000:
                    present_cl = "A2"
                else:
                    present_cl = "A1"

            cl_list.append(present_cl)

    hyo1["クラス"] = cl_list

    #出走馬の昇級しない着順を算出

    #前期

    ok_list = []
    for i in range(len(hyo1)):
        if racedate <= dt(kotoshi, 6, 30):
            
            if hyo1.loc[i]['年齢'] == 3:
                if hyo1.loc[i]['クラス'] == 'ND':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)
                
            
            elif hyo1.loc[i]['年齢'] == 4:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 200:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 200:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 200:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 200:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 200:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                 
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"
                
                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 5:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                    
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 600:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 600:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 600:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 600:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 600:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3600:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3600:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3600:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3600:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3600:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 
                        
                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 6:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                    
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 4700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 4700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 4700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 4700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 4700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 7:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                    
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 5300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 5300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 5300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 5300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 5300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)


            else:
                
                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1200:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1200:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1200:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1200:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1200:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"
                               
                if hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 5800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 5800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 5800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 5800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 5800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題" 

                ok_list.append(ok)


    #後期
        else:
            if hyo1.loc[i]['年齢'] == 3:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 200:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 200:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 200:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 200:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 200:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    
                
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 
                else:
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 4:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"   
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1600:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1600:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1600:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1600:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1600:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3300:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3300:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3300:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3300:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3300:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 
                else:
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 5:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                   
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 4100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 4100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 4100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 4100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 4100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            elif hyo1.loc[i]['年齢'] == 6:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                   
                
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 4800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 4800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 4800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 4800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 4800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)


            elif hyo1.loc[i]['年齢'] == 7:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                     

                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2200:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2200:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2200:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2200:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2200:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3000:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3000:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3000:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3000:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3000:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3700:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3700:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3700:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3700:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3700:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 5500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 5500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 5500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 5500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 5500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 
                        
                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題"

                ok_list.append(ok)

            else:    
            #if hyo1.loc[i]['年齢'] >= 8:

                if hyo1.loc[i]['クラス'] == 'C3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1200:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1200:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1200:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1200:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1200:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"                
            
                elif hyo1.loc[i]['クラス'] == 'C2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1500:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1500:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1500:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1500:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1500:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"    

                elif hyo1.loc[i]['クラス'] == 'C1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 1900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 1900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 1900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 1900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 1900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B3':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 2400:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 2400:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 2400:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 2400:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 2400:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'B2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3100:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3100:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3100:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3100:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3100:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                elif hyo1.loc[i]['クラス'] == 'B1':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 3900:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 3900:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 3900:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 3900:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 3900:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級"

                elif hyo1.loc[i]['クラス'] == 'A2':
                    if hyo1.loc[i]['賞金'] + race_syokin[4] >= 5800:
                        ok = "5着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[3] >= 5800:
                        ok = "4着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[2] >= 5800:
                        ok = "3着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[1] >= 5800:
                        ok = "2着で昇級"
                    elif hyo1.loc[i]['賞金'] + race_syokin[0] >= 5800:
                        ok = "1着で昇級"
                    else:
                        ok = "1着でも現級" 

                else:        
                #elif hyo1.loc[i]['クラス'] == 'A1':
                    ok = "稼ぎ放題" 

                ok_list.append(ok)

    hyo1["許容着順"] = ok_list
    hyo2 = hyo1[['順位', '馬番','馬名', '騎手', '調教師', 'クラス', '許容着順', '前走', '指数', 'オッズ', '年齢']]
    hyo3 = hyo2.sort_values('順位')
    hyo3.set_index("順位", inplace=True)

    st.write(racename)
    st.table(hyo3)
    
else:
    st.write("・・・・・・・")

