from sklearn.model_selection import train_test_split
from unicodedata import category
import pandas as pd

class Train_Encoding():
    def __init__(self, df):
        self.df = df
        
    #결측치 제거
    def drop(self):
        df = self.df
        df = df.dropna()

        return df

    def seperate(self):
        df = self.drop()
        lunch = df.loc[:, ['datetime', 'season', 'year', 'month', 'date', 'weekdays', 'vacation', 'worker_number', 'real_number', 'vacation_number', 'biztrip_number', 'overtime_number', 'telecom_number', 'temperature', 'rain', 'wind', 'humidity', 'discomfort_index', 'perceived_temperature', 'lunch_rice', 'lunch_soup', 'lunch_main', 'new_lunch', 'lunch_number']]
        dinner = df.loc[:, ['datetime', 'season', 'year', 'month', 'date', 'weekdays', 'vacation', 'worker_number', 'real_number', 'vacation_number', 'biztrip_number', 'overtime_number', 'telecom_number', 'temperature', 'rain', 'wind', 'humidity', 'discomfort_index', 'perceived_temperature', 'dinner_rice', 'dinner_soup', 'dinner_main', 'new_dinner', 'dinner_number']]

        return lunch, dinner

    #밥, 국, 메인반찬은 종류가 onehot encoding시 너무 복잡해집니다. 그래서 일반 밥과 특식 밥 메뉴 둘로 나눴고 Y, N으로 구분해줍니다.
    def rice_lunch(self):
        lunch = self.seperate()[0]
        for index in lunch.index:
            if lunch['lunch_rice'][index] == "밥":
                lunch['lunch_rice'][index] = "Y"
            else:
                lunch['lunch_rice'][index] = "N"
        
        del lunch['lunch_soup']
        del lunch['lunch_main']

        return lunch
        
    def rice_dinner(self):
        dinner = self.seperate()[1]
        for index in dinner.index:
            if dinner['dinner_rice'][index]== "밥":
                dinner['dinner_rice'][index] = "Y"
            else:
                dinner['dinner_rice'][index] = "N"
        
        del dinner['dinner_soup']
        del dinner['dinner_main']
        
        return dinner

    
    #훈련 성능을 위해 원핫인코딩 진행합니다.
    #추가적으로 MinMax Scalar, Feature Scaling 같은 정규화 작업도 추가해주면 좋을 듯합니다.
    def onehot_lunch(self):
        lunch = self.rice_lunch()

        # time = ["year", "month", "date"]
        # for col in time:
            # lunch[col] = lunch[col].astype('category')

        lunch = pd.get_dummies(lunch)

        # for col in time:
            # lunch[col] = lunch[col].astype(int)
        
        return lunch
    
    def onehot_dinner(self):
        dinner = self.rice_dinner()

        # time = ["year", "month", "date"]
        # for col in time:
            # dinner[col] = dinner[col].astype('category')

        dinner = pd.get_dummies(dinner)

        # for col in time:
            # dinner[col] = dinner[col].astype(int)

        return dinner


    ### split은 진행하지 않겠습니다. XGBR은 시계열 분석이 아니니 순서가 관계없으나, LSTM은 시계열분석이라 순서가 중요한 변수가 됩니다.
    ### 그래서 split은 XGBR, LSTM 단계에서 진행되도록 만들겠습니다. 
     
    # 최종적으로 훈련용과 테스트용으로 데이터를 나누는 함수입니다. 랜덤하게 뽑기 위해 sklearn에 train_test_split 사용했습니다.
    # def split_lunch(self):
    #     lunch_data = self.onehot_lunch().drop("lunch_number", axis = "columns")
    #     lunch_target = self.onehot_lunch()['lunch_number']
    #     lunch_X_train, lunch_X_test, lunch_y_train, lunch_y_test = train_test_split(lunch_data, lunch_target)

    #     return lunch_X_train, lunch_X_test, lunch_y_train, lunch_y_test

    # def split_dinner(self):
    #     dinner_data = self.onehot_dinner().drop("dinner_number", axis = "columns")
    #     dinner_target = self.onehot_dinner()['dinner_number']
    #     dinner_X_train, dinner_X_test, dinner_y_train, dinner_y_test = train_test_split(dinner_data, dinner_target)

    #     return dinner_X_train, dinner_X_test, dinner_y_train, dinner_y_test


    # 형태를 변경해줘야하는건 train 데이터만
    # split_lunch와 split_dinner에서 train 데이터만 뽑아오는게 효율적일까? 유지보수 측면에서 불리하지 않울까?