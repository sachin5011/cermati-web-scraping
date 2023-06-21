import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import json
import pandas as pd
from urllib3.util.retry import Retry

pd.set_option('display.max_column', None)
# Starting URL
base_url = "https://www.cermati.com/karir/"
session = requests.Session()
retry = Retry(connect=100, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# response = requests.get(base_url)
response = session.get(base_url)
# print(response.text)
# Create a BeautifulSoup object
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)
data = soup.find('script', attrs={'id': "initials"})
data = data.text.replace("\n", ' ').strip('')
json_data = json.loads(data)
df = pd.DataFrame(pd.json_normalize(json_data['smartRecruiterResult'])["all.content"][0])

df = df[['name', 'location',  'department', 'typeOfEmployment', 'creator']]

department_list =df["department"].to_list()
department_list = [dict(t) for t in {tuple(d.items()) for d in department_list}]
response_json =[]
for department in department_list:
    if department:
        dep_df = df[df["department"] == department].reset_index(drop=True)
        dep_df = pd.concat([dep_df, dep_df["location"].apply(pd.Series)], axis=1)
        dep_df = pd.concat([dep_df, dep_df["typeOfEmployment"].apply(pd.Series)], axis=1)
        dep_df = dep_df.drop(columns= ["location", 'typeOfEmployment'])

        d_list = []

        for index, row in dep_df.iterrows():
            d_list.append({'title': row['name'], 'location': row['city'] + ", " + row['country'], "description": "",
                           "qualification":'', 'job_type': row['label'], 'postedBy': row['creator']})

        d_dict = {dep_df['department'][0]['label']: d_list}
        response_json.append(d_dict)

print(response_json)