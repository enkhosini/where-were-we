
#find a better more general keyword extractor (?)
# With custom parameters


#lower score means more importantrelevent a keyword is

#find a better API
def api_query_task(api_url,keyword_list =["Rick Roll"], max_page_suggestions=3):
    url = api_url

    headers = {
        'User-Agent': 'MediaWiki REST API docs examples/0.1 (https://www.mediawiki.org/wiki/API_talk:REST_API)'
    }
    params = {
        'q': keyword_list,
        'limit': max_page_suggestions
    }

    # JSON string response object
    response = requests.get(url, headers=headers, params=params)
    print(response)

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
def initializr_the_dataframes():
    # make sure this runs once
    df = pd.DataFrame()
    topic_timeline = df.copy()

def timestamp_now():
    return pd.to_datetime(pd.Timestamp.now('Africa/Johannesburg'))

def add_entry_to_df():
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

def add_levels_to_new_entry():
    topic_timeline["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(topic_timeline))]

def draw_timeline(topic_timeline, df):
    fig, ax = plt.subplots(figsize=(18,9))

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
