import React from 'react';
import { Card, CardContent, CardActions, Typography, Button, Avatar, Stack } from '@mui/material';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import EventIcon from '@mui/icons-material/Event';
import PersonIcon from '@mui/icons-material/Person';

const MeetingsCard = ({ title, time, participants }) => {
    return (
        <Card sx={{ maxWidth: 345, margin: 2, boxShadow: 3 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    <MeetingRoomIcon sx={{ mr: 1 }} /> {title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    <EventIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    {time}
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    Participants:
                </Typography>
                <Stack direction="row" spacing={1}>
                    {participants.map((participant, index) => (
                        <Avatar key={index} alt={participant.name} sx={{ bgcolor: 'primary.main' }}>
                            {participant.name.charAt(0)}
                        </Avatar>
                    ))}
                    {participants.length === 0 && (
                        <Typography variant="body2" color="text.secondary">
                            No participants
                        </Typography>
                    )}
                </Stack>
            </CardContent>
        </Card>
    );
};

export default MeetingsCard;
