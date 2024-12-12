import * as React from 'react';
import Grid from '@mui/material/Grid2';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Copyright from '../../components/internals/components/Copyright';
import DashboardPlaybacks from './DashboardPlaybacks';
import ChartUserByCountry from '../../components/ChartUserByCountry';
import CustomizedTreeView from '../../components/CustomizedTreeView';
import CustomizedDataGrid from '../../components/CustomizedDataGrid';
import HighlightedCard from '../../components/HighlightedCard';
import PageViewsBarChart from '../../components/PageViewsBarChart';
import SessionsChart from './SessionsChart';
import StatCard from './StatCard';
import MeetingsGrid from './MeetingsGrid'

export default function MainGrid() {
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      {/* cards */}
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Personal Dashboard
      </Typography>
      <Grid
        container
        spacing={2}
        columns={12}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >
        <Grid size={{ xs: 12, sm: 12, lg: 12 }}>
          <MeetingsGrid />
        </Grid>
      </Grid>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Playbacks
      </Typography>
      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12, lg: 12 }}>
          <DashboardPlaybacks />
        </Grid>
      </Grid>

      <Box sx={{ mt: 'auto' }}>
        <Copyright sx={{ my: 4 }} />
      </Box>
    </Box>
  );
}
