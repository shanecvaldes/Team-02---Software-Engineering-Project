import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, List, ListItem, ListItemText } from '@mui/material';
import axios from 'axios';

export default function NotificationsPopup({ open, onClose }) {
    const [friendRequests, setFriendRequests] = useState([]);
    const [currentFriends, setCurrentFriends] = useState([]);

    useEffect(() => {
        if (open) {
            fetchFriendRequests();
        }
    }, [open]);

    const fetchFriendRequests = async () => {
        try {
            const response = await axios.get('http://localhost:8080/api/fetch/friend_requests', {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            setFriendRequests(response.data.pending_friends || []);
            setCurrentFriends(response.data.current_friends || []);
        } catch (err) {
            console.error('Error fetching friend requests:', err);
        }
    };

    // Handle Accepting a Friend Request
    const acceptFriend = async (user_id) => {
        try {
            const response = await axios.post('http://localhost:8080/api/friend/accept', 
                { user_id },
                { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
            );
            if (response.data.success) {
                fetchFriendRequests(); // Refetch to get updated data
            }
        } catch (err) {
            console.error('Error accepting friend request:', err);
        }
    };

    // Handle Declining a Friend Request
    const declineFriend = async (user_id) => {
        try {
            const response = await axios.post('http://localhost:8080/api/friend/decline', 
                { user_id },
                { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
            );
            if (response.data.success) {
                fetchFriendRequests(); // Refetch to get updated data
            }
        } catch (err) {
            console.error('Error declining friend request:', err);
        }
    };

    // Handle Removing an Accepted Friend
    const removeFriend = async (user_id) => {
        try {
            const response = await axios.post('http://localhost:8080/api/remove/friend', 
                { user_id },
                { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
            );
            if (response.data.success) {
                fetchFriendRequests(); // Refetch to get updated data
            }
        } catch (err) {
            console.error('Error removing friend:', err);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Incoming Friend Requests</DialogTitle>
            <DialogContent>
                <List>
                    {friendRequests.length > 0 ? (
                        friendRequests.map((request) => (
                            <ListItem key={request.user_id}>
                                <ListItemText primary={`From: ${request.username}`} />
                                <Button onClick={() => acceptFriend(request.user_id)} color="primary">Accept</Button>
                                <Button onClick={() => declineFriend(request.user_id)} color="secondary">Decline</Button>
                            </ListItem>
                        ))
                    ) : (
                        <ListItem>
                            <ListItemText primary="No new friend requests" />
                        </ListItem>
                    )}
                </List>
            </DialogContent>
            <DialogTitle>Current Friends</DialogTitle>
            <DialogContent>
                <List>
                    {currentFriends.length > 0 ? (
                        currentFriends.map((friend) => (
                            <ListItem key={friend.user_id}>
                                <ListItemText primary={`Friend: ${friend.username}`} />
                                <Button onClick={() => removeFriend(friend.user_id)} color="error">Remove</Button>
                            </ListItem>
                        ))
                    ) : (
                        <ListItem>
                            <ListItemText primary="No current friends" />
                        </ListItem>
                    )}
                </List>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Close</Button>
            </DialogActions>
        </Dialog>
    );
}
