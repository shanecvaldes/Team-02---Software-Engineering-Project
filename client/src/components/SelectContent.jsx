import * as React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import MuiAvatar from '@mui/material/Avatar';
import { styled } from '@mui/material/styles';
import logo from '../assets/lemon.svg';

const Avatar = styled(MuiAvatar)(({ theme }) => ({
  width: 40,
  height: 40,
  backgroundColor: (theme.vars || theme).palette.background.paper,
  color: (theme.vars || theme).palette.text.secondary,
  border: `1px solid ${(theme.vars || theme).palette.divider}`,
}));

export default function SelectContent() {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Avatar src={logo} alt="Company Logo" />
      <Typography variant="h6" component="div">
        LemonLang
      </Typography>
    </Box>
  );
}