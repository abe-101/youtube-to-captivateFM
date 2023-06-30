import subprocess
from typing import Optional

from pydub import AudioSegment


def normalize_volume(file_path: str, target_dBFS: float = -15.0) -> str:
    sound = AudioSegment.from_mp3(file_path)
    change_in_dBFS = target_dBFS - sound.dBFS
    normalized_sound = sound.apply_gain(change_in_dBFS)

    # Export the normalized sound and overwrite the original file
    normalized_sound.export(file_path, format="mp3")

    # Print the process
    print(f"Normalized volume of '{file_path}' to {target_dBFS} dBFS.")
    print(f"Overwrote the original file '{file_path}' with the normalized audio.")

    return file_path



def create_video_from_audio_and_picture(audio_file: str, image_file: str, video_file: str) -> str:
    """
    Creates a video from an audio file and an image file, and saves the video as a new file.

    Args:
        audio_file (str): The path to the audio file.
        image_file (str): The path to the image file.
        video_file (str): The path to save the video file.

    Returns:
        str: The name of the created video file.

    Raises:
        ValueError: If either the audio or image file does not exist.

    """

    ffmpeg_command = [
        "ffmpeg",
        "-loop",
        "1",
        "-y",  # Overwrite output file without asking
        "-i",
        image_file,
        "-i",
        audio_file,
        "-shortest",
        video_file,
    ]
    subprocess.run(ffmpeg_command)


    return video_file


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
    new = file1.rsplit(".", 1)[0] + " (combined).mp3"
    combined.export(new, format="mp3")
    return new


def combine_webm_files(input_file1: str, input_file2: str, output_file: str = None) -> None:
    """
    Combine two WebM audio files into a single file.

    :param input_file1: Path to the first WebM audio file to combine.
    :type input_file1: str
    :param input_file2: Path to the second WebM audio file to combine.
    :type input_file2: str
    :param output_file: Path to the output audio file.
    :type output_file: str
    """
    # Load the input files using Pydub.
    sound1 = AudioSegment.from_file(input_file1, format="webm")
    sound2 = AudioSegment.from_file(input_file2, format="webm")

    # Combine the two audio segments using Pydub.
    combined_sound = sound1 + sound2

    if output_file is None:
        output_file = input_file1.rsplit(".", 1)[0] + " (combined).webm"

    # Export the combined audio as a WebM file using Pydub.
    combined_sound.export(output_file, format="webm")
    return output_file
