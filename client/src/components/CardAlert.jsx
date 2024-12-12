import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import AutoAwesomeRoundedIcon from '@mui/icons-material/AutoAwesomeRounded';
import { useNavigate } from 'react-router';

export default function CardAlert({ needsPrompt }) {
  if (!needsPrompt) return null;
  const navigate = useNavigate();
  const handleNavigation = () => {
    navigate('/record_prompt');
  };
  return (
    <Card variant="outlined" sx={{ m: 1.5, p: 1.5 }}>
      <CardContent>
        <AutoAwesomeRoundedIcon fontSize="small" />
        <Typography gutterBottom sx={{ fontWeight: 600 }}>
          Have you calibrated your voice yet?
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
          Click below to get started.
        </Typography>
        <Button onClick={handleNavigation} variant="contained" size="small" fullWidth>
          Profile Calibration
        </Button>
      </CardContent>
    </Card>
  );
}
