import React, { useEffect, useState } from 'react';
import '/src/css/teams.css';
import axios from 'axios';
import PlaybackGrid from '../../components/PlaybackGrid.jsx';
import { Box, CircularProgress, Divider, List, ListItem, ListItemIcon, Typography } from '@mui/material';
import StartSessionButton from './StartSessionButton.jsx';

function TeamData({ selectedTeam, teamName }) {
    const [loading, setLoading] = useState(false); // Track loading state
    const [teamData, setTeamData] = useState([]); // Track fetched data
    const [error, setError] = useState(null); // Track any errors

    useEffect(() => {
        // If no team is selected, do nothing
        if (!selectedTeam) return;

        const fetchTeamData = async () => {
            setLoading(true); // Start loading
            setError(null); // Reset errors
            try {
                const response = await axios.get(`http://localhost:8080/api/fetch/team/sounds/${selectedTeam}`, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setTeamData(response.data); // Save fetched data
                console.log(teamData)
            } catch (err) {
                console.error("Error fetching team data:", err);
                setError("Failed to fetch team data."); // Save error state
            } finally {
                setLoading(false); // Stop loading
            }
        };

        fetchTeamData();
    }, [selectedTeam]); // Trigger when `selectedTeam` changes

    if (loading) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
                <Typography variant="h2">Loading data for {teamName}...</Typography>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
                <Typography variant="h2" color="error">
                    {error}
                </Typography>
            </Box>
        );
    }

    if (!teamData.length) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
                <StartSessionButton selectedTeam={selectedTeam} />

                <Typography variant="h2">{teamName}</Typography>
                <Typography variant="body1">No sound files available for this team.</Typography>
            </Box>
        );
    }

    return (
        <Box mt={4} mx={2}>
            <StartSessionButton selectedTeam={selectedTeam} />
            <Typography variant="h2" gutterBottom>
                Sound Files for {teamName}
            </Typography>
            <List>
                {teamData.map((file, index) => (
                    <React.Fragment key={index}>
                        <ListItem>
                            <PlaybackGrid sound_id={teamData[index]} />
                        </ListItem>
                        {index < teamData.length - 1 && <Divider />}
                    </React.Fragment>
                ))}
            </List>
        </Box>
    );
}

export default TeamData;
