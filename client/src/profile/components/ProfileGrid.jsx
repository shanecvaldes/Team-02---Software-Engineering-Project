import { TextareaAutosize, TextField, Button, MenuItem, Select, InputLabel, Box } from '@mui/material';
import React, { useState, useEffect } from 'react';
import Grid from '@mui/material/Grid2';
import ProfilePicture from "./ProfilePicture.jsx";
import ProfileInfo from './ProfileInfo.jsx';
import PersonalInfo from './PersonalInfo.jsx';

export default function ProfileGrid() {

    return (

        <Grid container spacing={4}>
            {/* Profile Picture */}
            <Grid item size={12}>
                <ProfilePicture />
            </Grid>
            <Grid item size={12}>
                <ProfileInfo />
            </Grid>
            <Grid item size={12}>
                <PersonalInfo />
            </Grid>

        </Grid>

    );
}
