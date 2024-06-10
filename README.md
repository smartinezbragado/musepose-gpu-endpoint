# MusePose GPU Endpoint

Welcome to the MusePose GPU Endpoint repository! This repository contains the implementation of the MusePose model, designed to be served via a REST API.

## Overview

MusePose is a diffusion-based and pose-guided virtual human video generation framework. Our main contributions can be summarized as follows:

## Examples

To see MusePose in action, check out the following examples:

- **Input image**: Reference image  


  <img src="examples/input_image.png" width="640" height="480" alt="Input Image">



- **Motion Sequence**: Motion sequence  


<video width="640" height="480" controls>
    <source src="examples/motion_sequence.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>


- **Output**: Generated dance video 


  <video width="640" height="480" controls>
    <source src="examples/dance_video.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  
  ## API Endpoint Description

  The MusePose GPU Endpoint provides a REST API for generating virtual human videos based on a reference image and an optional motion sequence or reference video. The endpoint accepts a JSON payload with the following schema:

  - **id**: A unique identifier for the animation request.
  - **audio_file**: The path to the audio file to be used in the generated video.
  - **output_path**: The path where the generated video will be saved.
  - **reference_image**: The path to the reference image to be used for generating the virtual human.
  - **reference_video**: (Optional) The path to a reference video to guide the animation.
  - **motion_sequence**: (Optional) The path to a motion sequence file to guide the animation.
  - **seed**: A seed value for random number generation to ensure reproducibility. Default is 1.
  - **image_clip_duration**: The duration of the image clip in seconds. Default is 5 seconds.
  - **lower_vram**: A boolean flag to indicate whether to use lower VRAM settings. Default is False.
  - **watermark**: A boolean flag to indicate whether to add a watermark to the generated video. Default is True.
  - **watermark_path**: The path to the watermark image.
  - **watermark_width**: The width of the watermark in pixels. Must be greater than 0. Default is 100 pixels.
  - **watermark_offset**: The offset of the watermark from the edges of the video in pixels. Must be greater than 0. Default is 20 pixels.
  - **remove_background**: A boolean flag to indicate whether to remove the background from the reference image. Default is False.

  The endpoint validates the input payload to ensure all required fields are provided and that the values are within acceptable ranges. Upon successful validation, the endpoint processes the request and generates the virtual human video, which is then saved to the specified output path.


