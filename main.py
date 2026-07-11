#using it to do the preprocessing of the text input of the chat messages
import yake
import requests
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
from clock import scroll, flat

text = "Sources tell us that Google is acquiring Kaggle, a platform that hosts data science and machine learning competitions. Details about the transaction remain somewhat vague, but given that Google is hosting its Cloud Next conference in San Francisco this week, the official announcement could come as early as tomorrow. Reached by phone, Kaggle co-founder CEO Anthony Goldbloom declined to deny that the acquisition is happening. Google itself declined 'to comment on rumors'. Kaggle, which has about half a million data scientists on its platform, was founded by Goldbloom  and Ben Hamner in 2010. The service got an early start and even though it has a few competitors like DrivenData, TopCoder and HackerRank, it has managed to stay well ahead of them by focusing on its specific niche. The service is basically the de facto home for running data science and machine learning competitions. With Kaggle, Google is buying one of the largest and most active communities for data scientists - and with that, it will get increased mindshare in this community, too (though it already has plenty of that thanks to Tensorflow and other projects). Kaggle has a bit of a history with Google, too, but that's pretty recent. Earlier this month, Google and Kaggle teamed up to host a $100,000 machine learning competition around classifying YouTube videos. That competition had some deep integrations with the Google Cloud Platform, too. Our understanding is that Google will keep the service running - likely under its current name. While the acquisition is probably more about Kaggle's community than technology, Kaggle did build some interesting tools for hosting its competition and 'kernels', too. On Kaggle, kernels are basically the source code for analyzing data sets and developers can share this code on the platform (the company previously called them 'scripts'). Like similar competition-centric sites, Kaggle also runs a job board, too. It's unclear what Google will do with that part of the service. According to Crunchbase, Kaggle raised $12.5 million (though PitchBook says it's $12.75) since its   launch in 2010. Investors in Kaggle include Index Ventures, SV Angel, Max Levchin, Naval Ravikant, Google chief economist Hal Varian, Khosla Ventures and Yuri Milner "

# text = ' Using a cloud service, rather than running comparable software yourself, essentially outsources the operation of that software to the cloud provider. There are good arguments for and against cloud services. Cloud providers claim that using their services saves you time and money, and allows you to move faster compared to setting up your own infrastructure.'
# text = 'Cloud providers claim that using their services saves you time and money, and allows you to move faster compared to setting up your own infrastructure'
#i want to implement the cleaning myself butonly a bit later on

#find a better more general keyword extractor (?)
# With custom parameters
custom_kw_extractor = yake.KeywordExtractor(
    lan="en",              # language
    n=2,                   # ngram size
    dedupLim=0.9,          # deduplication threshold
    dedupFunc='seqm',      # deduplication function
    windowsSize=1,         # context window
    top=2,                 # number of keywords to extract
    features=None,         # custom features
    stopwords=None
)
#lower score means more importantrelevent a keyword is

keywords = custom_kw_extractor.extract_keywords(text)
keyword_list = ''
max_page_suggestions = 3

for word in keywords:
    keyword_list += (word[0]) + ','

#find a better API
url = 'https://en.wikipedia.org/w/rest.php/v1/search/page'
headers = {
    'User-Agent': 'MediaWiki REST API docs examples/0.1 (https://www.mediawiki.org/wiki/API_talk:REST_API)'
}
params = {
    'q': keyword_list,
    'limit': max_page_suggestions
}

response = requests.get(url, headers=headers, params=params)
requestlink = response.url

# response.json() turns the recieved response into a python DS
data = response.json()

#dump turns python DS into a json string
results_json = json.dumps(data, indent=2)
# results_python = json.load(data)

print(requestlink)
# print(results_json)

# dataframe format 
topic_timeline = {
    'datetime': [],
    'Main Topic':[],
    'Main Topic description':[],
    'Second Topic':[],
    'Second Topic description': []
    }

pd.DataFrame(topic_timeline)
print(topic_timeline)