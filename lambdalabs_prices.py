from io import StringIO
import pandas as pd
import requests

# Get the html
url = 'https://lambdalabs.com/service/gpu-cloud'
html = StringIO(requests.get(url).text)

# Get the tables as a list of DataFrames
dfs = pd.read_html(html)

# Detect the good table

indexes = [i for i, df in enumerate(dfs) if 'VRAM / GPU' in df.columns]

assert len(indexes) == 1, 'Multiple valid tables found in html'  # Asserts only one good table is available

df = dfs[indexes[0]]

df['GPU Count'] = df['GPUs'].str.split('x').str[0].astype(int)  # Get GPU count as int (1st number on GPU Count column)
df['VRAM / GPU'] = df['VRAM / GPU'].str.split().str[0].astype(int)  # Get VRAM / GPU as int
df['PRICE'] = df['PRICE*'].str.split().str[0].str[1:].astype(float)  # Get price as float (separated from $ sign)

df['Full VRAM'] = df['GPU Count'] * df['VRAM / GPU']  # Count the full VRAM on the machine
df['Price / 100GB'] = (df['PRICE'] / (df['Full VRAM'] / 100)).round(2)  # Get the price per 100GB of VRAM
df = df.sort_values(by=['Price / 100GB', 'GPU Count'])  # Sort the dataframe per price/100GB

df['Price / 100GB'] = df['Price / 100GB'].astype(str) + ' $/h/100GB'  # Reformat price/100GB

df.drop(columns=['PRICE', 'GPU Count'])  # Remove useless columns

df.to_csv('output.csv', index=False)  # Save dataframe

md_table = df.to_markdown(index=False)  # Convert df to md table format

with open('readme.txt', 'r') as file:
    readme_content = file.read()

readme_content += md_table  # Append the MD table to the README.md content

with open('README.md', 'w') as file:
    file.write(readme_content)  # output
