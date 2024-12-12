-- Insert Users
INSERT INTO Users (username, password, email, gender, first_name, last_name)
VALUES 
    ('scv566s', '123', 'scv566s@missouristate.edu', 'male', 'Shane', 'Valdes'),
    ('ah258s', '123', 'ah258s@missouristate.edu', 'male', 'Andrew', 'Hurt'),
    ('cjk265s', '123', 'cjk265s@missouristate.edu', 'male', 'Curtis', 'Krick'),
    ('mve7s', '123', 'mve7s@missouristate.edu', 'male', 'Milo', 'Etz'),
    ('biser412', '123', 'biser412@live.missouristate.edu', 'female', 'Jenna', 'Biser'),
    ('ntc9s', '123', 'ntc9s@missouristate.edu', 'male', 'Nashod', 'Chappel')

RETURNING user_id;


-- Insert Friendships (status = TRUE for accepted friendships)
INSERT INTO Friends (user_a, user_b, status, timestamp)
VALUES 
    (1, 2, TRUE, NOW()),
    (1, 3, TRUE, NOW()),
    (1, 4, TRUE, NOW()),
    (2, 3, TRUE, NOW()),
    (2, 4, TRUE, NOW()),
    (3, 4, TRUE, NOW()),
    (1, 5, TRUE, NOW()),
    (2, 5, TRUE, NOW()),
    (3, 6, TRUE, NOW()),
    (4, 6, TRUE, NOW()),
    (5, 6, TRUE, NOW())
ON CONFLICT (user_a, user_b) DO NOTHING
;

-- Insert Pending Friendships (status = FALSE)
INSERT INTO Friends (user_a, user_b, status, timestamp)
VALUES 
    (1, 6, FALSE, NOW()),
    (2, 6, FALSE, NOW()),
    (3, 5, FALSE, NOW()),
    (4, 5, FALSE, NOW()),
    (5, 3, FALSE, NOW())
ON CONFLICT (user_a, user_b) DO NOTHING
;

-- Insert Teams
INSERT INTO Teams (user_id, team_name)
VALUES
    (1, 'The Best Team'),
    (2, 'Dream Team'),
    (3, 'Winning Squad')
;

-- Insert Team Members
INSERT INTO Team_Members (team_id, user_id)
VALUES
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 1),
    (2, 4),
    (2, 5),
    (3, 2),
    (3, 5),
    (3, 6)
ON CONFLICT (team_id, user_id) DO NOTHING
;

-- Insert Meetings
INSERT INTO Meetings (team_id, date_time, meeting_name)
VALUES
    (1, '2024-12-13 10:00:00', 'Team 1 - Strategy Planning'),
    (1, '2024-12-11 14:00:00', 'Team 1 - Product Roadmap'),
    (1, '2024-12-15 09:30:00', 'Team 1 - Marketing Review'),
    (1, '2024-12-18 16:00:00', 'Team 1 - Quarterly Budget Review'),

    (2, '2024-12-09 09:00:00', 'Team 2 - Sprint Planning'),
    (2, '2024-12-12 13:00:00', 'Team 2 - Retrospective'),
    (2, '2024-12-16 11:00:00', 'Team 2 - Product Demo'),
    (2, '2024-12-19 15:30:00', 'Team 2 - Performance Review'),

    (3, '2024-12-20 15:30:00', 'Team 3 - Annual Strategy Meeting'),
    (3, '2024-12-10 10:30:00', 'Team 3 - Development Standup'),
    (3, '2024-12-14 14:30:00', 'Team 3 - Client Feedback Session'),
    (3, '2024-12-21 16:00:00', 'Team 3 - End-of-Year Wrap-Up')
RETURNING meeting_id;



INSERT INTO Profile_Images (user_id, image_path)
VALUES
    (1, '\uploads\profile_pics\scv566s.jpg'),
    (2, DEFAULT),
    (3, '\uploads\profile_pics\cjk265s.jpg'),
    (4, DEFAULT),
    (5, DEFAULT),
    (6, DEFAULT);


INSERT INTO Model_Files
VALUES
    (3, 'model_data/data_containers/team_3.pkl', 'model_data/models/team_3_LSTM.keras'),
    (2, 'model_data/data_containers/team_2.pkl', 'model_data/models/team_2_LSTM.keras'),
    (1, 'model_data/data_containers/team_1.pkl', 'model_data/models/team_1_LSTM.keras');

