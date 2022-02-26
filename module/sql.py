import numpy as np
import pandas as pd
import sqlite3
from os import mkdir
import csv


def make_database():
    try:
        conn = sqlite3.connect('data/team3.db')
    except sqlite3.OperationalError:
        mkdir('error')
    finally:
        conn = sqlite3.connect('data/team3.db')
        cur = conn.cursor()

    hr = """create table if not exists hr(
            datetime  datetime,
            worker_number   int,
            real_number int,
            biztrip_number  int,
            overtime_number int,
            telecom_number  int    
        )
        """
    cur.execute(hr)
    conn.commit()

    lunch = """create table if not exists lunch(
            datetime  datetime,
            new_lunch   varchar(10),
            lunch_rice varchar(20),
            lunch_soup  varchar(20),
            lunch_main varchar(20),
            lunch_number  int    
        )
        """
    cur.execute(lunch)
    conn.commit()

    dinner = """create table if not exists dinner(
            datetime  datetime,
            new_dinner   varchar(10),
            dinner_rice varchar(20),
            dinner_soup  varchar(20),
            dinner_main varchar(20),
            dinner_number  int    
        )
        """
    cur.execute(dinner)
    conn.commit()

    weather = """create table if not exists weather(
            datetime  datetime,
            temperature   float(32),
            rain float(32),
            wind float(32),
            humidity  float(32),
            discomfort_index    float(32),
            perceived_temperature   float(32)
        )
        """
    cur.execute(weather)
    conn.commit()

    calendar = """create table if not exists calendar(
            datetime  datetime,
            year   int,
            month   int,
            date int,
            weekdays  varchar(16),
            season varchar(16),
            vacation  int    
            )
            """
    cur.execute(calendar)
    conn.commit()

    conn.close()


class Transform():
    def __init__(self, data, weather):
        self.data = data
        self.weather = weather

    def transform_data(self):
        #### 1. 일자를 datetime 형태로 변경
        self.data['일자'] = pd.to_datetime(self.data['일자'])
        #### 2. 실질 사내 근무자 수
        self.data['실질정원수'] = self.data['본사정원수'] - (self.data['본사휴가자수'] + self.data['본사출장자수'] + self.data['현본사소속재택근무자수'])
        self.data = self.data.loc[:, ['일자', '요일', '본사정원수', '실질정원수', '본사휴가자수', '본사출장자수', '본사시간외근무명령서승인건수', '현본사소속재택근무자수', '중식메뉴', '석식메뉴', '중식계', '석식계']]
        #### 3. 월, 일 칼럼과 계절 칼럼, 연휴 칼럼 만들기
        self.data['Year'] = self.data['일자'].dt.strftime('%Y')
        self.data['Month'] = self.data['일자'].dt.strftime('%m')
        self.data['Date'] = self.data['일자'].dt.strftime('%d')
        
        season = []

        for index in range(len(self.data)):
            if self.data['Month'][index] == '03' or self.data['Month'][index] == '04' or self.data['Month'][index] == '05':
                season.append('spring')
            elif self.data['Month'][index] == '06' or self.data['Month'][index] == '07' or self.data['Month'][index] == '08':
                season.append('summer')
            elif self.data['Month'][index] == '09' or self.data['Month'][index] == '10' or self.data['Month'][index] == '11':
                season.append('fall')
            elif self.data['Month'][index] == '12' or self.data['Month'][index] == '01' or self.data['Month'][index] == '02':
                season.append('winter')
        
        self.data['Season'] = season



        holiday_gap=[]

        for i in range(len(self.data)):
            if i == len(self.data) - 1:
                holiday_gap.append(0)
            elif int((pd.to_datetime(self.data['일자'][i+1])-pd.to_datetime(self.data['일자'][i])).days)==1:
                holiday_gap.append(0)
            elif int((pd.to_datetime(self.data['일자'][i+1])-pd.to_datetime(self.data['일자'][i])).days)==2:
                holiday_gap.append(1)
            elif int((pd.to_datetime(self.data['일자'][i+1])-pd.to_datetime(self.data['일자'][i])).days)==3:
                holiday_gap.append(0)
            else:
                holiday_gap.append(1)
                
        self.data['연휴'] = holiday_gap


        weekdays=[]
        
        for i in range(len(self.data.index)):
            if self.data['요일'][i] == "월":
                weekdays.append("monday")
            elif self.data['요일'][i] == "화":
                weekdays.append("tuesday")
            elif self.data['요일'][i] == "수":
                weekdays.append("wednesday")
            elif self.data['요일'][i] == "목":
                weekdays.append("thursday")
            elif self.data['요일'][i] == "금":
                weekdays.append("friday")
            elif self.data['요일'][i] == "토":
                weekdays.append("saturday")
            elif self.data['요일'][i] == "일":
                weekdays.append("sunday")
            
        self.data['요일'] = weekdays

        #### 4. 신메뉴 여부 칼럼 만들기 Y = 신메뉴 / N = 신메뉴 X
        New_lunch = []
        New_dinner = []

        for index in range(len(self.data)):
            if 'New' in self.data['중식메뉴'][index]:
                New_lunch.append('Y')
            else:
                New_lunch.append('N')

        for index in range(len(self.data)):
            if 'New' in self.data['석식메뉴'][index]:
                New_dinner.append('Y')
            else:
                New_dinner.append('N')
        
        self.data['New_lunch'] = New_lunch
        self.data['New_dinner'] = New_dinner

        #### 5. 점심, 저녁에서 밥, 국, 메인반찬 칼럼 만들기
        #점심
        lunch = []
        for index in range(len(self.data)):
            tmp = self.data.loc[index,'중식메뉴'].split(' ') # 스페이스로 구분
            tmp = ' '.join(tmp).split()    # 빈칸 제거

            # ()안에 있는 내용 제거
            for menu in tmp:
                if '(' in menu:
                    tmp.remove(menu)
            lunch.append(tmp)

        for index in range(len(self.data)):
            if '쌀밥' in lunch[index][0]:
                lunch[index][0] = '밥'
        
        rice=[]
        soup=[]
        main=[]

        for i in range(len(self.data)):
            if lunch[i][0]:
                rice.append(lunch[i][0])
            if lunch[i][1]:
                soup.append(lunch[i][1])
            if lunch[i][2]:
                main.append(lunch[i][2])

        self.data['lunch_rice'] = rice
        self.data['lunch_soup'] = soup
        self.data['lunch_main'] = main

        #저녁
        dinner = []

        for index in range(len(self.data)):
            tmp = self.data.loc[index,'석식메뉴'].split(' ')
            tmp = ' '.join(tmp).split()

            for menu_d in tmp:
                if '(' in menu_d:
                    tmp.remove(menu_d)
            dinner.append(tmp)

        dinner_rice=[]
        dinner_soup=[]
        dinner_main=[]


        for word in dinner:
            
            
            if len(word) == 0:
                dinner_rice.append('None')
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '*' in word:
                dinner_rice.append('None')
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '가정의날' in word:
                dinner_rice.append('None') 
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '가정의달' in word:
                dinner_rice.append('None') 
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '자기계발의날' in word:
                dinner_rice.append('None') 
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '*자기계발의날*' in word:
                dinner_rice.append('None') 
                dinner_soup.append('None')
                dinner_main.append('None')
            elif '자기개발의날' in word:
                dinner_rice.append('None') 
                dinner_soup.append('None')
                dinner_main.append('None')

            else:
                dinner_rice.append(word[0])
                dinner_soup.append(word[1])
                dinner_main.append(word[2])
        
        self.data['dinner_rice'] = dinner_rice
        self.data['dinner_soup'] = dinner_soup
        self.data['dinner_main'] = dinner_main

        for index in range(len(self.data)):
            if '쌀밥' in self.data['dinner_rice'][index]:
                self.data['dinner_rice'][index] = '밥'
            elif '흑미밥' in self.data['dinner_rice'][index]:
                self.data['dinner_rice'][index] = '밥'
            
        del self.data['중식메뉴']
        del self.data['석식메뉴']

        return self.data


    def transform_weather(self):
        #### 6. 날짜 데이터 merge
        # merge 전 날짜 데이터 전처리
        self.weather['일자'] = pd.to_datetime(self.weather['일시'])
        del self.weather['일시']
        del self.weather['지점']
        del self.weather['지점명']

        #결측치 제거
        self.weather['일강수량(mm)']=self.weather['일강수량(mm)'].replace({np.NaN:0})
        self.weather['평균 상대습도(%)'] = self.weather['평균 상대습도(%)'].replace({np.NaN:0})

        #칼럼명 변경
        self.weather.columns = ['기온', '강수량', '풍속', '습도', '일자']

        # 불쾌지수, 체감온도 칼럼 생성
        self.weather['불쾌지수'] = 9/5 * self.weather['기온'] - 0.55 * (1-self.weather['습도']/100) * (9/5 * self.weather['기온'] - 26) + 32
        self.weather['체감온도'] = 13.12 + 0.6215 * self.weather['기온'] - 11.37 * (self.weather['풍속'] ** 0.16) + 0.3965 * (self.weather['풍속'] ** 0.16) * self.weather['기온']    #### 7. 칼럼명 영어로 바꾸기

        return self.weather

    # 2022.02.26일 transfrom_data, transform_weather 함수로 얻은 결과값을 make_csv에 자동으로 입력되게 만들고 싶음
    # make_csv를 클래스에서 뺀 다음 두 함수의 리턴값을 직접 입력해주는 방식도 괜찮지만, 모듈은 만든 이유가 자동화이기 때문에 가능하면 두 함수의 리턴값을 입력하게 만들고 싶음.
    # 해결
    def make_csv(self):
        data = self.transform_data()
        weather = self.transform_weather()
        df = pd.merge(data, weather, how='inner', on='일자')

        col_eng = ['datetime', 'weekdays', 'worker_number', 'real_number', 'vacation_number', 'biztrip_number', 'overtime_number', 'telecom_number', 'lunch_number',
            'dinner_number', 'year', 'month', 'date', 'season', 'vacation', 'new_lunch', 'new_dinner', 'lunch_rice', 'lunch_soup', 'lunch_main', 'dinner_rice', 'dinner_soup', 'dinner_main',
            'temperature', 'rain', 'wind', 'humidity', 'discomfort_index', 'perceived_temperature']

        df.columns=col_eng

        return df

#Save_DB에 입력될 data는 Transform.make_csv의 리턴값이어야 합니다.
class Save_DB():
    def __init__(self, data):
        self.data = data

    def split(self):
        hr_data = self.data.loc[:, ["datetime", "worker_number", "real_number", "biztrip_number", "overtime_number", "telecom_number"]]
        lunch_data = self.data.loc[:, ["datetime", "new_lunch", "lunch_rice", "lunch_soup", "lunch_main", "lunch_number"]]
        dinner_data = self.data.loc[:, ["datetime", "new_dinner", "dinner_rice", "dinner_soup", "dinner_main", "dinner_number"]]
        weather_data = self.data.loc[:, ["datetime", "temperature", 'rain', 'wind', 'humidity', 'discomfort_index', 'perceived_temperature']]
        calendar_data = self.data.loc[:, ['datetime', 'year', 'month', 'date', 'weekdays', 'season', 'vacation']]

        return hr_data, lunch_data, dinner_data, weather_data, calendar_data


        # 데이터 입력하면 한번에 다 저장되도록 함수로 만들었습니다.
        # 데이터를 저장하는 이유는 파이썬에서 db에 데이터를 입력하기 위해 다시 csv 라이브러리로 open 시켜 한줄씩 불러와 반복문으로 입력해야하기 때문입니다. 
    def save(self):
        hr_data, lunch_data, dinner_data, weather_data, calendar_data = self.split()
        hr_data.to_csv("data/hr_data.csv", encoding='utf-8', index=False)
        lunch_data.to_csv("data/lunch_data.csv", encoding='utf-8', index=False)
        dinner_data.to_csv("data/dinner_data.csv", encoding='utf-8', index=False)
        weather_data.to_csv("data/weather_data.csv", encoding='utf-8', index=False)
        calendar_data.to_csv("data/calendar_data.csv", encoding='utf-8', index=False)

        # 함수 호출로 csv 데이터를 db에 저장할 수 있게 만들었습니다.
    def hr_db():
        conn = sqlite3.connect("data/team3.db")
        cur = conn.cursor()

        file = csv.reader(open("data/hr_data.csv", "r"), delimiter=",")
        next(file)

        for row in file:
            cur.execute("insert into hr values(?, ?, ?, ?, ?, ?)", row)

        conn.commit()
        conn.close()


    def lunch_db():
        conn = sqlite3.connect("data/team3.db")
        cur = conn.cursor()

        file = csv.reader(open("data/lunch_data.csv", "r"), delimiter=",")
        next(file)

        for row in file:
            cur.execute("insert into lunch values(?, ?, ?, ?, ?, ?)", row)

        conn.commit()
        conn.close()


    def dinner_db():
        conn = sqlite3.connect("data/team3.db")
        cur = conn.cursor()

        file = csv.reader(open("data/dinner_data.csv", "r"), delimiter=",")
        next(file)

        for row in file:
            cur.execute("insert into dinner values(?, ?, ?, ?, ?, ?)", row)

        conn.commit()
        conn.close()


    def weather_db():
        conn = sqlite3.connect("data/team3.db")
        cur = conn.cursor()

        file = csv.reader(open("data/weather_data.csv", "r"), delimiter=",")
        next(file)

        for row in file:
            cur.execute("insert into weather values(?, ?, ?, ?, ?, ?, ?)", row)

        conn.commit()
        conn.close()


    def calendar_db():
        conn = sqlite3.connect("data/team3.db")
        cur = conn.cursor()

        file = csv.reader(open("data/calendar_data.csv", "r"), delimiter=",")
        next(file)

        for row in file:
            cur.execute("insert into calendar values(?, ?, ?, ?, ?, ?, ?)", row)

        conn.commit()
        conn.close()