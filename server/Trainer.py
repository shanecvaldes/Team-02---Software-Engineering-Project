from DataContainer import DataContainer
from DataContainer import *
import tensorflow as tf
import keras
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from data_handler import Data_Handler
import tempfile
from imblearn.over_sampling import SMOTE
import sys
'''from tensorflow.keras import mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)'''

import keras_tuner

# Label containers
from sklearn.preprocessing import MultiLabelBinarizer

# Save modules
import pickle
import joblib

import time
from keras.callbacks import EarlyStopping # type: ignore

# Sklearn models
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
# Parameter testers
# Dont forget to remove unimportant features with the .feature_importance_member var
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import RandomizedSearchCV

from imblearn.over_sampling import SMOTENC


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


class Trainer():
    def __init__(self, DataContainer:DataContainer=None):
        self.DataContainer = DataContainer
        # Support Vector Classifier - DONE
        self.SVC_model = None
        # Sequential - DONE
        self.Sequential_model = None
        # Long Short-Term Memory
        self.LSTM_model = None
        # Random Forest
        self.RF_model = None
        # Decision Tree
        self.DT_model = None


    def save_all(self):
        if self.LSTM_model is not None:
            self.LSTM_model.save(f'model_data/models/team_{self.DataContainer.teamid}_LSTM.keras')
        if self.Sequential_model is not None:
            self.Sequential_model.save(f'model_data/models/team_{self.DataContainer.teamid}_Sequential.keras')
        if self.DT_model is not None:
            with open(f'model_data/models/team_{self.DataContainer.teamid}_DT.pkl', 'wb') as f:
                joblib.dump(self.DT_model, f)
        if self.RF_model is not None:
            with open(f'model_data/models/team_{self.DataContainer.teamid}_RF.pkl', 'wb') as f:
                joblib.dump(self.RF_model, f)
        if self.SVC_model is not None:
            with open(f'model_data/models/team_{self.DataContainer.teamid}_SVC.pkl', 'wb') as f:
                joblib.dump(self.SVC_model, f)

        if self.DataContainer is not None:
            with open(f'model_data/data_containers/team_{self.DataContainer.teamid}.pkl', 'wb') as f:
                joblib.dump(self.DataContainer, f)

        return {'container_path':f'model_data/data_containers/team_{self.DataContainer.teamid}.pkl',
                'model_path':f'model_data/models/team_{self.DataContainer.teamid}_LSTM.keras'}


    def getSMOTENC(self, X, y):
        # print(X[:5])
        y_flat = np.argmax(y, axis=1)  # Convert one-hot to single-label integers

        # Step 2: Apply SMOTE
        sm = SMOTE(random_state=42)
        X_res, y_res_flat = sm.fit_resample(X, y_flat)

        # Step 3: Convert back to one-hot encoding
        num_classes = y.shape[1]
        y_res = np.eye(num_classes)[y_res_flat]

        return X_res, y_res


        print(y.shape)
        print(X.shape)
        combined = np.concatenate((X, y), axis=1)
        sm = SMOTENC(categorical_features=[X.shape[1]], random_state=42)
        X_train_res, y_train_res = sm.fit_resample(combined, y)
        temp = X_train_res[:, :self.DataContainer.number_of_features]
        print(y_train_res)

        return temp, y_train_res
    def train_all(self):
        # X_train, X_test, y_train, y_test = train_test_split(self.DataContainer.features, self.encoded_labels, test_size=0.2, random_state=42)
        X_train, X_test, y_train_hot, y_test_hot = train_test_split(self.DataContainer.features, self.DataContainer.hot_labels, test_size=0.2, random_state=42)
        X_SMOTE, y_SMOTE = self.getSMOTENC(X_train, y_train_hot)

        # timestep 32
        # X_test_new = X_test.reshape(-1, self.DataContainer.number_of_features, 1)
        # X_train_new = X_SMOTE.reshape(-1, self.DataContainer.number_of_features, 1)

        # timestep 1


        X_test_new = X_test.reshape(-1, 1, self.DataContainer.number_of_features)
        X_train_new = X_SMOTE.reshape(-1, 1, self.DataContainer.number_of_features)
        self.timestep = 1

        print(y_SMOTE.shape)
        start = time.time()
        # self.train_DT(X_SMOTE, y_SMOTE, X_test, y_test_hot)
        # self.train_SVC(X_SMOTE, y_SMOTE, X_test, y_test_hot)
        # self.train_RF(X_SMOTE, y_SMOTE, X_test, y_test_hot)
        # 3self.train_Sequential(X_SMOTE, y_SMOTE, X_test, y_test_hot)
        self.train_LSTM(X_train_new, y_SMOTE, X_test_new, y_test_hot)
        # self.train_DT(X_train, y_train_hot, X_test, y_test_hot)
        # self.train_SVC(X_train, y_train_hot, X_test, y_test_hot)
        # self.train_RF(X_train, y_train_hot, X_test, y_test_hot)
        # self.train_Sequential(X_train, y_train_hot, X_test, y_test_hot)


        end = time.time()
        print(f'Total training took: {end - start} seconds')

        print('Testing LSTM...')
        self.test(self.LSTM_model, X_test_new, y_test_hot)
        return

        print('Testing Sequential...')
        self.test(self.Sequential_model, X_test, y_test_hot)
        print('Testing RF...')
        self.test(self.RF_model, X_test, y_test_hot)
        print('Testing DT...')
        self.test(self.DT_model, X_test, y_test_hot)
        print('Testing SVC...')
        self.test(self.SVC_model, X_test, y_test_hot)

    # DT MODELS -------------------------------------------------------------------------------------------------
    def train_DT(self, X_train, y_train, X_test, y_test):
        params = {}
        dtc = DecisionTreeClassifier()
        clf = GridSearchCV(dtc, params)
        clf.fit(X_train, y_train)

        # print(clf.predict(X_test))
        # print(clf.best_estimator_)
        # print(clf.score(X_test, y_test))
        self.DT_model = clf

    # RF MODELS -------------------------------------------------------------------------------------------------
    def train_RF(self, X_train, y_train, X_test, y_test):
        params = {'bootstrap': [True],
                'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],
                'max_features': ['log2', 'sqrt'],
                'min_samples_leaf': [1, 2, 4],
                'min_samples_split': [2, 5, 10],
                'n_estimators': [800, 1000, 1200, 1400, 1600, 1800, 2000]}
        rfc = RandomForestClassifier()
        # clf = GridSearchCV(rfc, params)
        clf = RandomizedSearchCV(estimator=rfc, param_distributions=params, n_iter=20, cv=3, verbose=2, random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)

        temp = RandomForestClassifier(max_depth=90, n_estimators=1400)

        # print(clf.predict(X_test))
        print(clf.best_estimator_)
        print(clf.score(X_test, y_test))
        self.RF_model = clf.best_estimator_

    # SCV MODELS -------------------------------------------------------------------------------------------------
    def train_SVC(self, X_train, y_train, X_test, y_test):
        # SCV fits
        params = {'kernel':['linear', 'poly', 'sigmoid', 'rbf'], 
                                         'C':[1, 10],
                                         'degree':[1, 2, 3, 4, 5],
                                         'gamma':['scale', 'auto']}
        svc = SVC()
        # clf = GridSearchCV(svc, params) 
        clf = MultiOutputClassifier(svc, n_jobs=10)
        clf.fit(X_train, y_train)
        
        # print(clf.best_estimator_)
        # print(clf.score(X_test, y_test))
        self.SVC_model = clf

    # LSMT MODELS -------------------------------------------------------------------------------------------------
    def train_LSTM(self, X_train, y_train, X_test, y_test):
        # Create Sequential Models
        '''
        total_elements_train = X_train.size  # Total number of elements in X_train
        num_samples_train = X_train.shape[0]  # Number of samples in X_train
        timesteps = 32  # Fixed number of timesteps

        # Calculate number of features for X_train
        number_of_features = total_elements_train // (num_samples_train * timesteps)
        print(f"Number of features: {number_of_features}")

        # Reshape X_train with the calculated number of features
        X_train_new = X_train.reshape(-1, 32, number_of_features)

        # Apply the same reshaping logic to X_test
        total_elements_test = X_test.size  # Total number of elements in X_test
        num_samples_test = X_test.shape[0]  # Number of samples in X_test

        # Ensure the number of features is consistent between X_train and X_test
        if total_elements_test == num_samples_test * timesteps * number_of_features:
            X_test_new = X_test.reshape(-1, 32, number_of_features)
        else:
            raise ValueError("Inconsistent number of features between X_train and X_test.")

        # Print shapes to verify the reshaping
        print(f"X_train_new shape: {X_train_new.shape}")
        print(f"X_test_new shape: {X_test_new.shape}")'''

        
        self.num_layers = 3
        # self.layers = [0, 8, 16, 32, 64, 128, 256]
        self.layers = [64, 128, 256]
        self.layer_names = ['first_layer', 'second_layer', 'third_layer']
        callback = EarlyStopping(monitor='val_loss', patience=3)
        with tempfile.TemporaryDirectory() as temp_dir:
            tuner = keras_tuner.RandomSearch(self.build_LSTM, objective='val_loss', max_trials=10, executions_per_trial=1, directory=temp_dir)
            tuner.search(X_train, y_train, batch_size=512, epochs=10, validation_data=(X_test, y_test), callbacks=[callback])
            self.LSTM_model = tuner.get_best_models()[0]

    def build_LSTM(self, hp):
        model = keras.Sequential()

        # Timestep 1
        if self.timestep == 1:
            model.add(keras.Input(shape=(1, self.DataContainer.number_of_features)))
        elif self.timestep == self.DataContainer.number_of_features:
            model.add(keras.Input(shape=(self.DataContainer.number_of_features, 1)))
        for i in range(self.num_layers):
            neurons_layer = hp.Choice(self.layer_names[i], self.layers)
            if neurons_layer > 0:
                model.add(layers.LSTM(
                        units=neurons_layer,
                        activation='tanh',
                        return_sequences=(i < self.num_layers - 1)
                    ))
        dropout_rate = hp.Choice('dropout_rate', [0.2, 0.4])
        if dropout_rate > 0:
            model.add(layers.Dropout(rate=dropout_rate))
        model.add(layers.Dense(self.DataContainer.hot_labels.shape[1], activation='sigmoid'))
        # optimizers Nadam, RMSprop, adam
        optimizer = keras.optimizers.Adam(learning_rate=0.01)
        optimizer = keras.optimizers.Adam(clipvalue=1.0)
        optimizer = keras.optimizers.Adam(clipvalue=1.0, learning_rate=0.001)

        model.compile(optimizer='Nadam', loss='binary_crossentropy', metrics=['accuracy'])
        
        return model

    # DENSE MODELS -------------------------------------------------------------------------------------------------
    def train_Sequential(self, X_train, y_train, X_test, y_test):
        # Create Sequential Models
        self.num_layers = 3
        self.layers = [0, 8, 16, 32, 64, 128]
        self.layers = [32, 64, 128]
        
        self.layer_names = ['first_layer', 'second_layer', 'third_layer']
        callback = EarlyStopping(monitor='val_loss', patience=3)

        with tempfile.TemporaryDirectory() as temp_dir:
            tuner = keras_tuner.RandomSearch(self.build_Sequential, objective='val_loss', max_trials=20, executions_per_trial=1, directory=temp_dir)
            tuner.search(X_train, y_train, batch_size=256, epochs=5, validation_data=(X_test, y_test), callbacks=[callback])
            self.Sequential_model = tuner.get_best_models()[0]
        
    def build_Sequential(self, hp):
        model = keras.Sequential()
        
        model.add(keras.Input(shape=(self.DataContainer.number_of_features,)))
        for i in range(self.num_layers):
            neurons_layer = hp.Choice(self.layer_names[i], self.layers)
            if neurons_layer > 0:
                model.add(layers.Dense(
                        units=neurons_layer,
                        activation='relu'
                    ))
        model.add(layers.Dense(self.DataContainer.number_of_lables, activation='sigmoid'))
        model.compile(optimizer='adam', loss='binary_crossentropy')
        
        return model
        
    def test(self, model, X_test, y_test):
        if model is None:
            return
        y_pred = model.predict(X_test)
        if y_pred[0][0] != 1 and y_pred[0][0] != 0:
            y_pred = (y_pred > 0.50).astype(int)
        print(classification_report(y_test, y_pred, zero_division=0))
        # print(self.DataContainer.label_encoder.inverse_transform(y_pred))

        # y_pred_flat = np.argmax(y_pred, axis=1)
        # print(classification_report(y_test, y_pred_hot, zero_division=0))


if __name__ == '__main__':
    # Set the path to your dataset folder (structure: dataset/speaker_name/*.wav)
    db_handler = Data_Handler(server = '', db = '', user='', password='')
    dataset = DataContainer(n_mfcc=32, users=['cjk265s', 'scv566s'], teamid=5)
    dataset.prepare_from_timestamps(db_handler)
    recognizer = Trainer(dataset)
    recognizer.train_all()

    # recognizer.save_all()