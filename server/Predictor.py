from DataContainer import DataContainer
from DataContainer import *
from Trainer import Trainer

import os
import joblib
import pickle

from keras.models import load_model # type: ignore
from sklearn.metrics import classification_report
from sklearn.preprocessing import MultiLabelBinarizer



class Predictor():
    def __init__(self, container:DataContainer = None):
        """Use a given data container and a loaded model to predict a file"""
        # passed container 
        self.container = container

        # model that needs to be loaded in
        self.selected_model = None

        
    def predict_file(self, path:str)-> list:
        """Predict and inverse transform an audio file prediction from a given audio file path"""
        features = np.array(self.container.audio_splicer(path, 1))
        features = features.reshape(-1, 1, self.container.number_of_features)
        predictions = self.selected_model.predict(features)
        print(predictions)
        if predictions[0][0] != 1 and predictions[0][0] != 0:
            predictions = (predictions > 0.70).astype(int)
        return self.container.label_encoder.inverse_transform(predictions)

    def load_model(self, model_path:str):
        """Load in model to be used by predictor instance"""
        # Dynamically load in a model from where ever
        print(f'Loading... {model_path}')
        if '.keras' in model_path:
            self.selected_model = load_model(model_path)
        elif '.pkl' in model_path:
             self.selected_model = joblib.load(model_path)

    
if __name__ == '__main__':
    # loaded in dataset example
    with open('model_data/data_containers/team_4.pkl', 'rb') as f:
        original_set = joblib.load(f)

    predictor = Predictor(original_set)
    predictor.load_model('model_data/models/team_4_LSTM.keras')
    predictions = predictor.predict_file('full_dataset/scv566s/2024-12-11_13-49-44.wav')
    # print(predictions)
    print(predictions)
    speakers = {}
    for i, prediction in enumerate(predictions):
        
        if prediction == ():
            continue
        print(prediction)
        for speaker in prediction:
            if speaker in speakers:
                speakers[speaker][-1] = i
            else:
                speakers[speaker] = [i, i]
        # find speakers that are not in the prediction and insert them
        speakers_to_delete = []
        for speaker in speakers.keys():
            if speaker not in prediction:
                start_time = f"{speakers[speaker][0]//3600:02}:{(speakers[speaker][0]%3600)//60:02}:{speakers[speaker][0]%60:02}"
                end_time = f"{speakers[speaker][1]//3600:02}:{(speakers[speaker][1]%3600)//60:02}:{speakers[speaker][1]%60:02}"
                # db_handler.insert_sound_timestamp_username(sound_id, speaker, start_time, end_time)
                speakers_to_delete.append(speaker)
        for speaker in speakers_to_delete:
            del speakers[speaker]
