# import mic_reader as mr
import numpy as np
from data_handler import Data_Handler
from Trainer import Trainer
from flask import Flask, request, jsonify, session, render_template, redirect, request, send_file, send_from_directory
from flask_jwt_extended import create_access_token, JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from flask_session import Session
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

import subprocess

import os
import base64
import pyaudio
import wave
import io
from Predictor import Predictor
from DataContainer import DataContainer
import joblib
from collections import Counter
import speech_recognition as sr
import datetime
from multiprocessing import Process

db_handler = Data_Handler()


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)

app.secret_key = 'This is the secret key'
app.config["JWT_SECRET_KEY"] = 'This is another secret key'
app.config["UPLOAD_FOLDER"] = 'uploads/profile_pics/'
app.config["ALLOWED_EXTENSIONS"] = {'jpg'}

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app, supports_credentials=True, origins='*')

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

socketio = SocketIO(app, cors_allowed_origins='*')
UPLOAD_FOLDER = 'prompt_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




dataset = None

sample_rate = 48000  # Common sample rate
channels = 2  # Stereo (adjust as needed)
sample_width = 2  # 2 bytes per sample (16-bit audio)

current_recording = None
filename = os.path.join(UPLOAD_FOLDER, 'streamed_recording.wav')  # Save as .wav

# region Recording

@app.route('/session/start', methods=['POST'])
@jwt_required()
def start_audio():
    data = request.get_json(silent=True)
    current_user = get_jwt_identity()[0]
    username = get_jwt_identity()[1]
    team_id = data.get('team_id')
    print("HELP")
    print(team_id)

    date = str(datetime.datetime.now())
    print('DATE', date)
    parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    print(parsed_date)
    formatted_date = parsed_date.strftime("%Y-%m-%d_%H-%M-%S")
    print("FORMATTED DATE", formatted_date)
    session_token = create_access_token(identity=(current_user, team_id, get_jwt_identity()[1], formatted_date), expires_delta=datetime.timedelta(minutes=60))
    '''with open(f'full_dataset/{username}/{current_user}_{team_id}.webm', 'wb') as f:
        pass'''
        
    return jsonify(success = True, session_token=session_token)

@socketio.on('audio_data')
def handle_audio_data(session_token, data):
    decoded = decode_token(session_token)
    current_user = decoded.get('sub')[0]
    team_id = decoded.get('sub')[1]
    username = decoded.get('sub')[2]
    date = decoded.get('sub')[3]
    print(current_user)
    # print(team_id)
    with open(f'full_dataset\\{username}\\{date}.webm', 'ab') as f:
        f.write(data)

@app.route('/session/stop', methods=['POST'])
@jwt_required()
def stop_audio():
    current_user = get_jwt_identity()[0]
    team_id = get_jwt_identity()[1]
    username = get_jwt_identity()[2]
    date = get_jwt_identity()[3]
    # print(date)
    # print(team_id)
    # print(current_user, team_id, username)

    audio_path = f'full_dataset\\{username}\\{date}.webm'
    if audio_path.endswith('.webm'):
        output = audio_path.removesuffix('.webm')+'.wav'
        # print(output)
        command = ['ffmpeg', '-i', audio_path, output] 
        subprocess.run(command)
        os.remove(audio_path)
        audio_path = output

    if team_id == 'null':
        team_id = None

    sound_id = db_handler.insert_sound_file(current_user, audio_path, team_id)
    
    if team_id != None:
        model_path, container_path = db_handler.get_team_model(team_id)[0]
        with open(container_path, 'rb') as f:
            original_set = joblib.load(f)
        predictor = Predictor(original_set)
        predictor.load_model(model_path)
        predictions = predictor.predict_file(audio_path)
        print(predictions)
        timestamp_inserts(predictions, sound_id, db_handler)
    else:
        with wave.open(audio_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        db_handler.insert_sound_timestamp(sound_id, current_user, '00:00:00', f"00:00:{duration}")

    # print(np.array(stream_queue))
    # print(predictor.feature_predict(np.array(stream_queue)))
    # audio_file = f'session_files/{session[1]}.webm'
    # print(audio_file)

    return jsonify(success = True)


@app.route('/session_prompt/stop', methods=['POST'])
@jwt_required()
def stop_audio_prompt():
    current_user = get_jwt_identity()[0]
    username = get_jwt_identity()[2]
    date = get_jwt_identity()[3]

    audio_path = f'full_dataset\\{username}\\{date}.webm'
    if audio_path.endswith('.webm'):
        output = audio_path.removesuffix('.webm')+'.wav'
        # print(output)
        command = ['ffmpeg', '-i', audio_path, output] 
        subprocess.run(command)
        os.remove(audio_path)
        audio_path = output

    team_id = None

    sound_id = db_handler.insert_sound_file(current_user, audio_path, team_id, is_prompt=True)

    return jsonify(success=True)

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
# endregion

# region Fetch

@app.route('/api/fetch/teams', methods=['GET'])
@jwt_required()
def get_teams():
    current_user_id = get_jwt_identity()[0]
    print(get_team_helper(current_user_id, 'member'))
    result = {}
    result['memberships'] = get_team_helper(current_user_id, 'member')
    result['created'] = get_team_helper(current_user_id, 'leader')
    return jsonify(result)




@app.route('/api/fetch/meetings', methods=['GET'])
@jwt_required()
def get_meetings():
    current_user = get_jwt_identity()[0]
    meetings = db_handler.get_meetings(current_user)
    return jsonify(success = True, meetings = meetings)

@app.route('/api/need_prompt', methods=['GET'])
@jwt_required()
def get_need_prompt():
    try:
        current_user = get_jwt_identity()[0]
        success = db_handler.needs_prompt(current_user)
        print(success)
        return jsonify(success=success)
    except:
        return jsonify(success=False)


@app.route('/api/fetch/friend_requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    user_id = get_jwt_identity()[0]
    friend_requests = db_handler.get_pending_friends(user_id)
    current_friends = db_handler.get_accepted_friends(user_id)

    friend_requests = [{'user_id': user_id, 'username': username} for user_id, username in friend_requests]
    current_friends = [{'user_id': user_id, 'username': username} for user_id, username in current_friends]
    print(current_friends)
    return jsonify(success=True, pending_friends = friend_requests, current_friends = current_friends)



@app.route('/api/friends/search', methods=['GET'])
@jwt_required()
def search_friends():
    search_query = request.args.get('query', '').strip()
    user_id = get_jwt_identity()[0]
    if not search_query:
        return jsonify(success=True, results = [])
    
    users = db_handler.search_friend(user_id, search_query)
    users = [{'username':i[0], 'email':i[1]} for i in users]
    print(users)
    return jsonify(success=True, results = users)


@app.route('/api/users/search', methods=['GET'])
@jwt_required()
def search_users():
    search_query = request.args.get('query', '').strip()
    user_id = get_jwt_identity()[0]
    if not search_query:
        return jsonify(success=True, results = [])
    
    users = db_handler.search_user(user_id, search_query)
    users = [{'username':i[0], 'email':i[1]} for i in users]
    return jsonify(success=True, results = users)


# Fetch the friends
@app.route("/api/fetch/user/friends", methods=["GET"])
@jwt_required()
def get_user_friends():
    user_id = get_jwt_identity()[0]
    result = db_handler.get_friends(user_id)
    # print(result)
    json_ready_data = [{"id": item[0], "username": item[1]} for item in result]
    return jsonify(json_ready_data)

# Fetch the teams that a user is a part of and not a creator
# Serve files from the upload folder
@app.route('/uploads/profile_pic/<path:filename>')
def serve_uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'default-avatar-profile-icon-of-social-media-user-vector.jpg')


def get_team_helper(user_id:int, role:str):
    """Find the users depending on the selected row"""
    try:
        teams_with_roles = db_handler.get_team(user_id, role=role)
        team_mappings_with_roles = {}
        for team_id, user_id, username, team_name, role in teams_with_roles:
            if team_id not in team_mappings_with_roles.keys():
                team_mappings_with_roles[team_id] = {'leader' : [], 'member' : [], 'team_name' : team_name}
            team_mappings_with_roles[team_id][role].append((user_id, username))
        # print(team_mappings_with_roles)
        return team_mappings_with_roles
    except Exception as e:
        print('Error finding:', user_id, role, teams_with_roles)
        print(e)


# Fetch the timestamps from a given sound_id
@app.route("/api/fetch/timestamps/<int:sound_id>", methods=["GET"])
@jwt_required()
def get_timestamps(sound_id):
    timestamps = db_handler.get_sound_timestamps(sound_id)
    transformed = {}
    team_id = db_handler.get_sound_team(sound_id)
    users = [i[-1] for i in db_handler.get_team_users(team_id)]
    for entry in timestamps:
        # Extract values
        timestamp_id, user_id, username, start_time, end_time = entry
        
        # Format times as 'MM:SS'
        start_time_str = f"{start_time.hour:02}:{start_time.minute:02}:{start_time.second:02}"
        end_time_str = f"{end_time.hour:02}:{end_time.minute:02}:{end_time.second:02}"
        
        # Add transformed entry to the list with 'id' maintained
        transformed[timestamp_id] = {
            'start_time': start_time_str,
            'end_time': end_time_str,
            'username': username
        }
    result = {}
    result['timestamps'] = transformed
    result['allowed_usernames']  = users

    return jsonify(result)

# Fetch the transcript from a given sound_id
@app.route("/api/fetch/transcript/<int:sound_id>", methods=["GET"])
@jwt_required()
def get_transcript(sound_id):
    path = db_handler.get_sound_transcription(sound_id)
    if len(path) == 0:
        return jsonify(success = False, reason = 'Transcript does not exist')
    try:
        with open(path, 'r') as f:
            return jsonify(success = True, transcript = f.read())
    except Exception as e:
        # print(e)
        # print(path)
        return jsonify(success = False, reason = 'Error finding transcript')

# Fetch playback from a sound_id
@app.route("/api/fetch/playback/<int:sound_id>", methods=["GET"])
@jwt_required()
def get_playback(sound_id):
    data = request.get_json(silent=True)
    query = """SELECT s.sound_path FROM Sound_Files s
                WHERE s.sound_id = %s;"""
    data = (sound_id,)
    try:
        path = db_handler.query(query=query, data=data)[0][0]
        print(f'Returning file: {path}')
        return send_file(
            path_or_file=path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'sound_{data[0]}.wav'
        )

    except Exception as e:
        print(e)
        print(f'Failed to find the path for: {data}')
    return jsonify({})

# Fetch all sound_ids that a user has created
@app.route("/api/fetch/user/sounds", methods=["GET"])
@jwt_required()
def get_user_sounds():
    user_id = get_jwt_identity()[0]
    sounds = db_handler.get_user_sounds(user_id)

    return jsonify(sound_ids=[i[0] for i in sounds])

# Fetch all sound_ids from a team
@app.route("/api/fetch/team/sounds/<int:team_id>", methods=["GET"])
@jwt_required()
def get_team_sound(team_id):
    team_sounds = db_handler.get_team_sounds(team_id)
    print(team_sounds)
    return jsonify([i[0] for i in team_sounds])

@app.route('/api/fetch/user/info', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()[0]
    user_info = db_handler.get_user_info(user_id)
    # print(user_info, 'help')
    try:
        return jsonify(username=user_info[0], email=user_info[1], gender=user_info[2])
    except:
        return jsonify(success = False, reason = 'Could not find details')
# endregion

# region Update and Create

@app.route('/api/save/timestamps', methods=['POST'])
@jwt_required()
def update_timestamps():
    try:
        data = request.get_json(silent=True)
        timestamps = data.get('timestamps')
        sound_id = data.get('sound_id')
        db_handler.delete_timestamps(sound_id)
        team_id = db_handler.get_sound_team(sound_id)
        users = db_handler.get_team_users(team_id)
        user_mappings = {i[1] : i[0] for i in users}
        for timestamp in timestamps.values():
            if timestamp['username'] not in user_mappings.keys():
                continue
            db_handler.insert_sound_timestamp(sound_id, user_mappings[timestamp['username']], start_time=timestamp['start_time'], end_time=timestamp['end_time'])
        # print(timestamps)
        return jsonify(success=True)
    except Exception as e:
        print(e)
        return jsonify(success=False)


def update_model(team_id, prompt=True):
    team_members = db_handler.get_team_users(team_id)
    users = [i[-1] for i in team_members]
    print(users)
    print(team_members)
    # print(team_members)
    print('PROMPT IS:', prompt)
    new_container = DataContainer(32, users, team_id)
    new_container.prepare_from_timestamps(db_handler, prompt)

    new_trainer = Trainer(new_container)
    new_trainer.train_all()
    paths = new_trainer.save_all()
    print('PATHS:',paths)
    return paths


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/api/remove/friend', methods=['POST'])
@jwt_required()
def remove_friend():
    current_user = get_jwt_identity()[0]
    data = request.get_json(silent=True)
    user_id = data.get('user_id')
    db_handler.delete_friend(current_user, user_id)
    return jsonify(success=True)


@app.route('/api/friend/decline', methods=['POST'])
@jwt_required()
def decline_friend():
    current_user = get_jwt_identity()[0]
    data = request.get_json(silent=True)
    user_id = data.get('user_id')
    db_handler.delete_friend(current_user, user_id)
    return jsonify(success=True)


@app.route('/api/friend/accept', methods=['POST'])
@jwt_required()
def accept_friend():
    current_user = get_jwt_identity()[0]
    data = request.get_json(silent=True)
    user_id = data.get('user_id')
    db_handler.update_friend_status(current_user, user_id)
    return jsonify(success=True)

@app.route('/api/update/profile_pic', methods=['POST'])
@jwt_required()
def update_profile_pic():
    try:
        current_username = get_jwt_identity()[1]
        if 'profilePicture' not in request.files or request.files['profilePicture'].filename == '':
            return jsonify(success=False, error='No file found')
        
        file = request.files['profilePicture']
        if file and allowed_file(file.filename):
            filename = f"{current_username}.jpg"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(filename, file_path)        
            file.save(file_path)
            return jsonify(success=True)
        return jsonify(success=False)
        

    except:
        return jsonify(success=False)


@app.route('/api/insert/team_member', methods=['POST'])
@jwt_required()
def insert_team_member():
    current_user = get_jwt_identity()[0]
    data = request.get_json(silent=True)
    username = data.get('username')
    team_id = data.get('team_id')
    if db_handler.is_team_leader(team_id, current_user):
        member_user_id = db_handler.insert_team_member(team_id, username)
    else:
        return jsonify(success = False, reason = 'Not the team leader')
    # db_handler.insert_team_member(data.get('username'))
    update_model(team_id, prompt = True)
    return jsonify(success = True, user_id = member_user_id)


@app.route('/api/create/team', methods=['POST'])
@jwt_required()
def create_team():
    try:
        current_user = get_jwt_identity()[0]
        current_username = get_jwt_identity()[1]
        data = request.get_json(silent=True)
        team_name = data.get('team_name')
        users = data.get('users')

        if len(users) == 0 or not all([db_handler.get_are_friends(current_username, user) for user in users]):
            print('NO')
            return jsonify(success = False, reason = "Someone isn't your friend")

        # trainer_users = [i for i in set([current_username] + users)]
        team_id = db_handler.insert_team(current_user, team_name)[0]
        for user in users:
            db_handler.insert_team_member(team_id, user)
        # for user in users:
        paths = update_model(team_id, prompt=True)
        '''print(trainer_users, team_id)
        new_team_container = DataContainer(32, trainer_users, team_id)
        new_team_container.prepare_data('full_dataset', 0.1)
        trainer = Trainer(new_team_container)


        trainer.train_all()
        paths = trainer.save_all()
        for user in users:
            db_handler.insert_team_member(team_id, user)'''

        db_handler.insert_model_file(team_id, paths['model_path'], paths['container_path'])
        return jsonify(success = True)
    except Exception as e:
        print(e)
        return jsonify(success = False)

@app.route('/api/send/friend_request', methods=['POST'])
@jwt_required()
def send_friend_request():
    try:
        current_user = get_jwt_identity()[0]
        data = request.get_json(silent=True)
        username = data.get('username')
        # print(username)
        db_handler.insert_friends(current_user, username)
        return jsonify(success = True)
    except:
        return jsonify(success = False)


# endregion

# region Login related tasks

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json(silent=True)
    username, email, password, confirmPassword, firstName, lastName = data.get('username'), data.get('email'), data.get('password'), data.get('confirmPassword'), data.get('firstName'), data.get('lastName')
    gender = data.get('gender').lower()
    if password != confirmPassword:
        return jsonify(success=False, reason='Passwords do not match')
    
    if gender not in ('male', 'female', 'other'):
        return jsonify(success=False, reason='Not a valid gender')
    try:
        user_id = db_handler.insert_user(username, password, email, gender, firstName, lastName)
    except Exception as e:
        print(e)
        return jsonify(success=False, reason='Username or email already exists')
    # print(result)
    os.mkdir(f"full_dataset\\{username}")
    os.mkdir(f"transcripts\\{username}")

    db_handler.insert_pic(user_id, f"uploads\\profile_pics\\{username}.jpg")
    return jsonify(success=True)

@app.route("/login", methods=['POST'])
def login():
    # return jsonify({'success':True})
    data = request.get_json(silent=True)
    identifier = data.get('identifier')
    password = data.get('password')
    data = (identifier, password)
    print(identifier, password)
    login_details = db_handler.get_login_details(identifier, password)
    print(login_details)
    if len(login_details) == 0:
        return jsonify({'success':False, 'reason':'Invalid Login'})
    login_details = login_details[0]

    access_token = create_access_token(identity=(login_details), expires_delta=datetime.timedelta(minutes=60))
    return jsonify(success = True, 
                   user_id = login_details[0], 
                   username = login_details[1],
                   email = login_details[2],
                   gender = login_details[3],
                   profile_image = login_details[4],
                   first_name = login_details[5],
                   last_name = login_details[6],
                   access_token=access_token)

@app.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()[0]
    print(current_user)
    try:
        teams = [i[0] for i in db_handler.get_created_teams(current_user)]
        print(teams)
    except:
        print('No teams')
        session.clear()
    for team in teams:
        # update for redundancy
        update_model(team, prompt = False)
    session.clear()
    return jsonify(success=True)

# endregion


if __name__=='__main__':
    app.run(debug=True, port=8080)