import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, CssBaseline, Grid } from '@mui/material';
import AppTheme from '../shared-theme/AppTheme';
import axios from 'axios';
import RecordingPopup from './RecordingPopup';
import PlaybackAudio from './PlaybackAudio';

const xThemeComponents = {
    // Add your theme customizations here
};

function PlaybackGrid({ sound_id }) {
    const [popupOpen, setPopupOpen] = useState(false);
    const [toggleState, setToggleState] = useState(false);

    const handleOpenPopup = () => {
        setPopupOpen(true);
    };

    const handleClosePopup = () => {
        setPopupOpen(false);
    };

    const handleToggleChange = (event) => {
        setToggleState(event.target.checked);
    }

    return (
        <AppTheme themeComponents={xThemeComponents}>
            <CssBaseline enableColorScheme />
            <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                <Grid container spacing={2} justifyContent="center" alignItems="center" sx={{ textAlign: 'center' }}>
                    <Grid item xs={12} sm={10}>
                        <PlaybackAudio sound_id={sound_id} />
                    </Grid>
                    <Grid item xs={12} sm={2}>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleOpenPopup}
                            sx={{ width: '100%' }}
                        >
                            View More
                        </Button>
                    </Grid>
                </Grid>
                <RecordingPopup
                    open={popupOpen}
                    onClose={handleClosePopup}
                    sound_id={sound_id}
                />
            </Box>
        </AppTheme>
    );
}

export default PlaybackGrid;
