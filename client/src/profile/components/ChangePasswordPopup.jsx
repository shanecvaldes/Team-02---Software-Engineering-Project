import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, TextField, FormControl, FormLabel, Typography } from '@mui/material';

export default function ChangePasswordPopup({ open, onClose, onSubmit }) {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        if (!isSecurePassword(newPassword)) {
            setError('Password must be at least 8 characters long and include a mix of letters, numbers, and special characters');
            return;
        }
        
        onSubmit({ currentPassword, newPassword });
        onClose();
    };

    const isSecurePassword = (password) => {
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return regex.test(password);
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Change Password</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleSubmit}>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>Current Password</FormLabel>
                        <TextField
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                        />
                    </FormControl>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>New Password</FormLabel>
                        <TextField
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                        />
                    </FormControl>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>Confirm New Password</FormLabel>
                        <TextField
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    </FormControl>
                    {error && (
                        <Typography color="error" sx={{ mt: 2 }}>
                            {error}
                        </Typography>
                    )}
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Close</Button>
                <Button type="submit" variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
            </DialogActions>
        </Dialog>
    );
}