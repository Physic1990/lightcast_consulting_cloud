#Models must take data files as arguments and print results to stdout

import sys
import pandas as pd

df = pd.read_excel(sys.argv[1], sheet_name=None)
processed_data = {}

for sheet_name, data in df.items():
    #The below is unique to each model
    if data.shape[1] >= 2:
        data["Mean"] = data.iloc[:, :2].mean(axis=1)

        processed_data[sheet_name] = data
    #End unique section

with pd.ExcelWriter(sys.argv[2], engine="openpyxl") as writer:
    for sheet, data in df.items():
        data.to_excel(writer, sheet_name=sheet, index=False)

print(processed_data)