import os
import cv2
import streamlit as st
from PIL import Image
import pandas as pd
from tensorflow import keras
from pymongo import MongoClient
import datetime
import numpy as np
import base64
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

# Constants
IMG_SIZE = 100
BATCH_SIZE = 32
EPOCHS = 20
MAX_SEQ_LENGTH = 100
NUM_FEATURES = 2048


# Displaying the first image centered
try:
    with open("first_image.jpeg", "rb") as f:
        avert_image = f.read()

    # Centering the image using CSS
    st.markdown(
        f'<div style="text-align:center"><img src="data:image/jpeg;base64,{base64.b64encode(avert_image).decode()}" alt="AVERT Logo" width="500"/></div>',
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.error("AVERT image file not found.")

# Displaying a header
st.markdown("<h1 style='text-align:center'>AVERT</h1>", unsafe_allow_html=True)
st.markdown("---")


# Displaying the AVERT logo centered and resized
try:
    with open("avert.jpeg", "rb") as f:
        avert_image = f.read()

    # Centering the image using CSS
    st.markdown(
        f'<div style="text-align:center"><img src="data:image/jpeg;base64,{base64.b64encode(avert_image).decode()}" alt="AVERT Logo" width="100"/></div>',
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.error("AVERT image file not found.")

# Add a file uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])


# Main Report Section
report = st.container()
with report:
    st.header("Report for Crime Cases in India")

    # Display live video recording
    webrtc_ctx = webrtc_streamer(
        key="record",
        video_processor_factory=None,  # no processing for raw video frames
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        ),
    )

    # Check if video is being captured
    if webrtc_ctx.video_transformer:
        st.write("Recording live video...")

        # Accessing live video frames
        while True:
            video_frame = webrtc_ctx.video_transformer.frame

            # Process video frame (add your processing logic here)

    else:
        st.write("Waiting for live video feed...")

# Footer
st.markdown("---")
