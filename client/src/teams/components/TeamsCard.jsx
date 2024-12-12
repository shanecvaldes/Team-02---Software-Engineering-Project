import React, { useEffect, useState } from 'react';
import { Box, Button, List, ListItemButton, ListItemText, ListItemIcon, Collapse } from '@mui/material';
import axios from 'axios';
import GroupIcon from '@mui/icons-material/Group';
import PersonIcon from '@mui/icons-material/Person';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

import AddNewTeam from './addnewteam.jsx';
import SearchFriend from './SearchFriend.jsx';

export default function TeamsCard({ toggle, onSelectTeam }) {
    const [memberTeams, setMemberTeams] = useState(null);
    const [createdTeams, setCreatedTeams] = useState(null);
    const [activeCollapse, setActiveCollapse] = useState('');
    const [selectedTeam, setSelectedTeam] = useState('');
    const [showNewTeamPopup, setTeamPopup] = useState(false);
    const [activeNewUser, setActiveNewUser] = useState(false);
    const [newUser, setNewUser] = useState('');
    const [currentTeams, setCurrentTeams] = useState(null);  // To store the current team list based on toggle

    useEffect(() => {
        
        const fetchAllTeams = async () => {
            try {
                const response = await axios.get("http://localhost:8080/api/fetch/teams", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setMemberTeams(response.data.memberships);
                setCreatedTeams(response.data.created);
                
            }catch (err) {
                console.error(err);
            }
        };
        fetchAllTeams();
    }, []);  // Only fetch on component mount

    useEffect(() => {
        if (memberTeams && createdTeams) {
            // Set current teams based on the toggle value
            setCurrentTeams(toggle ? memberTeams : createdTeams);
        }
    }, [toggle, memberTeams, createdTeams]);  // When toggle changes, update currentTeams

    const toggleCollapse = (name) => {
        if (activeCollapse === name) {
            setActiveCollapse('');
            setSelectedTeam(null);
            onSelectTeam(null, null);
        } else {
            setActiveCollapse(name);
            setSelectedTeam(name);
            onSelectTeam(name, currentTeams[name]?.team_name);
        }
        setActiveNewUser(false);
    };

    const handleAddNewTeam = (newTeam) => {
        const postNewTeam = async () => {
            await axios.post("http://localhost:8080/api/create/team", { team_name: newTeam.teamName, users: newTeam.users }, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`
                }
            });
        };
        postNewTeam();
        // Update the current teams list based on toggle
        // setCurrentTeams(toggle ? [...memberTeams, newTeam] : [...createdTeams, newTeam]);
    };

    const postNewUser = async (username) => {
        console.log(username);
    };

    const handleAddNewUser = (user_id, username) => {
        if (newUser.length > 0) {
            setCurrentTeams((prevTeams) => ({
                ...prevTeams,
                [selectedTeam]: {
                    ...prevTeams[selectedTeam],
                    member: [
                        ...(prevTeams[selectedTeam]?.member || []),
                        [-1, newUser],
                    ],
                },
            }));
        }
        setNewUser('');
        setActiveNewUser(false);
        postNewUser(newUser);
    };

    const createNewTeamPopup = () => {
        setTeamPopup(true);
    };

    const closeNewTeamPopup = () => {
        setTeamPopup(false);
    };

    const activateNewUser = () => {
        setActiveNewUser(true);
    };

    const teamNames = currentTeams ? Object.keys(currentTeams) : [];

    return (
        <Box>
            <AddNewTeam show={showNewTeamPopup} onClose={closeNewTeamPopup} onSubmit={handleAddNewTeam} />
            {!toggle && (
                <Button className='addTeamButton' onClick={() => createNewTeamPopup()}>
                    Add New Team
                </Button>
            )}

            <List>
                {teamNames.map((teamName) => (
                    <React.Fragment key={teamName}>
                        <ListItemButton onClick={() => toggleCollapse(teamName)}>
                            <ListItemIcon>
                                <GroupIcon />
                            </ListItemIcon>
                            <ListItemText primary={currentTeams[teamName].team_name} />
                            {activeCollapse === teamName ? <ExpandLess /> : <ExpandMore />}
                        </ListItemButton>

                        <Collapse in={activeCollapse === teamName} timeout="auto" unmountOnExit>
                            <List component="div" disablePadding>
                                {currentTeams[teamName]?.leader?.map(([id, leader], index) => (
                                    <ListItemButton key={`leader-${id}`} sx={{ pl: 4 }}>
                                        <ListItemIcon>
                                            <PersonIcon />
                                        </ListItemIcon>
                                        <ListItemText primary={`${leader} (Leader)`} />
                                    </ListItemButton>
                                ))}

                                {currentTeams[teamName]?.member?.map(([id, member], index) => (
                                    <ListItemButton key={`member-${id}`} sx={{ pl: 4 }}>
                                        <ListItemIcon>
                                            <PersonIcon />
                                        </ListItemIcon>
                                        <ListItemText primary={member} />
                                    </ListItemButton>
                                ))}

                                {!activeNewUser && <Button onClick={activateNewUser}>+</Button>}
                                {activeNewUser && toggle === false && (
                                    <Box component="form">
                                        <SearchFriend selectedTeam={teamName} onSelectNewUser={handleAddNewUser} />
                                    </Box>
                                )}
                            </List>
                        </Collapse>
                    </React.Fragment>
                ))}
            </List>
        </Box>
    );
}
