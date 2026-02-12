import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Multi Page", layout="wide")

def page_home():
    st.title("Home")
import os
def page_process():
    st.title("Preprocessing")
    #읽혀진 csv는 parquet로 생성해주셔서, 나중에 덕db에서 읽어보세요.
    result = pd.DataFrame()
    for i in os.listdir():
        if i.startswith("api_123_"):
            tmp = pd.read_csv(i)
            tmp.to_parquet(i+".parquet")
            result = pd.concat([result,tmp])
            pd.DataFrame({"file":[i],
                          "time":[datetime.now().strftime("%H")]}).to_sql(
                              "test5", create_engine("sqlite:///s.db"),
                              if_exists="append", index=False
                          )
    result.to_sql()
from datetime import datetime
from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql+psycopg2://postgres:12345@localhost:5432/postgres')
def page_data():
    time = datetime.now().strftime("%H_%M_%S")
    num = st.slider("choose row:",1, 10, 5)

    if st.button("click"):
        r = requests.get("http://localhost:8001/data?row="+str(num))
        df = pd.DataFrame( r.json() )
        df.to_csv("api_123_"+time+".csv")
        df.to_sql("test", engine, schema="public",
                  if_exists="append", index=False)
        st.dataframe( df )

def page_DB():
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="public")
    table = st.selectbox("table: ", tables)
    st.dataframe( pd.read_sql_query("select * from "+table, engine) )

st.sidebar.subheader("페이지 선택")
pages = {
    "Home": page_home,
    "Data": page_data,
    "Preprocessing": page_process,
    "DB": page_DB,
}
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
