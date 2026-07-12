#using it to do the preprocessing of the text input of the chat messages
import json
import pytz
import numpy as np
import pandas as pd
import seaborn as sns
import requests
import yake
import matplotlib.pyplot as plt
from RealtimeSTT import AudioToTextRecorder
# import voice_to_speech as vts

tz = pytz.timezone('Africa/Johannesburg')

text = ''

def process_text(text):
    print(text)

# maybe use the one shot to monologue and then the machine can try to predict what what the user is talking about 
def start_transcription():
    recorder = AudioToTextRecorder(
        transcription_engine="whisper_cpp",
        enable_realtime_transcription=True,
        model="tiny.en",
        device="cpu",
        beam_size=1,
    )

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print("Recording stopped by User...")
        exit(0)

#find a better more general keyword extractor (?)
# With custom parameters
custom_kw_extractor = yake.KeywordExtractor(
    lan="en",              # language
    n=2,                   # ngram size
    dedupLim=0.9,          # deduplication threshold
    dedupFunc='seqm',      # deduplication function
    windowsSize=1,         # context window
    top=2,                # number of keywords to extract
    features=None,         # custom features
    stopwords=None
)

#lower score means more importantrelevent a keyword is
keywords = custom_kw_extractor.extract_keywords(text)

keyword_list = ''
max_page_suggestions = 3

for word in keywords:
    keyword_list += (word[0]) + ','
    # print(word[0])

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
requestlink = response.url

# response.json() turns the recieved response into a python DS
data = response.json()

#dump turns python DS into a json string
results_json = json.dumps(data, indent=2)
# results_python = json.load(data)


print(requestlink)
# print(results_json)

results_json = json.dumps(data, indent=2)
# results_python = json.load(data)
#.split('.')[0] is used to remove the extra precision points in the time stamp 
df = pd.DataFrame()

def timestamp_now():
    return pd.to_datetime(pd.Timestamp.now('Africa/Johannesburg'))
# dataframe format 
entry_series = {
    'timestamp':                [timestamp_now()],
    'Main Topic':               [data['pages'][0]['title']],
    'Main Topic description':   [data['pages'][0]['description']],
    'Second Topic':             [data['pages'][1]['title']],
    'Second Topic description': [data['pages'][1]['description']]
    }

entry_series = pd.DataFrame(entry_series)

entry_series['Time'] = entry_series['timestamp'].dt.strftime("%H:%M:%S")
df = pd.concat([df, entry_series], ignore_index=True)

topic_timeline = df.copy()
topic_timeline["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(topic_timeline))]

fig, ax = plt.subplots(figsize=(18,9))

# here we are plotting a straight black line with the df['Time] values and the data points (with shape "-o" and in black) will be placed in their positions
# [0,]* len(df) is the y values for the graph(as a list), where we are telling it to put all the markers at y=0 for the length of the straight line
ax.plot(topic_timeline['Time'], [0,]* len(df), "-o", color="black", markerfacecolor="white")

ax.set_ylim(-7,7)

for idx in range(len(topic_timeline)):
    time, topic, level = topic_timeline["Time"][idx], topic_timeline["Main Topic"][idx], topic_timeline["Level"][idx]
    ax.annotate(topic, xy=(time, 0.1 if level>0 else -0.1),xytext=(time, level),
                arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),ha="center"
               );

ax.spines[["left", "top", "right", "bottom"]].set_visible(False)
ax.spines[["bottom"]].set_position(("axes", 0.5))
ax.yaxis.set_visible(False)
ax.set_title("Current conversation timeline", pad=10, loc="center", fontsize=25, fontweight="bold")
plt.show()

if __name__ == "__main__":
    capture_audio()
