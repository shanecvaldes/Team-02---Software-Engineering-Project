import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, CircularProgress, CssBaseline } from '@mui/material';
import AppTheme from '../shared-theme/AppTheme';
import axios from 'axios';
// import RecordingPopup from '../teams/components/RecordingPopup';

const xThemeComponents = {
    // Add your theme customizations here
};

function PlaybackAudio({ sound_id }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [popupOpen, setPopupOpen] = useState(false);
    const [src, setSrc] = useState("");
    const mediaRef = useRef(null);
    const [loading, setLoading] = useState(true);


    const handleEnd = () => {
        setIsPlaying(false);
    };

    const fetchPlayback = async () => {
        try {
            const response = await axios.get(`http://localhost:8080/api/fetch/playback/${sound_id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
                responseType: 'blob'
            });
            const objectUrl = URL.createObjectURL(response.data);
            setSrc(objectUrl);
            setLoading(false);
        } catch (err) {
            console.log(err);
            fetchPlayback();
            setLoading(false);
        }

    };


    useEffect(() => {
        if (sound_id !== null) {
            fetchPlayback();
        }
    }, [sound_id]);

    return (
        <AppTheme themeComponents={xThemeComponents}>
            <CssBaseline enableColorScheme />
            <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
                {loading ? (
                    <CircularProgress />
                ) : (

                    <audio
                        ref={mediaRef}
                        src={src}
                        onEnded={handleEnd}
                        controls
                        style={{ width: '100%' }} // Ensures the audio player stretches across the full width
                    />
                )}

            </Box>
        </AppTheme>
    );
}

export default PlaybackAudio;