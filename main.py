#using it to do the preprocessing of the text input of the chat messages
import json
import requests
import keyboard
import pytz
import numpy as np
import pandas as pd
import seaborn as sns
import yake
import matplotlib.pyplot as plt
import os
from RealtimeSTT import AudioToTextRecorder

tz = pytz.timezone('Africa/Johannesburg')

# figure out a way to capture the things like text buffer and current word count without having them being caught up in the repeaping loop
# i think the way ive decided on is to have a switch that is true the first time it run then immediately turns false after init
# then when the word count has been reached then we reset the values and reset the bool var 

text_buffer = ''
keyword_list = []
word_count = 0
desired_word_count = 50

def initialize_the_dataframes():
    # make sure this runs once
    df = pd.DataFrame()
    topic_timeline = df.copy()

def timestamp_now():
    return pd.to_datetime(pd.Timestamp.now('Africa/Johannesburg'))

# AI did thi for me so i gotta read back and make a personal implementation fr
def random_level(i):
    """
    Random level whose range bound is driven by i.
    Even i -> negative value between -i and -2
    Odd  i -> positive value between 2 and i
    """
    limit = max(i, 3)  # keeps randint's low < high valid even when i is small (e.g. 0, 1, 2)
    return np.random.randint(-limit, -2) if i % 2 == 0 else np.random.randint(2, limit)

def format_response(data, p_length):

    entry_series = {
    'timestamp':                [timestamp_now()],
    'Main Topic':               [data['pages'][0]['title']],
    'Main Topic description':   [data['pages'][0]['description']],
    'Second Topic':             [data['pages'][1]['title']],
    'Second Topic description': [data['pages'][1]['description']],
    'Level':                    [random_level(5)]
    }

    entry_series = pd.DataFrame(entry_series)
    # entry_series["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(p_length)]


    entry_series['Time'] = entry_series['timestamp'].dt.strftime("%H:%M:%S")
    return entry_series

def visualise(p_timeline_df):

    fig, ax = plt.subplots(figsize=(18,9))

    ax.plot(p_timeline_df['Time'], [0,]* len(p_timeline_df), "-o", color="black", markerfacecolor="white")

    ax.set_ylim(-7,7)

    for idx in range(len(p_timeline_df)):
        time, topic, level = p_timeline_df["Time"][idx], p_timeline_df["Main Topic"][idx], p_timeline_df["Level"][idx]
        ax.annotate(topic, xy=(time, 0.1 if level>0 else -0.1),xytext=(time, level),
                    arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),ha="center"
                );

    ax.spines[["left", "top", "right", "bottom"]].set_visible(False)
    ax.spines[["bottom"]].set_position(("axes", 0.5))
    ax.yaxis.set_visible(False)
    ax.set_title("Current conversation timeline", pad=10, loc="center", fontsize=25, fontweight="bold")
    # plt.show()  
    # 
    fig.tight_layout()
    fig.savefig("./static/timeline.png", dpi=120)
    plt.close(fig)   
    return

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

    #why is DNS popping up as such a random error on myside, and then the thing just cra 
    # JSON string response object
    response = requests.get(url, headers=headers, params=params)
    response = response.json()



    return response
    # print(response.url)

def process_text(text):
    desired_word_count = 10
    global text_buffer
    global word_count

    # just check if the transcription section is empty
    if text != "":
        with open('transcription.txt', 'a') as file:
            file.writelines(text + "\n")
            file.close()   

        word_count += len(text.split())
        text_buffer += ' ' + text
        print("\n" + text + "\n")

        # only send the query after 100 words
        print("Word Count: " + str(word_count) + "\n")

        if word_count > desired_word_count:
            print("word count reached \n")
            # print("Text buffer: " + text_buffer + "\n")
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
            keywords = custom_kw_extractor.extract_keywords(text_buffer)

            text_buffer = ''
            word_count = 0
            global keyword_list

            for kw_score_pair in keywords:
                keyword_list.append(kw_score_pair[0])

            api_query_task('https://en.wikipedia.org/w/rest.php/v1/search/page', keyword_list, max_page_suggestions)


            # output_processed_text(keyword_list)
            return keyword_list, word_count
        else:
            print(f"api call will happen when word count is more than the desired word count: {desired_word_count}")
    else:
        print("Nothing transcribed\n")
        
# function to send out the keyword list to the api without having to terminate the whole function with the return keyword
# update: didnot work found a work around luckily. Focus on the concept not the technicalities
# def output_processed_text(p_recorder, p_process_funct):
#     return p_recorder.text(p_process_funct)



# maybe use the one shot to monologue and then the machine can try to predict what what the user is talking about 
def transcription():

    recorder = AudioToTextRecorder(
        transcription_engine="whisper_cpp",
        model="tiny.en",                    # final transcription
        language="en",                      # force this — skips language auto-detection        enable_realtime_transcription=True,
        realtime_model_type="tiny.en",      # keep same if already smallest, or try "tiny"
        realtime_processing_pause=0.4,      # increase this — fewer realtime passes = less CPU load
        device="cpu",
        beam_size=1,
        spinner=True,
        silero_sensitivity=0.5,
        webrtc_sensitivity=2,
        post_speech_silence_duration=0.6
        )
    
    # read the docs to figure out why this ⠋ speak now still lingers even after i recorder.abort() it or even Ctl+C it
    # so apparently this thing has a rouge thread runnning around even after i kill the  process
    #turns out its actually a thread hat doesnt .join() at the end of its work
    #fucking hell i turns out that i just didnt know that there was a recorder.shutdown() function, i kept trying .abort() and .stop()
    # no disrespect on the RTSTT dev but then im so confused on the functions Oh my Days!
    # but anyways "Google! Play me The Man by Aloe Blacc " 
    # edit: its tweaking out again when i put it back into the while loop
    # so i tried to throw everything i had at it and it just laughed in my face because when i removed .abort() and .stop() happening again then it kinda worked better at stopping the voice to txt
    # so its now working well, but its just the visuals that are fucked up
    # edit: i succumed to the jure of AI to fix the problem, father dont shun me. and whats worse is that it worked
    # lesson: dont get so hardstuck into the way that you wanna do it, open up your mind into other kinds of ways to do it, to might find that it helps your use case even better

    firstTime = True
    # make sure this runs once
    if firstTime == True:
        df = pd.DataFrame()
        topic_timeline = df.copy()

    while True:
        try:
            text = recorder.text()              # blocks until transcription is ready
            print("Transcribed:", text, "\n")

            keyword_list = process_text(text)   # use it right here
            response = api_query_task('https://en.wikipedia.org/w/rest.php/v1/search/page', keyword_list, max_page_suggestions)
            response_formatted = format_response(response, len(df))

            df = pd.concat([df, response_formatted], ignore_index=True)
            topic_timeline = df

            visualise(topic_timeline)

            if firstTime==False:
                firstTime=True

        except KeyboardInterrupt:
            recorder.shutdown()
            recorder.stop()
            # recorder.abort()
            print("\nRecording stopped by User...\n")
            return


if __name__ == "__main__":
    while True:
        u_input = ''
        print('-'*100)
        print("\n                                           where were we?...\n")
        print('-'*100)
        # print('Start of loop')

        # add a global settings menu perhaps??? for things like api link and desired word count
        u_input = input("Please Enter: \n    T to start tracking conversation \n    Q to quit the program entirely\n\n->  ").lower()
        
        if u_input == "t":
            # print('You Pressed T Key!')
            # starting the conversation recorder
            file = open('transcription.txt', 'a')
            file.writelines("\nStarting transcryption:...\n")
            file.close()
            # data flow must happen here mainly
        
            max_page_suggestions = 3
            transcription()
            
            print("right after transcription halt")

            pass
        elif u_input == 'q': 
            print('Thank you for trying to remember, im sure youll be back soon kkkkk...')
            # exiting the program
            exit(0) 
        else:
            print("\n...unrecognized key...\ntry again!!!")  # if user pressed a key other than the given key the loop will break

