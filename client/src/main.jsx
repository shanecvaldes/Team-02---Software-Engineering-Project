import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './css/index.css';
import Dashboard from './dashboard/Dashboard.jsx';
import SignIn from './sign-in/SignIn.jsx';
import Signup from './sign-up/SignUp.jsx';
import Record from './record/record.jsx';
import RecordPrompt from './record/record_prompt.jsx';
import Teams from './teams/teams.jsx';
import Profile from './profile/Profile.jsx';



createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Router>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/record" element={<Record />} />
        <Route path="/record_prompt" element={<RecordPrompt />} />

        <Route path="/teams" element={<Teams />} />
        <Route path="/profile" element={<Profile />} />

        <Route path="/" element={<Navigate to="/signin" />} />
      </Routes>
    </Router>
  </StrictMode>,
);