import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Multi Page", layout="wide")

def page_home():
    st.title("Home")
    st.write("작업 경로 내 api_data라는 폴더에 대해서 아래의 작업들을 해보세요.")
    st.write("데이터는 fastapi로 실행된 API로 부터 수집하세요.")

    #대상 디렉토리에 대한 현황을 출력해보세요

def page_data():
    st.title("Data")
    st.write("데이터 수집")
    #API로 부터 데이터를 수집해서 파일로 생성하거나 DB에 저장해보세요.
    r = requests.get("http://localhost:8001/data?row="+str(num))
    df = pd.DataFrame( r.json() )

def page_process():
    st.title("Preprocessing")
    st.write("데이터 전처리")
    #수집된 데이터에 대한 전처리를 적용해보세요.

def page_DB():
    st.title("DB")
    st.write("DB저장")
    #전처리된 데이터를 DB에 저장하고 현황을 출력해보세요.

pages = {
    "Home": page_home,
    "Data": page_data,
    "Preprocessing": page_process,
    "DB": page_DB,
}

st.sidebar.subheader("페이지 선택")
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
