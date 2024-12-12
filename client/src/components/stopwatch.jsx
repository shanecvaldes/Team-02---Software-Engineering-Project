import React, { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

function Stopwatch({ startRecording, stopRecording }) {
    const [isRunning, setIsRunning] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const intervalIdRef = useRef(null);
    const startTimeRef = useRef(0);

    useEffect(() => {
        if (isRunning) {
            intervalIdRef.current = setInterval(() => {
                setElapsedTime(Date.now() - startTimeRef.current);
            }, 10);
        }

        return () => clearInterval(intervalIdRef.current);
    }, [isRunning]);

    const start = () => {
        if (startRecording) startRecording(); // Call parent-provided recording logic
        setIsRunning(true);
        startTimeRef.current = Date.now() - elapsedTime;
    };

    const stop = () => {
        if (stopRecording) stopRecording(); // Call parent-provided stop logic
        setIsRunning(false);
        setElapsedTime(0);
    };

    const formatTime = () => {
        const hours = String(Math.floor(elapsedTime / (1000 * 60 * 60))).padStart(2, "0");
        const minutes = String(Math.floor((elapsedTime / (1000 * 60)) % 60)).padStart(2, "0");
        const seconds = String(Math.floor((elapsedTime / 1000) % 60)).padStart(2, "0");
        const milliseconds = String(Math.floor((elapsedTime % 1000) / 10)).padStart(2, "0");

        return `${hours}:${minutes}:${seconds}:${milliseconds}`;
    };

    return (
        <div className="stopwatch">
            <div className="display">{formatTime()}</div>
            <div className="controls">
                <button onClick={start} className="start-button" disabled={isRunning}>
                    Start
                </button>
                <button onClick={stop} className="stop-button" disabled={!isRunning}>
                    Stop
                </button>
            </div>
        </div>
    );
}

Stopwatch.propTypes = {
    startRecording: PropTypes.func.isRequired,
    stopRecording: PropTypes.func.isRequired,
};

export default Stopwatch;
