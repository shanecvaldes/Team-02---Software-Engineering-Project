import React, { useState, useEffect } from "react";
import { Box, Button, Typography, Avatar, Card, Stack } from "@mui/material";
import Grid from "@mui/material/Grid2";
import ChangePasswordPopup from "./ChangePasswordPopup";

export default function ProfileInfo() {
    const [username, setUsername] = useState(localStorage.getItem('username'));
    const [firstName, setFirstName] = useState(localStorage.getItem('first_name'));
    const [lastName, setLastName] = useState(localStorage.getItem('last_name'));
    const [email, setEmail] = useState(localStorage.getItem('email'));
    const [popupOpen, setPopupOpen] = useState(false);

    const handleOpenPopup = () => {
        setPopupOpen(true);
    };

    const handleClosePopup = () => {
        setPopupOpen(false);
    };

    const handleSubmit = (passwordInfo) => {
        // Make an API call to change the password
        console.log('Password changed:', passwordInfo);
    };

    return (
        <Box sx={{ textAlign: "left", padding: 2 }}>
            <Card sx={{ padding: 2 }}>
                <Stack spacing={2}>
                    <Typography variant="h3" component="h1">
                        Profile Info
                    </Typography>
                    <Typography variant="h6" component="h2">
                        Username: {username}
                    </Typography>
                    <Typography variant="h6" component="h2">
                        Email: {email}
                    </Typography>
                    {/* Example for additional info <Button variant="contained" color="primary" sx={{ marginTop: 2 }} onClick={handleOpenPopup}>
                        Change Password
                    </Button>*/}
                    
                </Stack>
            </Card>
            <ChangePasswordPopup open={popupOpen} onClose={handleClosePopup} onSubmit={handleSubmit} />
        </Box>
    );
}
