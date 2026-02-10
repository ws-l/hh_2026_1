import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Multi Page", layout="wide")

def page_home():
    st.title("Home")
    st.subheader("현황")    

#upload
def data_upload():   
    uploaded_file = st.file_uploader(label="Select a file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df.head(10))
        st.session_state["df"] = df
        st.success("데이터 저장 완료")

#explore
def data_eda():  
    tmp_df = st.session_state["df"]
    g = sns.pairplot(data=tmp_df )
    st.pyplot(g.fig)  

def data_eda2():  
    tmp_df = st.session_state["df"]
    fig, ax = plt.subplots()
    sns.heatmap(data=tmp_df.corr() )
    st.pyplot(fig)  

def data_eda3():
    tmp_df = st.session_state["df"]
    col_X = st.selectbox("X 선택",  tmp_df.columns.tolist())
    col_Y = st.selectbox("Y 선택",  tmp_df.columns.tolist())

    g = sns.jointplot(
        data=tmp_df,
        x=col_X,
        y=col_Y,
        kind="scatter"
    )
    st.pyplot(g.fig)

pages = {
    "Home": page_home,
    "Data upload": data_upload,
    "Data EDA-Pair Plot": data_eda,    
    "Data EDA-Heat Map": data_eda2,            
    "Data EDA-Joint Plot": data_eda3,                
}

st.sidebar.subheader("처리 선택")
choice = st.sidebar.selectbox("이동", list(pages.keys()))
pages[choice]()
