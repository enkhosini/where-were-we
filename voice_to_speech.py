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

# if __name__ == "__main__":
#     recorder = AudioToTextRecorder(
#     transcription_engine="whisper_cpp",
#     model="tiny.en",
#     device="cpu",
#     beam_size=5,
#     transcription_engine_options={
#         "model": {
#             "n_threads": 8,
#             "redirect_whispercpp_logs_to": None,
#         },
#     },
#     enable_realtime_transcription=True,
#     realtime_transcription_engine="whisper_cpp",
#     realtime_model_type="tiny.en",
#     beam_size_realtime=1,
#     realtime_processing_pause=0.15,
#     realtime_transcription_engine_options={
#         "model": {
#             "n_threads": 8,
#             "redirect_whispercpp_logs_to": None,
#         },
#         "transcribe": {
#             "single_segment": True,
#             "no_context": True,
#             "print_timestamps": False,
#         },
#     },)