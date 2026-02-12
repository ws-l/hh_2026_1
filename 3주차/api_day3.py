from fastapi import FastAPI
import pandas as pd
import numpy as np

app = FastAPI()

df = pd.read_csv("data.csv")


@app.get("/data")
def date_gen(row: int = 50):
    x = df.sample(row)
    #na 추가
    n_missing = 10
    rows = np.random.randint(0, x.shape[0], n_missing)
    cols = np.random.randint(0, x.shape[1], n_missing)
    for r, c in zip(rows, cols):
        x.iloc[r, c] = np.nan
    x = x.replace({np.nan: None})
    return  x.to_dict(orient="records")
