from RealtimeSTT import AudioToTextRecorder

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
