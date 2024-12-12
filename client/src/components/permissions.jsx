import '/src/css/record.css';
import React, { useState, useEffect } from 'react';

function MicrophoneAccess() {
    const [isMicrophoneAllowed, setIsMicrophoneAllowed] = useState(false);

    useEffect(() => {
        const requestMicrophoneAccess = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                setIsMicrophoneAllowed(true);
                // Do something with the stream, e.g., pass it to an audio processing library
            } catch (err) {
                console.error('Error accessing microphone:', err);
            }
        };

        requestMicrophoneAccess();
    }, []);

    return (
        <div className='mic-access'>
            {isMicrophoneAllowed ? (
                <p className='fadeOut'>Microphone access granted!</p>
            ) : (
                <p className='need-perms'>Need microphone access</p>
            )}
        </div>
    );
}

export default MicrophoneAccess;