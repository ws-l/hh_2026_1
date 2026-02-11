from datetime import datetime
from prefect import flow, task
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine, text
from sklearn.compose import ColumnTransformer, make_column_selector as selector
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

import streamlit as st
import pandas as pd
import requests
import os
import pickle
import shutil as sh

#task 정의 
@task
def preprocess1()-> pd.DataFrame:
    files = os.listdir("api_data")
    result = pd.DataFrame()
    for file in files:
        if file.endswith(".csv"):
            temp = pd.read_csv( os.path.join("api_data", file) )
            result = pd.concat([result, temp], ignore_index=True)   
    
    return result


@task
def preprocess2(df: pd.DataFrame, target: str) -> pd.DataFrame:
    with open("pipeline.pkl", "rb") as f:
        saved = pickle.load(f)
    pipe = saved["pipeline"]

    X = df.drop(columns=[target])    
    y = df[target]

    X_piped = pipe.fit_transform(X)
    df = pd.DataFrame(X_piped)#, columns=X.columns) 
    df[target] = y.values         

    
    return df


@flow
def preprocessing(target: str):
    df = preprocess1()
    df = preprocess2(df, target)

    
#-------------------------------------------------------------------------------------------------#
#UI 구성

st.set_page_config(page_title="Multi Page", layout="wide")
def page_home():
    st.title("Home")

#-------------------------------------------------------------------------------------------------#
def page_data():   
    if os.path.exists("api_data") == False:
        os.mkdir("api_data")
    
    st.title("API Data 수집")            
    num = st.slider("수집할 데이터 개수", min_value=10, max_value=100, value=50, step=10, key="num_rows")
    
    if st.button("Collect"):
        r = requests.get("http://localhost:8001/data?row="+str(num))
        df = pd.DataFrame( r.json() )

        st.subheader("CSV 저장")
        df["date_collected"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #date컬럼 추가
        df.to_csv("api_data/data_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".csv", index=False)


#-------------------------------------------------------------------------------------------------#
def page_process():
    st.title("데이터 전처리")  
    name = st.text_input(label = "target 컬럼 이름을 입력하세요", value="Pass.Fail")
    
    if st.button("Preprocessing"):
        preprocessing(name)

#-------------------------------------------------------------------------------------------------#
pages = {
    "Home": page_home,
    "Data Collect": page_data,
    "Preprocessing": page_process,
}

st.sidebar.subheader("처리 선택")
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
