from datetime import datetime
from sqlalchemy import create_engine, text
import streamlit as st
import pandas as pd
import os
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

#-------------------------------------------------------------------------------------------------#
#UI 구성

st.set_page_config(page_title="Multi Page", layout="wide")
def page_home():
    st.title("Home")
    st.subheader("현황")

#DB에 api_save 테이블에 저장
def page_db_save():
    if os.path.exists("api_backup") == False:
        os.mkdir("api_backup")

    st.title("DB저장")
    if st.button("DB저장 및 파일 정리"):
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
    "DB Save": page_db_save,
    "DB Select": page_db_select,
}

st.sidebar.subheader("처리 선택")
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
