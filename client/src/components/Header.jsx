import * as React from 'react';
import Stack from '@mui/material/Stack';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import CustomDatePicker from './CustomDatePicker';
import NavbarBreadcrumbs from './NavbarBreadcrumbs';
import MenuButton from './MenuButton';
import ColorModeIconDropdown from '../shared-theme/ColorModeIconDropdown';

import Search from './Search';
import NotificationButton from './NotificationButton';

export default function Header() {
  return (
    <Stack
      direction="row"
      sx={{
        display: { xs: '', md: 'flex' },
        alignItems: { xs: 'flex-start', md: 'center' },
        justifyContent: 'space-between',
        maxWidth: { sm: '100%', md: '1700px' },
        p: 2,
        position: 'fixed',     
        top: 0,                               
        right: 0,              
        zIndex: 1000,          
      }}
      spacing={2}
    >
      {/*<NavbarBreadcrumbs /> <CustomDatePicker />*/}
      <Stack direction="row" sx={{ gap: 1 }}>
        <Search />
        <NotificationButton showBadge aria-label="Open notifications" />
        <ColorModeIconDropdown />
      </Stack>
    </Stack>
  );
}
