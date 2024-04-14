import os
import cv2
import streamlit as st
from PIL import Image
import pandas as pd
from tensorflow import keras
from pymongo import MongoClient
import datetime
import moviepy.editor as mp
#from vdb import upload

IMG_SIZE = 100
BATCH_SIZE = 32
EPOCHS = 20
MAX_SEQ_LENGTH = 100
NUM_FEATURES = 2048


#import streamlit as st

# Displaying a header
st.markdown("<h1 style='text-align:center'>AVERT</h1>", unsafe_allow_html=True)
st.markdown("---")

# Displaying the image centered with a specific width
try:
    with open("avert.jpeg", "rb") as f:
        image = f.read()
    st.image(image, caption='AVERT Logo', width=100, use_column_width=True)
except FileNotFoundError:
    st.error("Image file not found.")




report=st.container()
state=st.container()
with report:
    st.header("Report for crime Case around the INDIA")

    # Add a file uploader
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

    # Check if a file was uploaded
    if uploaded_file is not None:
        # Save the uploaded file
        with open("uploaded_video.mp4", "wb") as f:
            f.write(uploaded_file.read())

    

    def convert_video(input_file, output_file, codec='libx264', fps=30):
        # Load the video clip using moviepy
        video = mp.VideoFileClip(input_file)

        # Write the video to the output file with the desired codec and format
        video.write_videofile(output_file, codec=codec, fps=fps)

    if uploaded_file is not None:
        # Usage example
        input_file = 'uploaded_video.mp4'
        output_file = 'converted.mp4'
        convert_video(input_file, output_file, codec='libx264')

    if uploaded_file is not None:
    # Use the uploaded file in your app
        with open("converted.mp4", 'rb') as f:
            video_bytes = f.read()
            st.video(video_bytes)
    

    sequence_model = keras.models.load_model('saved_model/')  

    def build_feature_extractor():
        feature_extractor = keras.applications.InceptionV3(
            weights="imagenet",
            include_top=False,
            pooling="avg",
            input_shape=(IMG_SIZE, IMG_SIZE, 3),
    )
        preprocess_input = keras.applications.inception_v3.preprocess_input

        inputs = keras.Input((IMG_SIZE, IMG_SIZE, 3))
        preprocessed = preprocess_input(inputs)

        outputs = feature_extractor(preprocessed)
        return keras.Model(inputs, outputs, name="feature_extractor")


    feature_extractor = build_feature_extractor()

    import numpy as np
    df = pd.read_csv('dataset.csv', header=None)
    df.columns = ["class", "path"]
    df = df.astype({"class": str})
    train, test = np.split(df.sample(frac=1, random_state=42), [int(.8*len(df))])
    
    train_df = train
    test_df = test

    print(f"Total videos for training: {len(train_df)}")
    print(f"Total videos for testing: {len(test_df)}")


    def crop_center_square(frame):
        y, x = frame.shape[0:2]
        min_dim = min(y, x)
        start_x = (x // 2) - (min_dim // 2)
        start_y = (y // 2) - (min_dim // 2)
        return frame[start_y:start_y+min_dim,start_x:start_x+min_dim]

    def load_video(path, max_frames=0, resize=(224, 224)):
        cap = cv2.VideoCapture(path)
        frames = []
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = crop_center_square(frame)
                frame = cv2.resize(frame, resize)
                frame = frame[:, :, [2, 1, 0]]
                frames.append(frame)

                if len(frames) == max_frames:
                    break
        finally:
            cap.release()
        return np.array(frames)
    
    label_processor = keras.layers.StringLookup(
    num_oov_indices=0, vocabulary=np.unique(train_df["class"])
    )
    print(label_processor.get_vocabulary())

    import imageio
    from tensorflow_docs.vis import embed

    def prepare_single_video(frames):
        frames = frames[None, ...]
        frame_mask = np.zeros(shape=(1, MAX_SEQ_LENGTH,), dtype="bool")
        frame_featutes = np.zeros(shape=(1, MAX_SEQ_LENGTH, NUM_FEATURES), dtype="float32")

        for i, batch in enumerate(frames):
            video_length = batch.shape[1]
            length = min(MAX_SEQ_LENGTH, video_length)
            for j in range(length):
                frame_featutes[i, j, :] = feature_extractor.predict(batch[None, j, :])
                frame_mask[i, :length] = 1  # 1 = not masked, 0 = masked

        return frame_featutes, frame_mask


    def sequence_prediction(path):
        class_vocab = label_processor.get_vocabulary()

        frames = load_video(os.path.join(path))
    
        frame_features, frame_mask = prepare_single_video(frames)
        probabilities = sequence_model.predict([frame_features, frame_mask])[0]
        v = ['NON-VIOLENCE','VIOLENCE']
        metadata_class=[]
        metadata_probability=[]
        for i in np.argsort(probabilities)[::-1]:
            st.write(f"  {str(v[class_vocab[i].astype(int)])} :{class_vocab[i]}: {probabilities[i] * 100:5.2f}%")
            metadata_class.append(class_vocab[i]) 
            metadata_probability.append(probabilities[i]*100) 

        nv=''
        if metadata_class[0] == 0:
            nv="NON-VIOLENCE"
        else:
            nv="VIOLENCE"

        if nv=="VIOLENCE":
            
            cluster=MongoClient("mongodb+srv://amrutharajsheker:abcd1234@cluster0.ofwbhxo.mongodb.net/?retryWrites=true&w=majority")
            db=cluster["test"]
            collection=db["student"]
            collection.insert_one({"class":metadata_class[1],"probability":metadata_probability,"date and time":datetime.datetime.now()})

            upload()
            
            import requests
            import json

            send_url = "http://api.ipstack.com/check?access_key=a8d32cb61d8d0c874b8f2e5a373cbe9b"
            geo_req = requests.get(send_url)
            geo_json = json.loads(geo_req.text)
            latitude = geo_json['latitude']
            longitude = geo_json['longitude']
            country = geo_json['country_name']
            region = geo_json['region_name']

            st.write("Country ",geo_json['country_name'])
            st.write("Region_name ",geo_json['region_name'])
            st.write("City :","Chennai")
            st.write("Latitude ",latitude)
            st.write("Longitude ",longitude)
            st.image(geo_json["location"]["country_flag"],width=100)
            
            location="Country :" +country+"\n"+"Region Name :"+region+"\n"+"City : Chennai\n"+"Latitude : " + str(latitude) + "\n" + "Longitude :" + str(longitude)
            
            from twilio.rest import Client

            account_sid = 'AC72a76bc4280fd371e1784e869d97685d'
            auth_token = '04e0689bec93ad04bcc4838f895534b2'
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(from_='+19377147840',
                                            body=nv + "\n date and time \n" + str(datetime.datetime.now()) + " \n Location- \n" + str(location),
                                            to='+918681085550')

            print(message.sid)

        return frames
    
    if uploaded_file is not None:
            test_frames = sequence_prediction("converted.mp4")

st.markdown("---")