import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography, TextField, FormControl, FormLabel, Select, MenuItem } from '@mui/material';

export default function ChangePersonalInfoPopup({ open, onClose, onSubmit }) {
    const [firstName, setFirstName] = useState(localStorage.getItem('first_name'));
    const [lastName, setLastName] = useState(localStorage.getItem('last_name'));
    const [gender, setGender] = useState(localStorage.getItem('gender'));

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ firstName, lastName, gender });
        onClose();
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Change Personal Info</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleSubmit}>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>First Name</FormLabel>
                        <TextField
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                        />
                    </FormControl>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>Last Name</FormLabel>
                        <TextField
                            type="text"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                        />
                    </FormControl>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>Gender</FormLabel>
                        <Select
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                        >
                            <MenuItem value="female">Female</MenuItem>
                            <MenuItem value="male">Male</MenuItem>
                            <MenuItem value="other">Other</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Close</Button>
                <Button type="submit" variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
            </DialogActions>
        </Dialog>
    );
}