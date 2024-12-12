from data_handler import Data_Handler
from DataContainer import DataContainer
from Trainer import Trainer
from Predictor import Predictor
import os
import wave
import subprocess
import ffmpeg
import speech_recognition as sr
import joblib

def get_wav_duration(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
        return round(duration, 2)
    
def reset(db_handler):
    with open('queries/drop_tables.sql') as f:
        for query in f.read().split(';'):
            try:
                db_handler.insert(query, ())
            except Exception as e:
                print(e)

    with open('queries/new_voice_application_query.sql') as f:
        for query in f.read().split(';'):
            try:
                db_handler.insert(query, ())
            except Exception as e:
                print(e)

    for trigger in ['queries/enforce_user_a_le_user_b.sql', 'queries/enforce_creator_not_member.sql']:
        with open(trigger) as f:
            try:
                db_handler.insert(f.read(), ())
            except Exception as e:
                print(e)

    with open('queries/new_inserts.sql') as f:
        for query in f.read().split(';'):
            try:
                db_handler.insert(query, ())
            except Exception as e:
                print(e)

    protected = ['team_1_LSTM.keras','team_2_LSTM.keras','team_3_LSTM.keras',
                 'team_1.pkl','team_2.pkl','team_3.pkl']
    for model_path in os.listdir('model_data\\models'):
        if model_path not in protected:
            os.remove('model_data\\models\\'+model_path)
    for data_continer_path in os.listdir('model_data\\data_containers'):
        if data_continer_path not in protected:
            os.remove('model_data\\data_containers\\'+data_continer_path)
def generate_sounds(db_handler:Data_Handler, dataset_path):

    prompt_mappings= {'ah258s':'Drew-sample.wav', 
                    'scv566s':'Shane Prompt.wav', 
                    'biser412':'Recording (5).wav',
                    'cjk265s':'Curtis prompt.wav',
                    'mve7s':'Milo Etz Voice Prompt.wav',
                    'ntc9s':'Nashod Prompt.wav',
                    }
    
    team_mappings = {}
    r = sr.Recognizer()
    for speaker in os.listdir(dataset_path):
        speaker_path = os.path.join(dataset_path, speaker)
        

        # Skip any non-directory files
        if not os.path.isdir(speaker_path):
            continue
        
        if speaker != 'Null':
            user_id = db_handler.query("""SELECT user_id FROM users u WHERE username=%s;""", (speaker, ))[0][0]

        for audio_file in os.listdir(speaker_path):
            audio_path = os.path.join(speaker_path, audio_file)
            
            if audio_file.endswith('.m4a'):
                output = audio_path.removesuffix(audio_file)+audio_file.removesuffix('.m4a')+'.wav'
                # print(output)
                command = ['ffmpeg', '-i', audio_path, output] 
                subprocess.run(command)
                os.remove(audio_path)
                audio_path = output
            # print(audio_path)
            if speaker == 'Null':
                continue
            
            is_prompt = audio_file == prompt_mappings[speaker]

            
            # print(audio_path)
            duration = get_wav_duration(audio_path)

            '''sound_files_query = """INSERT INTO sound_files (user_id, sound_path, is_prompt)
                                VALUES (%s, %s, %s)
                                RETURNING sound_id;
                                """
            
            # ON CONFLICT (sound_id) DO UPDATE SET user_id = EXCLUDED.user_id, sound_path = EXCLUDED.sound_path
            data = (user_id, audio_path, is_prompt)
            sound_id = db_handler.insert(sound_files_query, data)'''
            if audio_path in team_mappings.keys():
                team_id = team_mappings[audio_path]
            else:
                team_id = None
            sound_id = db_handler.insert_sound_file(user_id, audio_path, team_id, is_prompt)

            if team_id == None:
                db_handler.insert_sound_timestamp(sound_id, user_id, '00:00:00', f"{int(duration//3600)}:{int((duration%3600)//60)}:{int(duration%60)}")

def model_helper(dataset:DataContainer):
    trainer = Trainer(dataset)
    trainer.train_all()
    return trainer.save_all()


def generate_models(db_handler:Data_Handler):
    print('Generating models...')
    query = """SELECT DISTINCT team_id FROM teams;"""
    teams = db_handler.query(query, ())
    query_leader = """SELECT u.username FROM users u
                INNER JOIN teams t ON u.user_id = t.user_id
                WHERE t.team_id = %s"""
    
    query_members = """SELECT u.username FROM users u
                INNER JOIN team_members t ON u.user_id = t.user_id
                WHERE t.team_id = %s"""
    team_mappings = {}
    
    for team in teams:
        users = [i[0] for i in db_handler.query(query_members, team) + db_handler.query(query_leader, team)]
        print(users, team)
        dataset = DataContainer(n_mfcc=32, users=users, teamid=team[0])
        dataset.prepare_from_timestamps(db_handler, prompt=False)
        paths = model_helper(dataset)
        db_handler.insert_model_file(team[0], paths['model_path'], paths['container_path'])
        # db_handler.insert_model_file()

    for key, value in team_mappings.items():
        model_path, container_path = db_handler.get_team_model(value)[0]
        sound_id = db_handler.get_sound_id(key)
        print("HERE IS THE SOUND ID:", sound_id)
        with open(container_path, 'rb') as f:
            original_set = joblib.load(f)
        predictor = Predictor(original_set)
        predictor.load_model(model_path)
        predictions = predictor.predict_file(key)
        print(predictions)
        timestamp_inserts(predictions, sound_id, db_handler)
    return 

def timestamp_inserts(predictions:list, sound_id:int, db_handler:Data_Handler):
    # store like : speaker : [start, end]
    speakers = {}
    for i, prediction in enumerate(predictions):
        # print(prediction)
        for speaker in prediction:
            if speaker in speakers:
                speakers[speaker][-1] = i
            else:
                speakers[speaker] = [i, i]
        # find speakers that are not in the prediction and insert them
        speakers_to_delete = []
        for speaker in speakers.keys():
            # print(speaker)
            if speaker not in prediction:
                start_time = f"{speakers[speaker][0]//3600}:{(speakers[speaker][0]%3600)//60}:{speakers[speaker][0]%60}"
                end_time = f"{speakers[speaker][1]//3600}:{(speakers[speaker][1]%3600)//60}:{speakers[speaker][1]%60}"
                # print(sound_id, speaker, start_time, end_time)
                db_handler.insert_sound_timestamp_username(sound_id, speaker, start_time, end_time)
                speakers_to_delete.append(speaker)
        for speaker in speakers_to_delete:
            del speakers[speaker]
    for speaker in speakers.keys():
        # print(speaker)
        start_time = f"{speakers[speaker][0]//3600}:{(speakers[speaker][0]%3600)//60}:{speakers[speaker][0]%60}"
        end_time = f"{speakers[speaker][1]//3600}:{(speakers[speaker][1]%3600)//60}:{speakers[speaker][1]%60}"
        # print(sound_id, speaker, start_time, end_time)
        db_handler.insert_sound_timestamp_username(sound_id, speaker, start_time, end_time)


def main():
    dataset_path = 'full_dataset'
    # names = {'Shane':'scv566s', 'Curtis':'cjk265s', 'Milo':'mve7s', 'Drew':'ah258s', 'Jenna':'biser412', 'Nashod':'ntc9s'}

    db_handler = Data_Handler()
    

    # db_handler.insert(f"""TRUNCATE TABLE sound_files CASCADE;""", ())
    reset(db_handler)
    generate_sounds(db_handler=db_handler, dataset_path=dataset_path)
    # generate_models(db_handler)



    

    

if __name__ == '__main__':
    main()