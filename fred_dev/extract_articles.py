from src.yololo.utils import rss
from collections import defaultdict
import pandas as pd

link = 'https://www.theguardian.com/international/rss'

docus = rss.read_feed(link)

dict_data=defaultdict(dict)

for i, docu in enumerate(docus):

    dict_data[i]['title'] = docu.title
    dict_data[i]['link'] = docu.link
    dict_data[i]['content'] = docu.content

df=pd.DataFrame().from_dict(dict_data, orient='index')
df.to_csv('dataset_pandas.tsv', sep='\t')