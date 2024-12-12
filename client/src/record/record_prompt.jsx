import { useState, useEffect, useRef } from 'react';
import { Box, Stack, Typography, Avatar, CssBaseline, Grid, Paper, TextField, Button, Divider } from '@mui/material';
import AppNavbar from '../components/AppNavbar';
import SideMenu from '../components/SideMenu';
import AppTheme from '../shared-theme/AppTheme';
import axios from "axios";
import RecordRTC from "recordrtc";
import Stopwatch from '../components/stopwatch';
import MicrophoneAccess from '../components/permissions';
import { useLocation } from 'react-router-dom';
import { io } from "socket.io-client";

const xThemeComponents = {
    // Your custom theme components
};

function RecordPrompt(props) {
    const [imagePath, setImagePath] = useState('');
    const [prompt, setPrompt] = useState('');
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const team_id = queryParams.get('team_id');
    const recorderRef = useRef(null);
    const [socket, setSocket] = useState(null);

    const fetchImagePath = async () => {
        try {
            const response = await fetch(`http://localhost:8080/uploads/profile_pic/${localStorage.getItem('username')}.jpg`);
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                setImagePath(url);
            } else {
                console.error('Failed to fetch image');
            }
        } catch (error) {
            console.error('Error fetching image:', error);
        }
    };

    const startRecording = async () => {
        const a = await axios.post("http://localhost:8080/session/start",
            { team_id: team_id },
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`
                }
            },
            { withCredentials: true });
        localStorage.setItem('session_token', a.data.session_token);
        record();
    };

    const record = async () => {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(async function (stream) {
            recorderRef.current = RecordRTC(stream, {
                type: 'audio',
                mimeType: 'audio/webm',
                sampleRate: 48000,
                desiredSampRate: 16000,
                timeSlice: 1000,
                frameRate: 2,
                ondataavailable: (blob) => {
                    socket.emit("audio_data", localStorage.getItem('session_token'), blob);
                }
            });
            recorderRef.current.startRecording();
        });
    };

    const endRecording = async () => {
        recorderRef.current.stopRecording(async function () {
            const blob = recorderRef.current.getBlob();
            try {
                const response = await axios.post("http://localhost:8080/session_prompt/stop",
                    { team_id: team_id },
                    {
                        headers: { Authorization: `Bearer ${localStorage.getItem('session_token')}` }
                    }
                );
                console.log(response.data);
            } catch (error) {
                console.error("Error stopping session:", error);
            }
        });
    };

    useEffect(() => {
        fetchImagePath();
        const newSocket = io("http://localhost:8080/");
        setSocket(newSocket);
        return () => newSocket.close();
    }, []);

    return (
        <AppTheme themeComponents={xThemeComponents}>
            <CssBaseline enableColorScheme />
            <Box sx={{ display: 'flex' }}>
                <SideMenu />
                <AppNavbar />
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        backgroundColor: (theme) => theme.palette.background.default,
                        overflow: 'auto',
                        p: 3,
                    }}
                >
                    <Grid container spacing={4}>
                        {/* Main Section */}
                        <Grid item xs={12} md={8}>
                            <Stack spacing={4} alignItems="center" sx={{ mt: { xs: 8, md: 0 }, pb: 5 }}>
                                {/* Username and Microphone Access */}
                                <Box sx={{ width: '100%' }}>
                                    <Grid container spacing={3} alignItems="center">
                                        <Grid item xs={12} sm={6}>
                                            <Typography variant="h5">{localStorage.getItem('username')}</Typography>
                                            <MicrophoneAccess />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <Avatar
                                                alt="Profile Picture"
                                                src={imagePath}
                                                sx={{
                                                    width: 150,
                                                    height: 150,
                                                    margin: "0 auto",
                                                    mb: 2,
                                                    border: '4px solid #fff',
                                                    boxShadow: 3,
                                                }}
                                            />
                                        </Grid>
                                    </Grid>
                                </Box>

                                {/* Stopwatch and Recording Controls */}
                                <Stopwatch
                                    startRecording={startRecording}
                                    stopRecording={endRecording}
                                />
                            </Stack>
                        </Grid>

                        {/* Prompt Section */}
                        <Grid item xs={12} md={4}>
                            <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
                                <Typography variant="h6" gutterBottom>
                                    Session Prompt
                                </Typography>
                                <Divider />
                                <Typography variant="h6" gutterBottom>
                                A quirky fox jumps over the lazy dog, quickly vexing nimble birds while bright gnomes frolic in the warm sunlight, showcasing vibrant colors of their playful kites. As fuzzy squirrels dart around the green park, they gather nuts and chase each other with joy. Nearby, a jovial child sings softly, his voice echoing under the tall trees, while curious rabbits peek out from behind bushes, all enjoying the cheerful day filled with fun and laughter.
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                </Box>
            </Box>
        </AppTheme>
    );
}

export default RecordPrompt;
