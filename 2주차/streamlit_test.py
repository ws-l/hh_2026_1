import streamlit as st
import pandas as pd
st.title("기본 UI 예제")
name = st.text_input("파일명을 입력하세요")
if name.endswith(".csv"): #os.path.exists(파일명)
    if st.button("파일읽기"):
        df = pd.read_csv(name)
        st.dataframe( df.describe() )
        row = st.slider("행 위치", 0, df.shape[0], 25)
        st.subheader("데이터프레임")
        st.dataframe( df.iloc[row:row+5, :] )
        if st.button("export"):
             df.describe().to_parquet("export.parquet")