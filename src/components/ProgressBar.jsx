// src/components/ProgressBar.jsx
import React from 'react';
import '../styles/App.css'; // Import shared styles

const ProgressBar = ({ current, total }) => {
  // current is 1-based index of current step in progress
  // total is the total number of steps in progress
  if (total <= 0 || current <= 0) {
       // Optionally render nothing or an empty container if no progress to show
      // This might happen before the first real question step loads
      return <div className="progress-bar-container" style={{ opacity: 0 }}></div>;
  }

  return (
    // Wrapper controls the centering and max-width
    <div className="progress-bar-container">
        <div className="progress-bar">
        {/* Create segments based on total */}
        {Array.from({ length: total }).map((_, index) => (
            <div
            key={index}
            // Segment is active if its index (0-based) is less than the current step (1-based)
            className={`progress-segment ${index < current ? 'active' : ''}`}
            />
        ))}
        </div>
    </div>
  );
};

export default ProgressBar;
