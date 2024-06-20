from typing import Dict

import pandas as pd
from fastapi import FastAPI
import uvicorn
from logger import logger

HOST = '127.0.0.1'
PORT = 8080


hedge_df = pd.DataFrame(columns=["volume", "side"])
app = FastAPI()


@app.get("/new_position/")
def add_position(params: Dict):
    logger.info(f"DC received a new trade: {params}")
    symbol = params["symbol"]
    volume = params["volume"]
    side = params["side"]
    if symbol in hedge_df.index:
        hedge_df.loc[symbol, "volume"] += volume
    else:
        hedge_df.loc[symbol, "volume"] = volume
        hedge_df.loc[symbol, "side"] = side
    print(hedge_df)
    return {"message": "success"}


@app.get("/all_positions/")
def get_all_positions():
    data_json = hedge_df.to_json(orient='index', lines=False)
    return data_json


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )
