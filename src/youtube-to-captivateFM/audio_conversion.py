from typing import Optional

from pydub import AudioSegment


def convert_wav_to_mp3(input_file: str, output_file: Optional[str] = None) -> str:
    """Convert WAV audio file to MP3.

    :param input_file: The file path of the WAV audio file to be converted.
    :type input_file: str
    :param output_file: The file path where the MP3 file will be saved. If not provided, the original file name will be used, with the '.wav' extension changed to '.mp3'.
    :type output_file: Optional[str], optional
    :return: The file path of the MP3 file.
    :rtype: str
    """
    if not output_file:
        output_file = input_file.rsplit(".", 1)[0] + ".mp3"

    sound = AudioSegment.from_wav(input_file)
    sound.export(output_file, format="mp3")

    return output_file


def combine_mp3_files(file1: str, file2: str) -> str:
    """Combine two mp3 files into one.

    :param file1: The path to the first mp3 file.
    :type file1: str
    :param file2: The path to the second mp3 file.
    :type file2: str
    :return: The combined audio.
    :rtype: AudioSegment
    """
    sound1 = AudioSegment.from_mp3(file1)
    sound2 = AudioSegment.from_mp3(file2)
    combined = sound1 + sound2
    new = file1.rsplit(".", 1)[0] + "(combined) .mp3"
    combined.export(new, format="mp3")
    return new
