import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_selector as selector
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
#아래 내용을 binary.csv에 적용하세요, target: admit (1은 합격,,)
with open("pipeline.pkl", "rb") as f:
     loaded = pickle.load(f)  #dictionary
pipe3 = loaded["pipeline"]
df = pd.read_csv("binary.csv")
X = df.drop("admit", axis=1)
y = df.admit
pipe3.fit(X, y)

from fastapi import FastAPI
app = FastAPI()

#localhost:8000/predict?age=20
@app.get("/predict")
def predict(gre: float, gpa:float, rank:float):
    tmp=pipe3.predict(
        pd.DataFrame({"gre":[gre],"gpa":[gpa],"rank":[rank]})) 
    if tmp==1:      
        return {"result":"admit"}  #결과 부분에 입력값도 반영해서 출력
    else:
        return {"result":"fail"}
