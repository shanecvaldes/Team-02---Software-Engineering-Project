import psycopg2.errorcodes
import pyodbc
import json
import psycopg2
from datetime import datetime
# from Trainer import Trainer ah~ eh
import joblib
import os
import speech_recognition as sr
from pydub import AudioSegment
import math

# import time
class Data_Handler:
    def __init__(self, server='', db='', user='', password='', driver='{ODBC Driver 18 for SQL Server}'):
        # self.__verifyargs(server, db, user, password)
        # conn_str = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={db};UID={user};PWD={password}'
        
        self.connection = None
        self.cursor = None
        self.rows = None
        self.tables = []

        self.curr_table = None
        self.json_schema = None

        # Connect to DB
        # self.__connect(conn_str)
        db_name = input('What is the name of your database? ')
        db_password = input('What is the password to your database? ')
        self.__local_connect(db_name, db_password)

        # self.__local_connect('you db', 'your password')


    def __del__(self):
        if self.connection != None:
            self.connection.close()

    def __local_connect(self, db, password):
        self.connection = psycopg2.connect(database=db, user='postgres', password=password, host='localhost')
        self.cursor = self.connection.cursor()

    def __connect(self,conn_str):
        while True:
            try:
                self.connection = pyodbc.connect(conn_str)
                print('Connection successful')
                break
            except pyodbc.OperationalError as e:
                print('Connection timeout, trying again...')
            except:
                raise ConnectionError('Credentials incorrect')
        self.cursor = self.connection.cursor()

    def __getTables(self):
        self.cursor.execute(f'''SELECT table_schema, table_name
                                FROM information_schema.tables
                                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                                AND table_type = 'BASE TABLE'
                                ORDER BY table_schema, table_name;''')
        self.tables = [i[-1] for i in self.cursor.fetchall()]



        # self.tables = [i[-2] for i in self.cursor.fetchall()]

    def __setRows(self):
        self.cursor.execute(f'''SELECT 
                                    COLUMN_NAME, 
                                    DATA_TYPE 
                                FROM 
                                    INFORMATION_SCHEMA.COLUMNS 
                                WHERE 
                                    TABLE_NAME = \'{self.curr_table}\'
                                ORDER BY 
                                    ORDINAL_POSITION;''')
        # print(self.cursor.fetchall())
        self.rows = self.cursor.fetchall()

    def __verifyargs(self, server, db, user, password):
        if server == '' or db == '' or user == '' or password == '':
            raise Exception('Did not provide all connection info')

    # Getters for table(s) information
    def getTables(self):
        return self.tables
    
    def getRows(self):
        if self.curr_table != None:
            return self.rows[:]
        else:
            print('No table is set')
            
    # Initialize current table being used
    def setTable(self, table:str):
        print(table)
        if table in self.tables:
            self.curr_table = table
        else:
            print('Table not found')
            return
        self.__setRows()
        '''
        try:
            with open(f'./json/{table}.json') as f:
                self.json_schema = json.load(f)
        except Exception as e:
            print('Table does not contain json schema')
            self.json_schema = None'''
        
    def insert(self, query, data):
        # print(query)
        try:
            result = self.cursor.execute(query, data)
            if 'RETURNING' in query:
                result = self.cursor.fetchone()
            self.connection.commit()
            return result
        except Exception as e:
            # print('Yo Mr White you didn\'t give a good insert, yo:', e)
            self.connection.rollback()
            print(query)
            raise Exception('Yo Mr White you didn\'t give a good insert, yo', e)
        # return self.cursor.fetchall()

    def query(self, query, data):
        try:
            self.cursor.execute(query, data)
        except Exception as e:
            self.connection.rollback()
            raise Exception('Yo Mr White you didn\'t give a good query, yo', e)
        try:
            return self.cursor.fetchall()
        except:
            print('Nothhing was returned from the query')

    # region Delete functions
 
    # delete a user and its associated files
    def delete_timestamps(self, sound_id):
        query = """
                    DELETE FROM Sound_Timestamps CASCADE
                    WHERE sound_id = %s; 
                """
        data = (sound_id,)
        return self.insert(query, data)

    def delete_user(self, user_id):
        # update to delete path files as well
        teams = self.get_created_teams(user_id)
        for team in teams:
            self.delete_team(team[0])

        sounds = self.get_user_sounds(user_id)
        for sound in sounds:
            self.delete_team(sound[0])

        query = """
                    DELETE FROM Users CASCADE
                    WHERE user_id = %s; 
                """
        data = (user_id,)
        return self.insert(query, data)

    # delete a friend pairing
    def delete_friend(self, user_a, user_b):
        query = """
                    DELETE FROM Friends CASCADE
                    WHERE user_a = %s AND user_b = %s; 
                """
        data = (min(user_a, user_b), max(user_a, user_b))
        return self.insert(query, data)

    # delete team member from team
    def delete_team_member(self, team_id, user_id):
        query = """
                    DELETE FROM Team_Members CASCADE
                    WHERE team_id = %s AND user_id = %s; 
                """
        data = (team_id, user_id)
        return self.insert(query, data)

    # delete team and its associated files
    def delete_team(self, team_id):
        # delete all path files as well
        model_paths = self.get_team_model(team_id)[0]
        self.delete_path(model_paths[0])
        self.delete_path(model_paths[1])

        sounds = self.get_team_sounds(team_id)
        for sound in sounds:
            self.delete_sound(sound[0])
        query = """
                    DELETE FROM Teams CASCADE
                    WHERE team_id = %s; 
                """
        data = (team_id,)
        return self.insert(query, data)

    # delete the meetings <= timestamp
    def delete_meeting(self, meeting_id):
        query = """
                    DELETE FROM Meetings CASCADE
                    WHERE meeting_id = %s; 
                """
        data = (meeting_id,)
        return self.insert(query, data)

    # delete the sound file and its associated files
    def delete_sound(self, sound_id):
        # delete path file as well
        try:
            sound_path = self.get_sound_path(sound_id)[0][0]
            transcription_path = self.get_sound_transcription(sound_id)[0][0]
        except:
            print('Did not find paths')

        self.delete_path(sound_path)
        self.delete_path(transcription_path)

        query = """
                    DELETE FROM Sound_Files CASCADE
                    WHERE sound_id = %s; 
                """
        data = (sound_id,)
        return self.insert(query, data)

    def delete_path(self, path):
        try:
            os.remove(path)
        except:
            raise Exception('Could not find path:', path)

    # endregion

    # region Update functions

    # update the user_info but do not allow changing of username



    def update_user_info(self, user_id, password, email, gender):
        query = """
                    UPDATE Users
                    SET password = %s, email = %s, gender = %s
                    WHERE user_id = %s
                    RETURNING *;

                """
        data = (password, email, gender, user_id)

        return self.insert(query, data)


        
    # update friend status to friended, delete friend if removed
    def update_friend_status(self, user_a, user_b):
        query = """
                    UPDATE Friends
                    SET status = TRUE
                    WHERE user_a = %s AND user_b = %s
                    RETURNING *;
                """
        data = (min(user_a, user_b), max(user_a, user_b))
        return self.insert(query, data)

    # update the team name
    def update_team(self, user_id, team_id, team_name):
        query = """
                    UPDATE Teams
                    SET team_name = %s
                    WHERE user_id = %s AND team_id = %s
                    RETURNING *;
                """
        data = (team_name, user_id, team_id)
        return self.insert(query, data)

    def update_meeting(self, team_id, date_time):
        query = """
                    UPDATE Meetings
                    SET date_time = %s
                    WHERE team_id = %s
                    RETURNING *;
                """
        data = (date_time, team_id)
        return self.insert(query, data)

    def update_timestamp(self, id, user_id, start_time, end_time):
        query = """
                    UPDATE Sound_Timestamps
                    SET user_id = %s, start_time = %s, end_time = %s
                    WHERE id = %s
                    RETURNING *;
                """
        data = (user_id, start_time, end_time, id)
        return self.insert(query, data)

    def update_transcript(self, sound_id, new_transcript):
        query = """
                    SELECT sound_path FROM Sound_Files
                    WHERE sound_id = %s;
                """
        data = (sound_id,)
        try:
            result = self.query(query, data)[0][0]
            with open(result, 'w') as f:
                f.write(new_transcript)
        except:
            raise Exception('Failed to find the transcription file')
        return True

    # endregion

    # region Getter functions

    def get_sound_id(self, sound_path:str):
        query = """
                    SELECT sound_id FROM Sound_Files
                    WHERE sound_path = %s;
                """
        data = (sound_path,)
        print(sound_path, self.query(query, data))
        try:
            return self.query(query, data)[0]
        except Exception as e:
            print(e)
            return None

    def needs_prompt(self, user_id):
        query = """
                    SELECT NOT EXISTS (SELECT 1 FROM Sound_Files
                        WHERE user_id = %s and is_prompt=True);
                """
        data = (user_id, )
        return self.query(query, data)[0][0]

    def search_friend(self, user_id, identifier):
        query = """
                    SELECT u.username, u.email 
                    FROM users u
                    WHERE (u.username ILIKE %s OR u.email ILIKE %s)
                    AND u.user_id != %s
                    AND EXISTS (
                        SELECT 1
                        FROM friends f
                        WHERE ((f.user_a = u.user_id AND f.user_b = %s) 
                        OR (f.user_a = %s AND f.user_b = u.user_id)) AND f.status = TRUE
                    )
                    ORDER BY u.username ASC
                    LIMIT 10;
                """

        data = (f"{identifier}%", f"{identifier}%", user_id, user_id, user_id)
        return self.query(query, data)
    
    def is_team_leader(self, team_id, user_id):
        query = """
                    SELECT EXISTS (
                        SELECT 1
                        FROM Teams
                        WHERE team_id = %s AND user_id = %s
                    );
                """
        data = (team_id, user_id)
        return self.query(query, data)[0][0]

    def search_user(self, user_id, identifier):
        query = """
                    SELECT u.username, u.email 
                    FROM users u
                    WHERE (u.username ILIKE %s OR u.email ILIKE %s)
                    AND u.user_id != %s
                    AND NOT EXISTS (
                        SELECT 1
                        FROM friends f
                        WHERE (f.user_a = u.user_id AND f.user_b = %s) 
                        OR (f.user_a = %s AND f.user_b = u.user_id)
                    )
                    ORDER BY u.username ASC
                    LIMIT 10;
                """

        data = (f"{identifier}%", f"{identifier}%", user_id, user_id, user_id)
        return self.query(query, data)

    def get_login_details(self, identifier, password):
        query = """SELECT u.user_id, u.username, u.email, u.gender, pf.image_path, u.first_name, u.last_name
                    FROM users u
                    INNER JOIN Profile_Images pf ON u.user_id = pf.user_id
                    WHERE (email = %s OR username = %s) AND password = %s;
                    """
        data = (identifier, identifier, password)
        return self.query(query, data)

    def get_team(self, user_id, role = 'leader'):
        if role == 'leader':
            query = """
                    (SELECT 
                        t.team_id, 
                        t.user_id,
                        u.username,
                        t.team_name, 
                        'leader' AS role
                    FROM Teams t
                    INNER JOIN Users u ON u.user_id = t.user_id
                    WHERE t.user_id = %s)
                    UNION ALL
                    (SELECT 
                        tm.team_id, 
                        tm.user_id,
                        u.username,
                        t.team_name, 
                        'member' AS role
                    FROM Team_Members tm
                    INNER JOIN Users u ON u.user_id = tm.user_id
                    JOIN Teams t ON tm.team_id = t.team_id
                    WHERE t.user_id = %s
                    ORDER BY team_id, role ASC);
                    """
            data = (user_id, user_id)
        elif role == 'member':
            query =     """WITH user_teams AS (SELECT 
                        tm.team_id
                        FROM Team_Members tm
                        JOIN Teams t ON tm.team_id = t.team_id
                        WHERE tm.user_id = %s)
                        (SELECT
                        t.team_id, 
                        t.user_id,
                        u.username,
                        t.team_name, 
                        'leader' AS role
                        FROM Teams t
                        INNER JOIN Users u ON t.user_id = u.user_id
                        INNER JOIN user_teams um ON t.team_id = um.team_id)
                        UNION ALL
                        (SELECT
                        t.team_id, 
                        t.user_id,
                        u.username,
                        t.team_name, 
                        'member' AS role
                        FROM Team_Members tm
                        INNER JOIN Users u ON tm.user_id = u.user_id
                        INNER JOIN user_teams um ON tm.team_id = um.team_id
                        INNER JOIN Teams t ON t.team_id = tm.team_id);
                        """
            data = (user_id,)
        return self.query(query, data)

    def get_friends(self, user_id):
        query = """
                    SELECT a.user_id, a.username, b.user_id, b.username FROM Friends f
                    INNER JOIN Users a ON a.user_id = f.user_a
                    INNER JOIN Users b ON b.user_id = f.user_b
                    WHERE (a.user_id = %s OR b.user_id = %s) AND status = TRUE;
                """
        data = (user_id, user_id)
        result = self.query(query, data)
        return_result = []
        for i in result:
            if i[0] == user_id:
                return_result.append(i[2::])
            else:
                return_result.append(i[:-2:])
        return return_result
        
    def get_accepted_friends(self, user_id):
        query = """
                    SELECT a.user_id, a.username, b.user_id, b.username FROM Friends f
                    INNER JOIN Users a ON a.user_id = f.user_a
                    INNER JOIN Users b ON b.user_id = f.user_b
                    WHERE (a.user_id = %s OR b.user_id = %s) AND status = TRUE;
                """
        data = (user_id, user_id)
        result = self.query(query, data)
        return_result = []
        for i in result:
            if i[0] == user_id:
                return_result.append(i[2::])
            else:
                return_result.append(i[:-2:])
        return return_result
    def get_pending_friends(self, user_id):
        query = """
                    SELECT a.user_id, a.username, b.user_id, b.username FROM Friends f
                    INNER JOIN Users a ON a.user_id = f.user_a
                    INNER JOIN Users b ON b.user_id = f.user_b
                    WHERE (a.user_id = %s OR b.user_id = %s) AND status = FALSE;
                """
        data = (user_id, user_id)
        result = self.query(query, data)
        return_result = []
        for i in result:
            if i[0] == user_id:
                return_result.append(i[2::])
            else:
                return_result.append(i[:-2:])
        return return_result

    def get_created_teams(self, user_id):
        query = """SELECT team_id, team_name FROM teams
                    WHERE user_id = %s;"""
        data = (user_id,)
        return self.query(query, data)
    
    def get_sound_team(self, sound_id):
        query = """
                    SELECT team_id FROM Sound_Files 
                    WHERE sound_id = %s;
                """
        data = (sound_id,)
        return self.query(query, data)[0]

    def get_team_users(self, team_id):
        query = """(SELECT u.user_id, u.username FROM Team_Members tm
                    INNER JOIN Users u ON u.user_id = tm.user_id
                    WHERE tm.team_id = %s)
                    UNION ALL 
                    (SELECT u.user_id, u.username FROM Teams t
                    INNER JOIN Users u ON u.user_id = t.user_id
                    WHERE t.team_id = %s);
                    """
        data = (team_id, team_id)
        return self.query(query, data)


    def get_team_members(self, team_id):
        query = """SELECT u.user_id, u.username FROM Team_Members tm
                    INNER JOIN Users u ON u.user_id = tm.user_id
                    WHERE tm.team_id = %s;"""
        data = (team_id,)
        return self.query(query, data)

    def get_meetings(self, user_id):
        now = datetime.now()

        # Query to fetch meetings with their participants
        query = """
            SELECT 
                m.meeting_name, 
                m.team_id, 
                m.date_time, 
                u.username AS participant
            FROM Meetings m
            INNER JOIN Teams t ON t.team_id = m.team_id
            LEFT JOIN Team_Members tm ON tm.team_id = t.team_id
            LEFT JOIN Users u ON u.user_id = tm.user_id
            WHERE t.team_id IN (
                SELECT t.team_id 
                FROM Users u
                INNER JOIN Teams t ON t.user_id = u.user_id
                WHERE u.user_id = %s
                UNION ALL 
                SELECT tm.team_id 
                FROM Users u
                INNER JOIN Team_Members tm ON tm.user_id = u.user_id
                WHERE u.user_id = %s
            )
            ORDER BY m.date_time;
        """
        data = (user_id, user_id)
        result = self.query(query, data)
        # Process the results to organize meetings with participants
        meetings = {}
        for row in result:
            meeting_name, team_id, date_time, participant = row
            meeting_key = (meeting_name, team_id, date_time)
            if meeting_key not in meetings:
                meetings[meeting_key] = []  # Initialize with an empty list
            if participant:  # Add participant if not null
                meetings[meeting_key].append({'name':participant})

        # Optional: Format the output as a list of dictionaries
        formatted_meetings = [
            {
                "meeting_name": key[0],
                "team_id": key[1],
                "date_time": key[2],
                "participants": participants
            }
            for key, participants in meetings.items()
        ]
        return formatted_meetings

    def get_all_prompt_timestamps(self, username):
        query="""SELECT s.sound_path, u.username, st.start_time, st.end_time
                    FROM Sound_Timestamps st
                    INNER JOIN Users u ON u.user_id = st.user_id
                    INNER JOIN Sound_Files s ON st.sound_id = s.sound_id
                    WHERE u.username = %s AND s.is_prompt = True;"""
        data = (username,)

        timestamps_dict = {}
        results = self.query(query, data)
        print(results)
        for sound_path, username, start_time, end_time in results:            
            # If sound_path is not in the dictionary, initialize an empty list
            if sound_path not in timestamps_dict:
                timestamps_dict[sound_path] = []
            
            # Append the user and timestamp information
            timestamps_dict[sound_path].append({
                'username': username,
                'start_time': start_time,
                'end_time': end_time
            })
        # print(timestamps_dict)
        return timestamps_dict

    def get_all_timestamps(self, username):
        query="""SELECT s.sound_path, u.username, st.start_time, st.end_time
                    FROM Sound_Timestamps st
                    INNER JOIN Users u ON u.user_id = st.user_id
                    INNER JOIN Sound_Files s ON st.sound_id = s.sound_id
                    WHERE u.username = %s;"""
        data = (username,)

        timestamps_dict = {}
        results = self.query(query, data)
        for sound_path, username, start_time, end_time in results:            
            # If sound_path is not in the dictionary, initialize an empty list
            if sound_path not in timestamps_dict:
                timestamps_dict[sound_path] = []
            
            # Append the user and timestamp information
            timestamps_dict[sound_path].append({
                'username': username,
                'start_time': start_time,
                'end_time': end_time
            })
        # print(timestamps_dict)
        return timestamps_dict


    def get_sound_timestamps(self, sound_id):
        query="""SELECT st.id, st.user_id, u.username, st.start_time, st.end_time
                    FROM Sound_Timestamps st
                    INNER JOIN Users u ON u.user_id = st.user_id
                    WHERE st.sound_id = %s
                    ;"""
        data = (sound_id,)
        return self.query(query, data)

    def get_user_sounds(self, user_id):
        query = """SELECT sound_id, sound_path, is_prompt FROM Sound_Files
                    WHERE user_id = %s AND team_id IS NULL;"""
        data = (user_id,)
        return self.query(query, data)
        
    def get_team_sounds(self, team_id):
        query = """SELECT sound_id, sound_path, is_prompt FROM Sound_Files
                    WHERE team_id = %s;"""
        data = (team_id,)
        return self.query(query, data)

    def get_team_model(self, team_id):
        query = """SELECT model_path, container_path FROM Model_Files
                    WHERE team_id = %s;"""
        data = (team_id,)
        return self.query(query, data)

    def get_sound_transcription(self, sound_id):
        query = """SELECT transcription_path FROM Transcription_Files
                    WHERE sound_id = %s;"""
        data = (sound_id,)
        try:
            return self.query(query, data)[0][0]
        except:
            print('Failed to find sound_id:', sound_id)
            return 'Error in finding transcript'

    def get_sound_path(self, sound_id):
        query = """SELECT sound_path FROM Sound_Files
                    WHERE sound_id = %s;"""
        data = (sound_id,)
        return self.query(query, data)

    # return: True or False depending on if friends
    def get_are_friends(self, username_a, username_b):
        query = """
                    WITH user_ids AS (
                        SELECT MIN(user_id) as user_a, MAX(user_id) as user_b FROM Users u
                        WHERE username IN (%s, %s)
                    )
                    SELECT EXISTS(SELECT 1 FROM Friends f, user_ids
                    WHERE f.user_a = user_ids.user_a AND f.user_b = user_ids.user_b);
                """
        data = (username_a, username_b)
        return self.query(query, data)[0][0]
    
    def get_username(self, user_id):
        query = """
                    SELECT username FROM Users
                    WHERE user_id = %s
                """
        data = (user_id,)
        return self.query(query, data)[0][0]
    
    def get_user_info(self, user_id):
        query = """
                    SELECT username, email, gender FROM Users
                    WHERE user_id = %s;
                """
        data = (user_id,)
        try:
            return self.query(query, data)[0]
        except:
            return []

    # endregion


    # region Insertion functions
    def insert_model_file(self, team_id, model_path, container_path):
        query = """INSERT INTO Model_Files (team_id, model_path, container_path) 
                    VALUES (%s, %s, %s) ON CONFLICT (team_id)
                    DO UPDATE SET 
                    (model_path, container_path) = (EXCLUDED.model_path, EXCLUDED.container_path);"""
        data = (team_id, model_path, container_path)
        self.insert(query, data)

    def insert_transcription(self, sound_id, transcription_path):
        query = """INSERT INTO Transcription_Files (sound_id, transcription_path)
                    VALUES (%s, %s) ON CONFLICT (sound_id)
                    DO UPDATE SET
                    transcription_path = EXCLUDED.Transcription_Path;"""
        data = (sound_id, transcription_path)
        self.insert(query, data)

    def insert_meeting(self, teamid, date_time):
        query = """INSERT INTO Meetings (team_id, date_time) 
                    VALUES (%s, %s) ON CONFLICT (team_id)
                    DO UPDATE SET 
                    (date_time) = (EXCLUDED.date_time);"""
        data = (teamid, date_time)
        self.insert(query, data)

    def insert_user(self, username, password, email, gender, firstName, lastName):
        query = """
                INSERT INTO users (username, password, email, gender, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING user_id;
            """
        data = (username, password, email, gender, firstName, lastName)
        return self.insert(query, data)
    
    def insert_friends(self, user_a, username):
        now = datetime.now()
        print(user_a, username)
        query = """
                    INSERT INTO friends (user_a, user_b, timestamp)
                    VALUES (%s, (SELECT user_id FROM Users WHERE username = %s), %s)
                    ON CONFLICT DO NOTHING;
                """
        data = (user_a, username, now)
        self.insert(query, data)

    def insert_pic(self, user_id, path):
        query = """
                    INSERT INTO Profile_Images (user_id, image_path)
                    VALUES (%s, %s);
                """
        data = (user_id, path)
        # print(data)
        self.insert(query, data)

    def insert_sound_file(self, user_id, sound_path, team_id=None, is_prompt=False)-> int:
        query = """
                    INSERT INTO Sound_Files (user_id, sound_path, team_id, is_prompt)
                    VALUES (%s, %s, %s, %s)
                    RETURNING sound_id;
                """
        data = (user_id, sound_path, team_id, is_prompt)
        sound_id = self.insert(query, data)

        username = self.get_username(user_id)
        # Create a transcription file if not exists
        dataset_path = 'full_dataset'
        spliced_path = 'transcripts\\'+(sound_path.removeprefix(f'{dataset_path}\\')).removesuffix('.wav')+'.txt'
        if not os.path.exists(f'transcripts\\{username}'):
            os.makedirs(f'transcripts\\{username}')

        if not os.path.exists(spliced_path):
            r = sr.Recognizer()
            audio_seg = AudioSegment.from_wav(sound_path)
            chunk_duration_ms = 10 * 60 * 1000
            
            # Calculate the number of chunks
            num_chunks = math.ceil(len(audio_seg) / chunk_duration_ms)
            for i in range(num_chunks):
                start_time = i * chunk_duration_ms
                end_time = min((i + 1) * chunk_duration_ms, len(audio_seg))
                chunk = audio_seg[start_time:end_time]
                chunk_name = f"{sound_path}_chunk_{i + 1}.wav"
                chunk.export(chunk_name, format="wav")

                with sr.AudioFile(chunk_name) as source:
                    audio = r.record(source)
                    temp = r.recognize_azure(audio, key='7dYFUYNIvUkaounK4BpomrlzBUTC3w5ZyHMFFcTnodOIhFWHBAO5JQQJ99AKACYeBjFXJ3w3AAAYACOGxmEs', location='eastus')
                with open(f'{spliced_path}', 'a') as f:
                    f.write(temp[0])
                os.remove(chunk_name)
        self.insert_transcription(sound_id, spliced_path)
        return sound_id
    
    def insert_team(self, user_id, team_name):
        query = """
                    INSERT INTO Teams (user_id, team_name)
                    VALUES (%s, %s)
                    RETURNING team_id;
                """
        data = (user_id, team_name)
        return self.insert(query, data)

    def insert_team_member(self, team_id, username):
        query = """
                    INSERT INTO Team_Members (team_id, user_id)
                    VALUES (%s, (SELECT user_id FROM Users WHERE username = %s LIMIT 1))
                    ON CONFLICT DO NOTHING
                    RETURNING user_id;
                """
        data = (team_id, username)
        return self.insert(query, data)

    def insert_sound_timestamp_username(self, sound_id, username, start_time, end_time):
        query = """
                    INSERT INTO Sound_Timestamps (sound_id, user_id, start_time, end_time)
                    VALUES (%s, (SELECT user_id FROM Users WHERE username = %s), %s, %s)
                    RETURNING id;
                """
        data = (sound_id, username, start_time, end_time)
        return self.insert(query, data)

    def insert_sound_timestamp(self, sound_id, user_id, start_time, end_time):

        query = """
                    INSERT INTO Sound_Timestamps (sound_id, user_id, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """
        data = (sound_id, user_id, start_time, end_time)
        return self.insert(query, data)
    # endregion

if __name__ == '__main__':
    db_handler = Data_Handler()
    
    print(db_handler.get_pending_friends(2))
    print(db_handler.get_are_friends('scv566s', 'scv566s'))
