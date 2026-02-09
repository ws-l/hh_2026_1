from datetime import datetime
from prefect import flow, task, get_run_logger
from prefect.context import get_run_context
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
import sqlite3
import pickle
import shutil as sh

#-------------------------------------------------------------------------------------------------#
#DB 연결 설정
DB_INFO = {
    "user": "postgres",
    "password": "12345",
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
}

engine = create_engine(
    "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**DB_INFO)
)
engine_log = create_engine("sqlite:///example.db")

#-------------------------------------------------------------------------------------------------#
#task 정의 
@task
def preprocess1()-> pd.DataFrame:
    files = os.listdir("api_data")
    result = pd.DataFrame()
    for file in files:
        if file.endswith(".csv"):
            temp = pd.read_csv( os.path.join("api_data", file) )
            result = pd.concat([result, temp], ignore_index=True)
    
    pd.DataFrame({"process_time": [datetime.now().strftime("%Y_%m_%d_%H_%M_%S")],
                           "process": ["data collection"],
                           "processed_rows": [result.shape[0]],}).to_sql("api_logs",engine_log, if_exists="append",  index=False)
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

    pd.DataFrame({"process_time": [datetime.now().strftime("%Y_%m_%d_%H_%M_%S")],
                           "process": ["missing value handling & scaling"],
                           "processed_rows": [df.shape[0]],}).to_sql("api_logs",engine_log, if_exists="append",  index=False)
    
    return df


#PCA
@task(cache_policy=None)
def preprocess3(df: pd.DataFrame, target: str) -> pd.DataFrame:

    X = df.drop(columns=[target])
    y = df[target]

    pca = PCA(n_components=0.95, random_state=42)  # 누적 설명력 95% 되게끔 자동 선택
    X_pca = pca.fit_transform(X)
    df = pd.DataFrame(X_pca, columns=["PCA_"+str(i+1) for i in range(X_pca.shape[1])])
    df[target] = y.values
    
    pd.DataFrame({"process_time": [datetime.now().strftime("%Y_%m_%d_%H_%M_%S")],
                           "process": ["PCA"],
                           "processed_rows": [df.shape[0]],}).to_sql("api_logs",engine_log, if_exists="append",  index=False)

    return df

@task(cache_policy=None) #컬럼 타입이 섞인 경우, prefect가 caching을 못하면서 오류 메시지->캐시를 끄기
def preprocess4(df: pd.DataFrame):

    df.to_csv("preprocessed_data_"+datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+".csv", index=False)

    pd.DataFrame({"process_time": [datetime.now().strftime("%Y_%m_%d_%H_%M_%S")],
                           "process": ["file save"],
                           "processed_rows": [df.shape[0]],}).to_sql("api_logs",engine_log, if_exists="append",  index=False)

    df_check = pd.read_sql_query("SELECT * FROM api_logs", engine_log)
    st.dataframe(df_check)

@flow
def preprocessing(target: str):
    logger = get_run_logger()
    logger.info("Starting flow")
    df = preprocess1()
    logger.info(f"Data collected with shape: {df.shape}")
    df = preprocess2(df, target)
    logger.info("Missing values / Scaling handled")
    df = preprocess3(df, target)
    logger.info("PCA applied")
    preprocess4(df)
    logger.info("Preprocessed data saved")

#-------------------------------------------------------------------------------------------------#
#UI 구성

st.set_page_config(page_title="Multi Page", layout="wide")
def page_home():
    st.title("Home")
    st.subheader("현황")
    st.write("Time: "+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.write("Target Directory:"+os.getcwd()+"\\api_data")       
    st.write("디렉토리 내 파일개수: " + str(len( [i for i in os.listdir("api_data") if i.endswith(".csv") ] ) ) )


#-------------------------------------------------------------------------------------------------#
def page_data():   
    if os.path.exists("api_data") == False:
        os.mkdir("api_data")
    
    st.title("API Data 수집")            
    num = st.slider("수집할 데이터 개수", min_value=10, max_value=100, value=50, step=10, key="num_rows")
    
    if st.button("Collect"):
        r = requests.get("http://localhost:8001/data?row="+str(num))
        df = pd.DataFrame( r.json() )
        st.subheader("요약정보")
        st.dataframe( df.describe() )
        st.subheader("Missing Info")
        st.dataframe( df.isnull().mean().sort_values(ascending=False) )     

        st.subheader("CSV 저장")
        df["date_collected"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #date컬럼 추가
        df.to_csv("api_data/data_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".csv", index=False)
        st.write( "디렉토리 내 파일개수: " + str(len( [i for i in os.listdir("api_data") if i.endswith(".csv") ] ) ) )

#-------------------------------------------------------------------------------------------------#
def page_process():
    st.title("데이터 전처리")  
    name = st.text_input(label = "target 컬럼 이름을 입력하세요", value="Pass.Fail")
    
    if st.button("Preprocessing"):
        st.write("전처리 시작")
        preprocessing(name)
        st.write("전처리 로그 기록 완료")        


#-------------------------------------------------------------------------------------------------#
#DB에 api_save 테이블에 저장
def page_db_save():
    if os.path.exists("api_backup") == False:
        os.mkdir("api_backup")

    st.title("DB저장")
    if st.button("DB저장 및 파일 정리"):
        st.write("데이터 DB에 추가 및 처리된 파일 백업폴더 이동")
        #api_data 폴더 내 csv를 하나씩 읽어서 테이블에 추가, 읽은 파일은 다른 폴더로 이동
        files = os.listdir("api_data")
        cnt = 0
        for i in files:
            if i.endswith(".csv"):
                df = pd.read_csv( os.path.join("api_data", i) )
                cnt = cnt + df.shape[0]
                df.to_sql(
                name="api_save",   # 테이블명
                con=engine,
                schema="public",       # 기본 스키마
                if_exists="append",   # 'fail' | 'replace' | 'append'
                index=False
                )
                sh.move( os.path.join("api_data", i), os.path.join("api_backup", i) )        
                st.write( i + " 파일이 처리되었습니다." )
        st.write(str(cnt)+"개의 행이 DB에 추가")

#-------------------------------------------------------------------------------------------------#
#db 확인
def page_db_select():
    st.title("DB 조회")
    if st.button("DB조회"):
        query = "SELECT * FROM api_save"
        df = pd.read_sql_query(query, engine)
        st.subheader("요약정보")  
        with engine.connect() as conn:
            row_count = conn.execute(
                text("SELECT COUNT(*) FROM public.api_save")
            ).scalar()
            st.write("테이블 row 수:", row_count)
        st.subheader("첫5행")
        st.dataframe(df.head())

#-------------------------------------------------------------------------------------------------#

pages = {
    "Home": page_home,
    "Data Collect": page_data,
    "Preprocessing": page_process,
    "DB Save": page_db_save,
    "DB Select": page_db_select,
}

st.sidebar.subheader("처리 선택")
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
