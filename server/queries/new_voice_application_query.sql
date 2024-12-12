CREATE TYPE gender_selection AS ENUM('male', 'female', 'other');

CREATE TABLE IF NOT EXISTS Sound_Files (
    "sound_id" bigint GENERATED ALWAYS AS IDENTITY,
    "user_id" bigint NOT NULL,
    "team_id" bigint DEFAULT NULL,
    "sound_path" varchar(512) NOT NULL, -- Adjusted length for flexibility
    "is_prompt" BOOLEAN DEFAULT FALSE,
    PRIMARY KEY ("sound_id")
);

CREATE TABLE IF NOT EXISTS Users (
    "user_id" bigint GENERATED ALWAYS AS IDENTITY,
    "username" varchar(32) NOT NULL UNIQUE,
    "password" varchar(32) NOT NULL,
    "email" varchar(255) NOT NULL UNIQUE,
    "gender" gender_selection NOT NULL,
    "first_name" varchar(255) NOT NULL,
    "last_name" varchar(255) NOT NULL,
    PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS Sound_Timestamps (
    "id" bigint GENERATED ALWAYS AS IDENTITY,
    "sound_id" bigint NOT NULL,
    "user_id" bigint NOT NULL,
    "start_time" time(0) without TIME ZONE NOT NULL,
    "end_time" time(0) without TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS Teams (
    "team_id" bigint GENERATED ALWAYS AS IDENTITY,
    "user_id" bigint NOT NULL, -- Creator
    "team_name" varchar(255) NOT NULL,
    PRIMARY KEY ("team_id")
);

CREATE TABLE IF NOT EXISTS Team_Members (
    "team_id" bigint NOT NULL,
    "user_id" bigint NOT NULL, -- Members
    PRIMARY KEY ("team_id", "user_id")
);

CREATE TABLE IF NOT EXISTS Friends (
    "user_a" bigint NOT NULL,
    "user_b" bigint NOT NULL,
    "status" BOOLEAN DEFAULT FALSE, -- Changed from bytea
    "timestamp" timestamp with time zone NOT NULL,
    PRIMARY KEY ("user_a", "user_b")
);

CREATE TABLE IF NOT EXISTS Model_Files (
    "team_id" bigint NOT NULL,
    "container_path" varchar(512) NOT NULL,
    "model_path" varchar(512) NOT NULL,
    PRIMARY KEY ("team_id")
);

CREATE TABLE IF NOT EXISTS Meetings (
    "meeting_id" bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "team_id" bigint NOT NULL,
    "date_time" date NOT NULL,
    "meeting_name" varchar(255) DEFAULT 'Team Meeting'
);

CREATE TABLE IF NOT EXISTS Transcription_Files (
    "sound_id" bigint NOT NULL,
    "transcription_path" varchar(512) NOT NULL,
    PRIMARY KEY ("sound_id")
);

CREATE TABLE IF NOT EXISTS Profile_Images (
    "user_id" bigint NOT NULL PRIMARY KEY,
    "image_path" varchar(255) DEFAULT '\\uploads\\profile_pics\\default-avatar-profile-icon-of-social-media-user-vector.jpg'
);

-- ADD THE NEW CONSTRAINTS
-- SOUND_FILES Team_id reference Teams
-- Users prompt_id reference Sound_Files

-- Constraints
ALTER TABLE Transcription_Files ADD CONSTRAINT "Transcription_Files_fk0" FOREIGN KEY ("sound_id") REFERENCES Sound_Files("sound_id");

ALTER TABLE Sound_Files ADD CONSTRAINT "Sound_Files_fk0" FOREIGN KEY ("user_id") REFERENCES Users("user_id");
ALTER TABLE Sound_Files ADD CONSTRAINT "Sound_Files_fk1" FOREIGN KEY ("team_id") REFERENCES Teams("team_id");

ALTER TABLE Model_Files ADD CONSTRAINT "Model_Files_fk0" FOREIGN KEY ("team_id") REFERENCES Teams("team_id");

ALTER TABLE Meetings ADD CONSTRAINT "Meetings_fk0" FOREIGN KEY ("team_id") REFERENCES Teams("team_id");

ALTER TABLE Profile_Images ADD CONSTRAINT "Profile_Images_fk0" FOREIGN KEY ("user_id") REFERENCES Users("user_id");


ALTER TABLE Sound_Timestamps ADD CONSTRAINT "Sound_Timestamps_fk0" FOREIGN KEY ("sound_id") REFERENCES Sound_Files("sound_id");
ALTER TABLE Sound_Timestamps ADD CONSTRAINT "Sound_Timestamps_fk1" FOREIGN KEY ("user_id") REFERENCES Users("user_id");

ALTER TABLE Teams ADD CONSTRAINT "Teams_fk0" FOREIGN KEY ("user_id") REFERENCES Users("user_id");

ALTER TABLE Team_Members ADD CONSTRAINT "Team_Members_fk0" FOREIGN KEY ("team_id") REFERENCES Teams("team_id");
ALTER TABLE Team_Members ADD CONSTRAINT "Team_Members_fk1" FOREIGN KEY ("user_id") REFERENCES Users("user_id");

ALTER TABLE Friends ADD CONSTRAINT "Friends_fk0" FOREIGN KEY ("user_a") REFERENCES Users("user_id");
ALTER TABLE Friends ADD CONSTRAINT "Friends_fk1" FOREIGN KEY ("user_b") REFERENCES Users("user_id");

-- Indexes
CREATE INDEX "idx_sound_files_user_id" ON Sound_Files("user_id");
CREATE INDEX "idx_team_members_user_id" ON Team_Members("user_id");
CREATE INDEX "idx_sound_timestamps_user_id" ON Sound_Timestamps("user_id");
CREATE INDEX "idx_friends_active" ON Friends("user_a", "user_b") WHERE "status" = TRUE;
