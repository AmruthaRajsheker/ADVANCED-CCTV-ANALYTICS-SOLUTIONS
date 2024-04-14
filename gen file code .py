import streamlit as st
import cv2
import os
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import shutil
import base64


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


def create_image_list(folder):
    files = os.listdir(folder)
    image_list = []
    for file_name in files:
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_url = os.path.join("frames", file_name)
            image_dict = {"type": "image_url", "image_url": image_url}
            image_list.append(image_dict)
    return image_list
frames_folder = "frames"
def video_to_frames(video_file, output_folder, num_frames=15):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    temp_video_path = os.path.join(output_folder, "temp_video.mp4")
    with open(temp_video_path, "wb") as f:
        f.write(video_file.getbuffer())
    cap = cv2.VideoCapture(temp_video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total frames in the video:", total_frames)
    step_size = max(total_frames // num_frames, 1)
    current_frame = 0
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if current_frame % step_size == 0:
            frame_path = os.path.join(output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_count += 1
        current_frame += 1
        if frame_count == num_frames:
            break
    cap.release()
    print("\nFrames extraction completed.")
st.title("Video to Frames Converter")
uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])
if uploaded_file is not None:
    st.video(uploaded_file)
    output_folder = "frames"
    if st.button("Convert Video to Frames"):
        video_to_frames(uploaded_file, output_folder)
        st.success("Frames extraction completed.") 
        image_list = create_image_list(frames_folder)
        print(*image_list)
        llm = ChatGoogleGenerativeAI(model="gemini-pro-vision",google_api_key="AIzaSyAzl_WL5lerqdfIj4Pgk8FeCNNZRZkKPFc")
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "is there any harmful act on these images?",
                },  
                *image_list
            ]
        )
        try:
            st.write(llm.invoke([message]).content)
        except:
            # Alert message for predicted violence
            st.warning("A potential situation of violence has been detected. Please proceed with caution and take necessary actions.")

        shutil.rmtree(output_folder)
