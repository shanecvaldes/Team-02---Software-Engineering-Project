import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Box,
    Typography,
    List,
    ListItem,
    Paper,
    TextField,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import PlaybackAudio from './PlaybackAudio';
import axios from 'axios';

export default function RecordingPopup({ open, onClose, sound_id }) {
    const [timestamps, setTimestamps] = useState({});
    const [allowedUsernames, setAllowedUsernames] = useState([]);
    const [transcript, setTranscript] = useState('This is a sample transcript');

    useEffect(() => {
        if (sound_id) {
            fetchData();
        }
    }, []);
    const fetchData = async () => {
        try {
            const response = await axios.get(
                `http://localhost:8080/api/fetch/timestamps/${sound_id}`,
                {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
                }
            );

            const data = response.data || {};
            setTimestamps(data.timestamps || {});
            setAllowedUsernames(data.allowed_usernames || []);

            const a = await axios.get(`http://localhost:8080/api/fetch/transcript/${sound_id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            setTranscript(a.data.transcript || '');
        } catch (err) {
            console.error('Error fetching data:', err);
            fetchData();
        }
    };

    const handleTimestampChange = (index, field, value) => {
        const updatedTimestamps = { ...timestamps };
        updatedTimestamps[index][field] = value;
        setTimestamps(updatedTimestamps);
    };

    const handleAddTimestamp = () => {
        const newId = `temp_${Date.now()}`;
        setTimestamps((prev) => ({
            ...prev,
            [newId]: { start_time: '', end_time: '', username: '' },
        }));
    };

    const handleRemoveTimestamp = (timestamp_id) => {
        const updatedTimestamps = { ...timestamps };
        delete updatedTimestamps[timestamp_id];
        setTimestamps(updatedTimestamps);
    };

    const handleSave = async () => {
        try {
            await axios.post(
                'http://localhost:8080/api/save/timestamps',
                {
                    sound_id: sound_id,
                    timestamps,
                },
                {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
                }
            );
        } catch (err) {
            console.error('Error saving data:', err);
        }
    };

    const timestampMappings = Object.keys(timestamps);

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Recording Details</DialogTitle>
            <DialogContent>
                <Box display="flex" flexDirection="column" mb={2} sx={{ height: '100%' }}>
                    {/* Upper section with transcription on the left and timestamps on the right */}
                    <Box display="flex" justifyContent="space-between" mb={2}>
                        <Paper elevation={3} sx={{ flex: 1, mr: 2, p: 2, borderRadius: 2, maxHeight: '300px', overflow: 'auto' }}>
                            <Typography variant="h6">Transcript</Typography>
                            <Typography>{transcript}</Typography>
                        </Paper>

                        <Paper elevation={3} sx={{ flex: 1, ml: 2, p: 2, borderRadius: 2, maxHeight: '300px', overflow: 'auto' }}>
                            <Typography variant="h6">Timestamps</Typography>
                            <List>
                                {timestampMappings.map((timestamp_id) => {
                                    const timestamp = timestamps[timestamp_id];
                                    return (
                                        <ListItem key={timestamp_id}>
                                            <Grid container spacing={2} alignItems="center">
                                                <Grid item xs={3}>
                                                    <TextField
                                                        label="Start Time"
                                                        value={timestamp.start_time}
                                                        onChange={(e) =>
                                                            handleTimestampChange(
                                                                timestamp_id,
                                                                'start_time',
                                                                e.target.value
                                                            )
                                                        }
                                                        fullWidth
                                                    />
                                                </Grid>
                                                <Grid item xs={3}>
                                                    <TextField
                                                        label="End Time"
                                                        value={timestamp.end_time}
                                                        onChange={(e) =>
                                                            handleTimestampChange(
                                                                timestamp_id,
                                                                'end_time',
                                                                e.target.value
                                                            )
                                                        }
                                                        fullWidth
                                                    />
                                                </Grid>
                                                <Grid item xs={3}>
                                                    <FormControl fullWidth>
                                                        <InputLabel>Username</InputLabel>
                                                        <Select
                                                            value={timestamp.username || ''}
                                                            onChange={(e) =>
                                                                handleTimestampChange(
                                                                    timestamp_id,
                                                                    'username',
                                                                    e.target.value
                                                                )
                                                            }
                                                        >
                                                            {allowedUsernames.map((username) => (
                                                                <MenuItem key={username} value={username}>
                                                                    {username}
                                                                </MenuItem>
                                                            ))}
                                                        </Select>
                                                    </FormControl>
                                                </Grid>
                                                <Grid item xs={3}>
                                                    <Button
                                                        variant="outlined"
                                                        color="secondary"
                                                        onClick={() =>
                                                            handleRemoveTimestamp(timestamp_id)
                                                        }
                                                    >
                                                        Remove
                                                    </Button>
                                                </Grid>
                                            </Grid>
                                        </ListItem>
                                    );
                                })}
                            </List>
                            <Button variant="contained" onClick={handleAddTimestamp}>
                                Add Timestamp
                            </Button>
                        </Paper>
                    </Box>

                    {/* Bottom section with playback spanning full width */}
                    <Paper elevation={3} sx={{ flex: 1, p: 2, borderRadius: 2 }}>
                        <PlaybackAudio sound_id={sound_id} />
                    </Paper>
                </Box>
            </DialogContent>

            <DialogActions>
                <Button onClick={handleSave} color="primary">
                    Save
                </Button>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    );
}
