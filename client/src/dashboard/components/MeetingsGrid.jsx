import { useEffect, useState } from 'react';
import { Grid, Box, Pagination, Typography } from '@mui/material';
import MeetingsCard from './MeetingsCard';
import axios from 'axios';

const MeetingsPage = () => {
    const [meetings, setMeetings] = useState([]);
    const [page, setPage] = useState(1);  // Track the current page
    const itemsPerPage = 3;  // Number of meetings per page

    useEffect(() => {
        const fetchMeetings = async () => {
            try {
                const response = await axios.get("http://localhost:8080/api/fetch/meetings", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setMeetings(response.data.meetings)
            } catch (error) {
                console.error('Error fetching meetings:', error);
                fetchMeetings();
            }
        };

        fetchMeetings();
    }, []);

    // Calculate the meetings to display for the current page
    const handleChangePage = (event, value) => {
        setPage(value);
    };

    // Slice the meetings array for the current page
    const startIndex = (page - 1) * itemsPerPage;
    const selectedMeetings = meetings.slice(startIndex, startIndex + itemsPerPage);

    return (
        <Box sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
                Meetings
            </Typography>

            <Grid container spacing={2}>
                {/* Display meetings for the current page */}
                {selectedMeetings.map((meeting, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <MeetingsCard
                            title={meeting.meeting_name}
                            time={meeting.date_time}
                            participants={meeting.participants}
                        />
                    </Grid>
                ))}
            </Grid>

            {/* Pagination component */}
            <Pagination
                count={Math.ceil(meetings.length / itemsPerPage)}
                page={page}
                onChange={handleChangePage}
                color="primary"
                sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}
            />
        </Box>
    );
};

export default MeetingsPage;
