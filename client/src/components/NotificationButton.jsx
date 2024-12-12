import React, { useState } from 'react';
import Badge, { badgeClasses } from '@mui/material/Badge';
import IconButton from '@mui/material/IconButton';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import NotificationsPopup from './NotificationsPopup';

export default function NotificationButton({ showBadge = false }) {
    const [popupOpen, setPopupOpen] = useState(false);

    const handleOpenPopup = () => {
        setPopupOpen(true);
    };

    const handleClosePopup = () => {
        setPopupOpen(false);
    };

    return (
        <>
            <Badge
                color="error"
                variant="dot"
                invisible={!showBadge}
                sx={{ [`& .${badgeClasses.badge}`]: { right: 2, top: 2 } }}
            >
                <IconButton size="small" onClick={handleOpenPopup}>
                    <NotificationsRoundedIcon />
                </IconButton>
            </Badge>
            <NotificationsPopup open={popupOpen} onClose={handleClosePopup} />
        </>
    );
}