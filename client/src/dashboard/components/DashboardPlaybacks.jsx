import React, { useState, useEffect } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Typography, CircularProgress, Pagination } from '@mui/material';
import axios from 'axios';
import PlaybackGrid from '../../components/PlaybackGrid';
import PlaybackAudio from '../../components/PlaybackAudio';

export default function DashboardPlaybacks() {
    const [soundIds, setSoundIds] = useState([]); // This will hold the fetched sound_ids
    const [loading, setLoading] = useState(true);
    const [paginationModel, setPaginationModel] = React.useState({
        pageSize: 8,
        page: 0,
      });
    useEffect(() => {
        fetchPlaybacks();
    }, []);

    const fetchPlaybacks = async () => {
        setLoading(true);
        try {
            // Fetch only the sound_ids and pagination data from the backend
            const response = await axios.get(`http://localhost:8080/api/fetch/user/sounds`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            setSoundIds(response.data.sound_ids || []); // Only storing sound_ids
            // setTotalPages(response.data.totalPages || 1);
        } catch (error) {
            console.error("Error fetching sound_ids:", error);
        } finally {
            setLoading(false);
        }
    };


    const columns = [
        { field: 'id', headerName: 'ID', width: 100 },
        {
            field: 'playback',
            headerName: 'Playback',
            flex: 1,
            renderCell: (params) => (
                // The sound_id from the row is passed to the PlaybackAudio component
                <PlaybackGrid sound_id={params.row.id} />
            ),
        },
    ];

    return (
        <Box sx={{ height: 600, width: '100%', padding: 2 }}>
            <Typography variant="h4" gutterBottom>
                Playback List
            </Typography>
            {loading ? (
                <CircularProgress />
            ) : (
                <>
                    <DataGrid
                        rows={soundIds.map((soundId) => ({
                            id: soundId, // Setting each row's id as the sound_id
                        }))}
                        paginationModel={paginationModel}
                        onPaginationModelChange={setPaginationModel}
                        pageSizeOptions={[1, 3, 5, 8]}
                        columns={columns}
                        disableSelectionOnClick
                        autoHeight
                    />
                </>
            )}
        </Box>
    );
}
