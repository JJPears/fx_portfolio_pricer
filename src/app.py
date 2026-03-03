import pandas as pd
import os

from models.models import OptionTrade


INPUT_DATA_PATH = "/home/josh/coding/validus_takehome/src/tests/data/input_data"


input_file = os.path.join(INPUT_DATA_PATH, "fx_trades__1_.xlsx")

df = pd.read_excel(input_file, header=0, engine="calamine")


trades = [OptionTrade(**r) for r in df.to_dict("records")] # pyright: ignore[reportCallIssue]