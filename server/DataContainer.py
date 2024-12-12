import os
import numpy as np
import librosa
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer
import json
from data_handler import Data_Handler
from datetime import time, timedelta

__all__ = [
    'os',
    'np',
    'librosa',
    'pd',
]


class DataContainer(object):
    def __init__(self, n_mfcc:int, users=[], teamid=-1):
        self.number_of_features = n_mfcc
        self.number_of_lables = 0
        # Contain the users and their features
        self.features_collection = {}
        self.labels = users
        self.features = []
        self.offset = 0
        # self.label_encoder = LabelEncoder()
        # self.encoded_labels = []

        self.hot_labels = []
        self.label_encoder = MultiLabelBinarizer()


        self.teamid = teamid

    # Audio splicer
    # Desc: Splice an audio file into increments of at most n seconds (default 1), returning the features of each splice of data
    # Input: audio_path, seconds
    # Output: The features of the audio data
    def audio_splicer(self, audio_path, seconds=0.5):
        y, sr = librosa.load(audio_path, sr=None, offset = self.offset)
        # Calculates segment length in samples
        segment_samples = int(seconds * sr)
        total_segments = int(np.ceil(len(y) / segment_samples))
        segment_features = []
        start = 0
        end = segment_samples

        # Go through sections and extract features from segment
        for i in range(total_segments):
            start = int(i * segment_samples)
            end = min(int((i + 1) * segment_samples), len(y))
            segment = y[start:end]
            segment_features.append(self.feature_extract(segment, sr))
        # print(segment_features[-1])
        return segment_features

    def feature_extract(self, segment, sr):
        # Extract MFCCs from the segment
        mfccs = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=self.number_of_features)
        mfcc_mean = np.mean(mfccs.T, axis=0)
        return mfcc_mean

    def update_live(self, file_path, offset=0, seconds = 1):
        # if '' in self.features_collection.keys() == False:
        self.offset = offset
        # y, sr = librosa.load(file_path, sr=None, offset = self.offset)
        self.features_collection.clear()
        self.features_collection[''] = self.audio_splicer(file_path, seconds)
        self.unravel_features(update_encoder=False)
        # print(self.features)
        

    def prepare_data(self, dataset_path, seconds=0.5):
        # Loop through each directory (speaker) in the dataset
        # Leave room for 'Unknown'
        self.number_of_lables = len(self.labels)+1
        self.features_collection.clear()
        for speaker in os.listdir(dataset_path):
            speaker_path = os.path.join(dataset_path, speaker)

            # Skip any non-directory files
            if not os.path.isdir(speaker_path):
                continue

            if speaker not in self.labels:
                speaker = 'Null'
                continue

            for audio_file in os.listdir(speaker_path):
                audio_path = os.path.join(speaker_path, audio_file)
    
                if speaker in self.features_collection.keys():
                    self.features_collection[speaker] += self.audio_splicer(audio_path, seconds)
                else:
                    self.features_collection[speaker] = self.audio_splicer(audio_path, seconds)
        self.unravel_features()
        print(len(self.features))
        # self.label_encoder.fit(self.labels)
        print('Transforming')
        self.hot_labels = self.label_encoder.fit_transform(self.labels)
        # self.hot_labels = np.zeros((self.labels.size, self.number_of_lables))
        # self.hot_labels[np.arange(self.labels.size, dtype=np.int64), self.encoded_labels] = 1
        

        # print(type(self.features))

    def unravel_features(self):
        features = []
        # labels = []
        label_collection = []
        for speaker, current_features in self.features_collection.items():
            # labels += [speaker for i in range(len(current_features))]
            features += [i for i in current_features]
            label_collection += [set([speaker,]) for i in range(len(current_features))]
        self.features = np.array(features)
        self.labels = np.array(label_collection)
        # if update_encoder:
        #     self.test_labels = self.label_encoder.fit_transform(label_collection)
        # print(temp)
        # print(self.labels)
        # return np.array(labels), np.array(features)\

    def time_to_seconds(self, t):
            # Converts a datetime.time object to seconds
            return t.hour * 3600 + t.minute * 60 + t.second
    
    def merge_intervals(self, data):
        merged_data = {}
        for sound_path, intervals in data.items():
            # Sort intervals by 
            # print(intervals)
            intervals.sort(key=lambda x: self.time_to_seconds(x['start_time']))
            # print(intervals)
            merged_intervals = []
            current_interval = intervals[0]
            # print(current_interval['start_time'])

            for i in range(1, len(intervals)):
                next_interval = intervals[i]
                # If intervals overlap or are adjacent, merge them
                if self.time_to_seconds(next_interval['start_time']) <= self.time_to_seconds(current_interval['end_time']) + 1:
                    current_interval['end_time'] = max(current_interval['end_time'], next_interval['end_time'])
                    # print(current_interval['username'])
                    current_interval['username'] = list(set(current_interval['username']).union(set(next_interval['username'])))
                else:
                    # Push the current interval to the merged list and move to the next
                    merged_intervals.append(current_interval)
                    current_interval = next_interval

            # Add the last interval
            merged_intervals.append(current_interval)

            # Store merged intervals in the output dictionary
            merged_data[sound_path] = merged_intervals
        # print(merged_data)
        return merged_data

    def prepare_from_timestamps(self, db_handler: Data_Handler, prompt=True):
        # Step 1: Retrieve combined timestamps for all users
        combined_results = {}
        for user in self.labels:
            # Retrieve the timestamps for the current user
            # user_timestamps = db_handler.get_all_timestamps(user)
            if prompt:
                user_timestamps = db_handler.get_all_prompt_timestamps(user)
            else:
                user_timestamps = db_handler.get_all_timestamps(user)
            # Merge user_timestamps into combined_results
            for sound_path, entries in user_timestamps.items():
                for entry in entries:
                    entry['start_time'] = self.time_to_seconds(entry['start_time'])
                    entry['end_time'] = self.time_to_seconds(entry['end_time'])
                # print(entries)
                if sound_path not in combined_results:
                    combined_results[sound_path] = []                
                combined_results[sound_path].extend(entries)
        # print(combined_results)
        self.generate_features_and_labels(combined_results, 1)

        self.features, self.labels = self.generate_features_and_labels(combined_results, 1)
        self.features, self.labels = np.array(self.features), np.array(self.labels)

        self.hot_labels = self.label_encoder.fit_transform(self.labels)
        return 
    
    def generate_features_and_labels(self, combined_result, seconds=1):
        features_result = []
        labels = []
        # go through each sound and splice into intervals
        for sound_path, intervals in combined_result.items():
            # Extract audio features for the entire file
            current_time = 0
            spliced_features = self.audio_splicer(sound_path, seconds)
            # increment based on seconds
            for features in spliced_features:
                # go through the intervals and find user overlap
                current_label = set()
                for interval in intervals:
                    if interval['start_time'] <= current_time <= interval['end_time']:
                        current_label.add(interval['username'])
                labels.append(current_label)
                features_result.append(features)
                current_time += seconds
                # print(current_label)
            
        return features_result, labels

if __name__ == '__main__':

    db_handler = Data_Handler()
    
    # timestamps = db_handler.get_all_timestamps('scv566s')
    # print(timestamps)
    dataset_path = 'full_dataset'
    recognizer = DataContainer(n_mfcc=32, users=['scv566s', 'cjk265s', 'ah258s'], teamid=5)
    recognizer.prepare_from_timestamps(db_handler)

    print(recognizer.hot_labels)
    print(recognizer.label_encoder.inverse_transform(np.array([[1, 1, 1]])))
    # recognizer.prepare_data(dataset_path, 0.1)
