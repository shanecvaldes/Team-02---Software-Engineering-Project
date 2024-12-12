import React, { useState, useEffect } from 'react';
import FormControl from '@mui/material/FormControl';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import axios from 'axios';
import { Box, Button, List, ListItem, ListItemText, useTheme } from '@mui/material';
export default function Search() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const theme = useTheme();
  const handleSearch = async (event) => {
    const value = event.target.value;
    setSearchTerm(value);

    if (value.trim() === "") {
      setSearchResults([]);
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8080/api/users/search?query=${value}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
      setSearchResults(response.data.results);
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
  };

  const handleAddFriend = (username) => {
    const postNewFriend = async () => {
      const response = await axios.post("http://localhost:8080/api/send/friend_request",
        { username },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    };
    postNewFriend();
  };

  return (
    <Box>
      <FormControl sx={{ width: { xs: '100%', md: '80%' } }} variant="outlined">
        <OutlinedInput
          size="small"
          id="search"
          placeholder="Search People..."
          sx={{ flexGrow: 1 }}
          startAdornment={
            <InputAdornment position="start" sx={{ color: 'text.primary' }}>
              <SearchRoundedIcon fontSize="small" />
            </InputAdornment>
          }
          inputProps={{
            'aria-label': 'search',
          }}
          value={searchTerm}
          onChange={handleSearch}
        />
      </FormControl>
      {searchResults.length === 0 ? null : (
        <List style={{
          zIndex: 100,
          position: 'absolute',
          backgroundColor: theme.palette.background.default,
          padding: '10px',  // Optional: Padding for the list items
          borderRadius: '8px' // Optional: Rounded corners for the list
        }}>
          {searchResults.map((user) => (
            <ListItem key={user.id}>
              <ListItemText primary={user.username} secondary={user.email} />
              <Button
                color="primary"
                onClick={() => handleAddFriend(user.username)} // Trigger the add friend action
              >
                +
              </Button>
            </ListItem>
          ))}
        </List>

      )}

    </Box>

  );
}
