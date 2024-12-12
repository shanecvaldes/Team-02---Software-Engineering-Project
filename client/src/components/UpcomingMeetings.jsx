import React from 'react';
import '/src/css/Home.css';

const UpcomingMeetings = () => {
    const meetings = [
        { id: 1, title: "Project Kickoff", date: "2030-01-01", time: "10:00 AM" },
        { id: 2, title: "Team Standup", date: "2030-01-02", time: "9:00 AM" },
        { id: 3, title: "Client Review", date: "2030-01-03", time: "1:00 PM" },
        { id: 4, title: "Design Sync", date: "2030-01-04", time: "3:00 PM" },
        { id: 5, title: "Sprint Planning", date: "2030-01-05", time: "11:00 AM" },
        { id: 6, title: "Product Demo", date: "2030-01-06", time: "4:00 PM" },
    ];

    return (
        <div className="upcoming-meetings-container">
            <h2>Upcoming Meetings</h2>
            <div className="meeting-list">
                {meetings.map(meeting => (
                    <div key={meeting.id} className="meeting-item">
                        <p className="meeting-title">{meeting.title}</p>
                        <p className="meeting-date">{meeting.date}</p>
                        <p className="meeting-time">{meeting.time}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UpcomingMeetings;
