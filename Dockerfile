FROM python:3.10-slim

# Clone repo
COPY builder.sh /builder.sh
RUN chmod +x /builder.sh && /builder.sh

# Set the working directory
WORKDIR /muse_pose

# Install muse_pose requirements
RUN pip install -r requirements.txt --no-cache-dir

# Install mmlab packages
RUN pip install --no-cache-dir -U openmim 
RUN mim install mmengine 
RUN mim install "mmcv>=2.0.1" 
RUN mim install "mmdet>=3.1.0" 
RUN mim install "mmpose>=1.1.0" 

# Download MusePose weights
RUN git clone https://huggingface.co/TMElyralab/MusePose && \
    mv MusePose/MusePose /muse_pose/pretrained_weights/ && \
    rm -r MusePose

# Download Stable Diffusion models
RUN git clone https://huggingface.co/lambdalabs/sd-image-variations-diffusers && \
    mkdir /muse_pose/pretrained_weights/sd-image-variations-diffusers && \
    mv sd-image-variations-diffusers/unet /muse_pose/pretrained_weights/sd-image-variations-diffusers/ && \
    mv sd-image-variations-diffusers/image_encoder /muse_pose/pretrained_weights/ && \
    rm -r sd-image-variations-diffusers

RUN git clone https://huggingface.co/stabilityai/sd-vae-ft-mse && \
    mv sd-vae-ft-mse /muse_pose/pretrained_weights/

# Download DWPose model
RUN git clone https://huggingface.co/yzd-v/DWPose && \
    mv DWPose /muse_pose/pretrained_weights/dwpose

# Download YoLO model
RUN wget -O /muse_pose/pretrained_weights/dwpose/yolox_l_8x8_300e_coco.pth https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_l_8x8_300e_coco/yolox_l_8x8_300e_coco_20211126_140236-d3bd2b23.pth

# Install my dependencies
COPY runpod_requirements.txt /muse_pose/runpod_requirements.txt
RUN pip install -r runpod_requirements.txt --no-cache-dir

# Add runpod files
COPY images /muse_pose/images
COPY schemas.py /muse_pose/schemas.py
COPY handler.py /muse_pose/handler.py
COPY video_utils.py /muse_pose/video_utils.py
COPY firebase_utils.py /muse_pose/firebase_utils.py
COPY custom.yaml /muse_pose/configs/custom.yaml

CMD [ "python", "-u", "/muse_pose/handler.py" ]
