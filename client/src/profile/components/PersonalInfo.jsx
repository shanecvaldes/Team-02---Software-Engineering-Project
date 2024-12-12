import React, { useState, useEffect } from "react";
import { Box, Button, Typography, Avatar, Card, Stack } from "@mui/material";
import ChangePersonalInfoPopup from "./ChangePersonalInfoPopup";

export default function PersonalInfo() {
    const [username, setUsername] = useState(localStorage.getItem('username'));

    const [firstName, setFirstName] = useState(localStorage.getItem('first_name'));
    const [lastName, setLastName] = useState(localStorage.getItem('last_name'));
    const [email, setEmail] = useState(localStorage.getItem('email'));
    const [gender, setGender] = useState(localStorage.getItem('gender'));
    const [popupOpen, setPopupOpen] = useState(false);

    const handleOpenPopup = () => {
        setPopupOpen(true);
    };

    const handleClosePopup = () => {
        setPopupOpen(false);
    };

    const handleSubmit = (updatedInfo) => {
        setFirstName(updatedInfo.firstName);
        setLastName(updatedInfo.lastName);
        setEmail(updatedInfo.email);
        setGender(updatedInfo.gender);
        // Update localStorage or make an API call to save the changes
        localStorage.setItem('first_name', updatedInfo.firstName);
        localStorage.setItem('last_name', updatedInfo.lastName);
        localStorage.setItem('gender', updatedInfo.gender);
    };

    return (
        <Box sx={{ textAlign: "left", padding: 2 }}>
            <Card sx={{ padding: 2 }}>
                <Stack spacing={2}>
                    <Typography variant="h2" component="h1">
                        Personal Info
                    </Typography>
                    <Typography variant="h6" component="h2">
                        Full Name: {firstName} {lastName}
                    </Typography>

                    <Typography variant="h6" component="h2">
                        Gender: {gender.charAt(0).toUpperCase() + gender.slice(1)}
                    </Typography>

                    {/* Example for additional info<Button variant="contained" color="primary" sx={{ marginTop: 2 }} onClick={handleOpenPopup}>
                        Edit Personal Info
                    </Button> */}
                    
                </Stack>
            </Card>
            <ChangePersonalInfoPopup open={popupOpen} onClose={handleClosePopup} onSubmit={handleSubmit} />
        </Box>
    );
}
