import ffmpeg


def encode():
    video_path = 'Z:/Test/v.mkv'
    audio_path = 'Z:/Test/a.wav'
    output_file = 'Z:/Test/new.mkv'
    video_stream = ffmpeg.input(video_path)
    audio_stream = ffmpeg.input(audio_path)
    output_options = {
        "vcodec": "copy",
        "acodec": "aac",
        "audio_bitrate": "256k",
    }
    output = ffmpeg.output(video_stream['v'], audio_stream['a'], output_file, **output_options)
    ffmpeg.run(output)


encode()
