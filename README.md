# Voice ML Project
## How to run
### Server
Before running any of the server scripts, please download and install pgAdmin4.
The default port is 5432.

Please create a table and name it whatever you'd like, as long as the python scripts can
find the database, it should work.

Run pip install -r requirements.txt just in case while in the Voice-ML-Project/server directory to install 
all server dependencies.

Please install ffmpegif you do not have ffmpeg installed, you can install it through chocolatey by running:
choco install ffmpeg

Before running, I suggest running the inserts.py file to create the initial tables and the insertions.

Whenever you run the server_main.py or inserts.py, you will be prompted for your pgAdmin4 credentials.
If you would like to automate this process, please go to line 33 to change the db_name and password, and uncomment it. Comment out lines 29-31.

After running the queries, you will get some errors in the query handling, these are comments and should be ignored.

Once the insertions are completed, some models and data containers will appear in the model_data folder. This
means that every thing was completed and now you can run server_main.py.

### Client
We used node.js to run all of our front end, so please make sure the npm is installed on your device.

From the client directory in a new terminal, please run 'npm install' to make sure that all dependencies are installed.
From the client directory in a new terminal, run 'npm run dev' to initiate the front end.

### Other Notes
This project was made in collaboration with Milo Etz, Andrew Hurt, and Curtis Krick for a software engineering project
with Missouri State University.

This project is computation heavy and not optimized. Whenever running the inserts or creating a new team,
please be aware of the amount of time it takes to train the model.

If you would like to work with an account that has more things in it, you can sign into my account
after running the inserts.py file. The username is ah258s, the password is 123. The other accounts
have material in it, but none of the teams have recording files inside of them.

For the sake of time, I removed alot of the testing files during the development, the only recordings
are the initial ML trainer recordings. Things like creating a new team, adding a team member, and logging
out all make the ML updater activate, so please keep that in mind.

There are some pretrained models with our voices, if you would like to see the training during the insertions,
uncommenting line 197 will allow the program to retrain the models after running the inserts.

If there is any trouble in running the code, please email me at shane.valdes11@gmail.com.

Thank you