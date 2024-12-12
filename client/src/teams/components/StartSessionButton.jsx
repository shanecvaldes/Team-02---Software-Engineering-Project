import { Box, Button } from '@mui/material';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
export default function StartSessionButton ({ selectedTeam }) {
    const [team, setTeam] = useState(null)
    const navigate = useNavigate();


    const handleSessionStart = () => {
        navigate(`/record?team_id=${team}`)
    }

    

    useEffect(() => {
        setTeam(selectedTeam);
    }, [selectedTeam]);

    console.log(selectedTeam);

    return (
        <Box>
            <Button onClick={handleSessionStart}>
                Start Session
            </Button>

        </Box>

    );

}