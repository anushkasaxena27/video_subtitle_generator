import streamlit as st
import pvleopard
from pytube import YouTube
from typing import *
import os

st.header("Video Subtitle Generator")

def download_video(url, save_path='downloads/audio.mp3'):
    youtube = YouTube(url)
    audio_stream = youtube.streams.filter(only_audio=True, audio_codec='opus').order_by('bitrate').last()
    audio_stream.download(output_path=os.path.dirname(save_path),filename=os.path.basename(save_path))

def generate_transcript(path_to_audio=None):
    if os.path.exists(path_to_audio):
        leopard = pvleopard.create(access_key="tzvr0xRhwpxvhHfWvpEy6WlxjivG1hPWohXg+hETeOx8jFz8Wqb/qw==")
        transcript, words = leopard.process_file(path_to_audio)
        return (transcript,words)
    else:
        print("Please provide valid path to audio file")

def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)


    return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)


def to_srt(
        words: Sequence[pvleopard.Leopard.Word],
        endpoint_sec: float = 1.,
        length_limit: Optional[int] = 16) -> str:
    def _helper(end: int) -> None:
        lines.append("%d" % section)
        lines.append(
            "%s --> %s" %
            (
                second_to_timecode(words[start].start_sec),
                second_to_timecode(words[end].end_sec)
            )
        )
        lines.append(' '.join(x.word for x in words[start:(end + 1)]))
        lines.append('')


    lines = list()
    section = 0
    start = 0
    for k in range(1, len(words)):
        if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                (length_limit is not None and (k - start) >= length_limit):
            _helper(k - 1)
            start = k
            section += 1
    _helper(len(words) - 1)


    return '\n'.join(lines)


def save(location='subtitles.srt',words=None):
    with open(location, 'w') as f:
        f.write(to_srt(words))

option = st.radio('Select an option',['Enter a youtube URL','Upload an audio file'])

if option == 'Enter a youtube URL':
    url = st.text_input('Paste a youtube URL')
    submit = st.button('Download')
    if submit:
        download_video(url)
        transcript,words = generate_transcript(f'downloads/audio.mp3')
        save(location='transcripts/subtitles.srt',words = words)
        st.success("Transcript generated successfully")
        st.write(transcript)
        st.download_button('Download subtitles',data='transcripts/subtitles.srt',
            file_name='your_subtitle.srt')

else:
    audio = st.file_uploader('Upload an audio file')
    if audio:
        submit = st.button('Generate')
        if submit:
            transcript,words = generate_transcript(audio)
            save(location=f'transcripts/subtitles.srt',words=words)
            st.success("Transcript generated successfully")
            st.write(transcript)
            st.download_button('Download subtitles',data='transcripts/subtitles.srt',
                file_name='your_subtitle.srt')




