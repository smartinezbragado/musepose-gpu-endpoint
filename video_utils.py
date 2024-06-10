import numpy as np
from PIL import Image
from loguru import logger
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, VideoClip, ImageSequenceClip
)

def load_video_and_audio(video_path, audio_path):
    """Load video and audio files."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    return video, audio

def loop(video, audio):
    """Loop video to match audio duration and set audio."""
    video = video.loop(duration=audio.duration)
    return video

def crop_video(video):
    """Crop video."""
    width, height = video.size
    part_width = width // 3
    right_video = video.crop(x1=2*part_width, y1=0, x2=width, y2=height)
    return right_video

def add_image_clip_to_video(video, img_path, duration: float):
    """Add the image clip to the video."""
    image_clip = ImageClip(img_path, duration=duration)
    image_clip = image_clip.resize(video.size)
    blend_clip = VideoClip(make_frame=lambda t: (1-t/duration)*image_clip.get_frame(t) + t/duration*video.get_frame(t), duration=duration)
    return blend_clip

def combine_clips(blend_clip, right_video, offset: float):
    """Combine clips and write final video to disk."""
    final_video = CompositeVideoClip([blend_clip, right_video.set_start(offset)])
    return final_video

def add_watermark_to_video(
    video: str, 
    watermark_path: str, 
    output_path: str, 
    watermark_width: int=100, 
    offset: int=20
) -> None:
    """
    Adds a watermark to a video file and saves the resulting video with the watermark.

    Args:
        video_path (str): The path to the input video file.
        watermark_path (str): The path to the watermark image file.
        output_path (str): The path to save the output video file with the watermark.
        watermark_width (int, optional): The width of the watermark image in pixels. Defaults to 100.
        offset (int, optional): The offset in pixels from the corners of the video. Defaults to 20.

    Returns:
        None
    """
    watermark = ImageClip(watermark_path)
    watermark = watermark.resize(width=watermark_width)
    watermark = watermark.set_duration(video.duration)

    def watermark_position(t):
        y_offset = offset
        x_offset = offset
        return x_offset, y_offset

    watermark = watermark.set_position(watermark_position)

    video_with_watermark = CompositeVideoClip([video, watermark])
    video_with_watermark = video_with_watermark.set_audio(video.audio)
    video_with_watermark = video_with_watermark.set_duration(video.duration)
    
    video_with_watermark.write_videofile(
        output_path,
        codec='libx264',
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

            
def extract_audio_from_video(path: str, audio_path: str) -> None:
    reference_video = VideoFileClip(path)
    reference_audio = reference_video.audio
    reference_audio.write_audiofile(audio_path)


def remove_background_from_image(pipe, image_path: str, output_path: str):
    logger.info("Removing background from image")
    img = Image.open(image_path)
    img_without_bg = pipe(img)
    img_without_bg.save(output_path)

def remove_background_from_video(pipe, video_path: str, output_path: str):
    import time
    start_time = time.time()
    
    logger.info("Removing background from video")
    video = VideoFileClip(video_path)
    
    frames = []
    for frame in video.iter_frames():
        img = Image.fromarray(frame)
        img_without_bg = pipe(img)
        frames.append(np.array(img_without_bg))
    
    new_video = ImageSequenceClip(frames, fps=video.fps)
    new_video.write_videofile(output_path, codec='libx264')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Background removal completed in {elapsed_time:.2f} seconds")
