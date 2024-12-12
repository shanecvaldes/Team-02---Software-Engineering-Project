import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography, Input, FormLabel, FormControl, List } from '@mui/material';
import axios from 'axios';
import SearchUserAdd from './SeachUserAdd';

function AddNewTeam({ show, onClose, onSubmit }) {
    const [teamName, setTeamName] = useState('');
    const [users, setUsers] = useState([]);
    const [friends, setFriends] = useState([]);
    const [currentUser, setUser] = useState('');

    const fetchFriends = async () => {
        const response = await axios.get('http://localhost:8080/api/fetch/user/friends', {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setFriends(response.data);
    };

    useEffect(() => {
        if (show) {
            setUsers([]);
            setTeamName('');
            setUser('');
            fetchFriends();
        }
    }, [show]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (teamName === '') return;
        onSubmit({ teamName, users }); // Pass state as an object
        setTeamName('');  // Clear inputs after submission
        setUsers([]);
    };

    const handleNewUser = (user) => {
        setUsers((previousUsers) => [...previousUsers, user]);
        setUser('');
        console.log(users)
    };

    return (
        <Dialog open={show} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Add New Team</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleSubmit}>
                    <FormControl fullWidth margin="normal">
                        <FormLabel>Team Name</FormLabel>
                        <Input type='text' id='teamNameInput' value={teamName} onChange={(e) => setTeamName(e.target.value)} />
                    </FormControl>

                </Box>
                <SearchUserAdd onSelectNewUser={handleNewUser} />

                {users.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="h6">New Users</Typography>
                        <List>
                            {users.map((user, index) => (
                                <li key={index}>{user}</li>
                            ))}
                        </List>
                    </Box>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Close</Button>
                <Button type='submit' variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
            </DialogActions>
        </Dialog>
    );
}

export default AddNewTeam;