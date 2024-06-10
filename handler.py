import os
import glob
import shutil
import runpod
import requests
import warnings
from PIL import Image
from loguru import logger
from transformers import pipeline
from schemas import AnimationPayload
from firebase_utils import download_firebase_file, upload_firebase_file
from video_utils import (
    loop,
    load_video_and_audio,
    add_watermark_to_video,
    extract_audio_from_video,
    remove_background_from_image,
    remove_background_from_video
)

warnings.filterwarnings("ignore")

brackground_remover_pipe = pipeline(
    "image-segmentation", 
    model="briaai/RMBG-1.4", 
    trust_remote_code=True,
    device=0
)

def handler(event: dict):  
    try:  
        # Parse payload
        payload = AnimationPayload(**event["input"])
        logger.info(f"Payload: {str(payload)}")
        
        # Download motion sequence and refenrence image from firebase
        image_type = payload.reference_image.split('.')[-1]
        reference_img_path = os.path.join("assets", "images", f"reference_image.{image_type}")
        download_firebase_file(
            bucket=os.environ["BUCKET"], 
            firebase_filename=payload.reference_image, 
            local_filename=reference_img_path
        )

        if image_type != "png":
            img = Image.open(reference_img_path)
            reference_img_path_png = os.path.join("assets", "images", "reference_image.png")
            img.save(reference_img_path_png, "PNG")
            reference_img_path = reference_img_path_png

        motion_sequence_path = os.path.join("assets", "poses", "align", f"img_ref_video_dance.mp4")
        audio_path = os.path.join("assets", "audios", f"background_audio.{payload.audio_file.split('.')[-1]}")

        if payload.motion_sequence:
            os.makedirs(os.path.join("assets", "poses", "align"), exist_ok=True)
            download_firebase_file(
                bucket=os.environ["BUCKET"], 
                firebase_filename=payload.motion_sequence, 
                local_filename=motion_sequence_path
            )

            download_firebase_file(
                bucket=os.environ["BUCKET"], 
                firebase_filename=payload.audio_file, 
                local_filename=audio_path
            )

        else:
            reference_video_path = os.path.join("assets", "videos", f"reference_video.{payload.reference_video.split('.')[-1]}")
            download_firebase_file(
                bucket=os.environ["BUCKET"], 
                firebase_filename=payload.reference_video, 
                local_filename=reference_video_path
            )

            extract_audio_from_video(reference_video_path, audio_path)

            # Extract pose
            logger.info("Starting pose extraction")
            os.system(f"python pose_align.py --imgfn_refer {reference_img_path} --vidfn {reference_video_path}")
            logger.info("End pose extraction")

        # Send api call
        callPayload = {
            "apiKey": os.environ["INFERENCE_API_KEY"],
            "path": payload.output_path,
            "step": "handler"
        }
        requests.post(os.environ["INFERENCE_URL"], json=callPayload)

        # Start inference
        logger.info("Starting Inference")

        if payload.lower_vram:
            os.system("python test_stage_2.py --config ./configs/custom.yaml -W 512 -H 512")
        else:
            os.system("python test_stage_2.py --config ./configs/custom.yaml")

        dance_folder = glob.glob("./output/*/*")[0]
        logger.warning(os.system(f"ls {dance_folder}"))
        logger.info("Finished Inference")


        # Remove background from image
        dance_video_path = glob.glob(f"{dance_folder}/*.mp4")[0]
        dance_video_processed_path = os.path.join("assets", "videos", "dance_video.mp4")

        if payload.remove_background:
            remove_background_from_video(
                pipe=brackground_remover_pipe, 
                video_path=dance_video_path, 
                output_path=dance_video_processed_path
            )
        else:
            shutil.copy(dance_video_path, dance_video_processed_path)

        # Loop the video to match the audio length and add the audio to the video
        logger.info("Adding audio to the output video")
        video, audio = load_video_and_audio(dance_video_processed_path, audio_path)
        video = loop(video, audio)

        # Add watermark to video
        final_motion_sequence_path = "final_video.mp4"
        if payload.watermark:
            logger.info("Adding watermark to video")
            add_watermark_to_video(
                video=video,
                watermark_path=payload.watermark_path,
                output_path=final_motion_sequence_path,
                watermark_width=payload.watermark_width,
                offset=payload.watermark_offset
            )
        else:
            video.write_videofile(final_motion_sequence_path, codec='libx264')

        upload_firebase_file(
            bucket=os.environ["BUCKET"],
            firebase_filename=payload.output_path,
            local_filename=final_motion_sequence_path
        )

        # Send end api call
        callPayload = {
            "apiKey": os.environ["UPLOAD_API_KEY"],
            "path": payload.output_path
        }
        requests.post(os.environ["UPLOAD_URL"], json=callPayload)
        
        return {
            "statusCode": 200,
            "message": "Inference Job Succeed",
        }
        
    except Exception as e:
        print(e)
        exception_payload = {
            "apiKey": os.environ["exception_api_key"], 
            "path": payload.output_path, 
            "id": payload.id, 
            "reason": str(e)
        }
        requests.post(os.environ["exception_url"], data=exception_payload)
        return {
            "statusCode": 500,
            "error": str(exception_payload),
            "refresh_worker": True,
        }
    

runpod.serverless.start({"handler": handler})
