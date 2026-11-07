import React from 'react';

export default function AudioVisualizer({ isRecording }) {
  if (!isRecording) return null;

  return (
    <div className="flex items-center justify-center gap-1.5 h-12 my-2">
      {[40, 75, 100, 60, 90, 45, 80, 95, 55, 85, 65, 35].map((height, idx) => (
        <span
          key={idx}
          className="w-1.5 rounded-full bg-gradient-to-t from-indigo-500 via-purple-500 to-pink-500 animate-pulse"
          style={{
            height: `${height}%`,
            animationDuration: `${0.4 + (idx % 5) * 0.15}s`,
            animationDelay: `${idx * 0.08}s`
          }}
        />
      ))}
    </div>
  );
}

