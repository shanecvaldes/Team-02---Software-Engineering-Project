import React, { useState, useEffect } from "react";
import { Box, Button, Typography, Avatar } from "@mui/material";
import axios from 'axios';
export default function ProfilePicture() {
    const [imagePath, setImagePath] = useState('');

    const fetchImagePath = async () => {
        try {
            const response = await fetch(`http://localhost:8080/uploads/profile_pic/${localStorage.getItem('username')}.jpg`);
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                setImagePath(url);
                
            } else {
                console.error('Failed to fetch image');
            }
        } catch (error) {
            console.error('Error fetching image:', error);
        }
    };

    useEffect(() => {
        fetchImagePath();
    }, []);

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (file) {
            setImagePath(URL.createObjectURL(file)); // Preview the uploaded image

            // Create FormData to send the file to the backend
            const formData = new FormData();
            formData.append("profilePicture", file);
            formData.append("username", localStorage.getItem("username"));

            try {
                // Send the file to the server
                const response = await axios.post(
                    "http://localhost:8080/api/update/profile_pic",
                    formData,
                    {
                        headers: { 
                            "Content-Type": "multipart/form-data",
                            Authorization: `Bearer ${localStorage.getItem('token')}` 
                        },
                    }
                );

                if (response.status === 200) {
                    console.log("File uploaded successfully:", response.data);
                    alert("Profile picture updated!");
                } else {
                    console.error("Failed to upload file");
                    alert("Failed to upload file");
                }
            } catch (error) {
                console.error("Error uploading file:", error);
                alert("Error uploading profile picture");
            }
        }
    };

    return (
        <Box sx={{ textAlign: "center" }}>
            <Avatar
                alt="Profile Picture"
                src={imagePath}
                sx={{ width: 300, height: 300, margin: "0 auto", mb: 2 }}
            />
            <Button
                variant="outlined"
                onClick={() => document.getElementById("upload-input").click()}
            >
                Add a Photo
            </Button>
            <input
                id="upload-input"
                type="file"
                accept="image/jpg"
                style={{ display: "none" }}
                onChange={handleImageUpload}
            />
        </Box>
    );
}
