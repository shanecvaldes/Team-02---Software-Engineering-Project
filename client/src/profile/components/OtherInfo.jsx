import { Grid2, TextareaAutosize } from "@mui/material";
import Grid from '@mui/material/Grid2';
import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import { Select, MenuItem, InputLabel, FormControl } from '@mui/material';




export default function OtherInfo() {

    const [gender, setGender] = useState(''); // State to store selected gender

    const handleChange = (event) => {
        setGender(event.target.value); // Update the state with selected gender
    };

    return (
        <Box
            component="form"
            sx={{ '& .MuiTextField-root': { m: 1, width: '50ch' } }}
            noValidate
            autoComplete="off"
        >
            <div>
                <InputLabel id="gender-select-label">Gender</InputLabel>
                <Select
                    labelId="gender-select-label"
                    value={gender}
                    onChange={handleChange}
                    label="Gender"

                >
                    <MenuItem value="male">Male</MenuItem>
                    <MenuItem value="female">Female</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                </Select>

            </div>

        </Box>

    );
}