import { Grid2, Switch } from "@mui/material";
import TeamData from "./teamData";
import TeamsCard from "./TeamsCard";
import Grid from '@mui/material/Grid2';
import React, { useEffect, useState } from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';




export default function TeamsGrid() {
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [selectedTeamName, setSelectedTeamName] = useState('');
    const [toggleState, setToggleState] = useState(false);


    const handleSelectedTeam = (team, teamName) => {
        setSelectedTeam(team);
        setSelectedTeamName(teamName);
    }


    const handleToggleChange = (event) => {
        setToggleState(event.target.checked);
    };

    return (
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Grid container spacing={2}>
                <Grid size={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2, mb: 2 }}>
                        <Typography variant="body1" sx={{ mr: 1 }}>Created Teams</Typography>
                        <Switch checked={toggleState} onChange={handleToggleChange} />
                        <Typography variant="body1" sx={{ ml: 1 }}>Member Teams</Typography>
                    </Box>
                </Grid>
                <Grid size={6}>
                    <TeamsCard toggle={toggleState} onSelectTeam={handleSelectedTeam}></TeamsCard>
                </Grid>
                <Grid size={6}>
                    <TeamData selectedTeam={selectedTeam} teamName={selectedTeamName}></TeamData>
                </Grid>
            </Grid>
        </Box>
    );
}