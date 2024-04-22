# import torch
# import torchaudio
# from typing import Union

# # CURRENTLY AS OF LATEST DATE NOT WORKING! AND NOT NEEDED :)
# class SilenceDetector:
#     def __init__(self):
#         self.silence_counter = 0
#         self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)
#         print(utils)
#         self.get_speech_ts, *rest = utils

#     def is_silent(self, audio_path: str) -> bool:
#         waveform, sample_rate = torchaudio.load(audio_path)
#         speech_timestamps = self.get_speech_ts(waveform, self.model, sampling_rate=sample_rate)

#         if not speech_timestamps:
#             self.silence_counter += 1
#         else:
#             self.silence_counter = 0

#         return self.silence_counter >= 2

# # Example usage
# # detector = SilenceDetector()
# # print(detector.is_silent('path_to_1_second_audio.wav'))
