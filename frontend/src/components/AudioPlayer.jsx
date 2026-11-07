import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX } from 'lucide-react';

export default function AudioPlayer({ audioSrc, autoPlay = true, title = "Gnani Timbre Voice Response" }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    if (audioRef.current && audioSrc) {
      // Stop and release previous audio before loading new stream
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = audioSrc;
      audioRef.current.load();

      if (autoPlay) {
        audioRef.current.play().then(() => {
          setIsPlaying(true);
        }).catch((err) => {
          // Many browsers require direct user gesture for audio autoplay
          console.warn("Autoplay blocked by browser policy:", err);
          setIsPlaying(false);
        });
      }
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, [audioSrc, autoPlay]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch(console.error);
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const current = audioRef.current.currentTime;
    const dur = audioRef.current.duration || 0;
    setCurrentTime(current);
    setDuration(dur);
    setProgress(dur > 0 ? (current / dur) * 100 : 0);
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setProgress(100);
  };

  const handleSeek = (e) => {
    if (!audioRef.current || !duration) return;
    const seekTime = (parseFloat(e.target.value) / 100) * duration;
    audioRef.current.currentTime = seekTime;
    setProgress(e.target.value);
  };

  const restartAudio = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = 0;
    audioRef.current.play().then(() => {
      setIsPlaying(true);
    });
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    audioRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const formatTime = (secs) => {
    if (isNaN(secs) || secs < 0) return "0:00";
    const minutes = Math.floor(secs / 60);
    const seconds = Math.floor(secs % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  if (!audioSrc) return null;

  return (
    <div className="bg-[#F3EFE5] border border-[#DED9CE] rounded-2xl p-4 mt-4 shadow-sm">
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        preload="metadata"
      />
      {/* Player header */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#174B43] animate-pulse"></span>
          <span className="text-[11px] font-semibold text-[#174B43] tracking-wider uppercase font-sans">
            {title}
          </span>
        </div>
        <div className="text-xs font-mono text-[#77766F]">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      {/* Controls and scrubber */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={togglePlay}
          aria-label={isPlaying ? "Pause voice response" : "Play voice response"}
          className="w-10 h-10 rounded-full bg-[#174B43] text-[#F3EFE5] hover:bg-[#1E5E54] flex items-center justify-center shadow-sm cursor-pointer transition-transform active:scale-95"
        >
          {isPlaying ? (
            <Pause className="w-4 h-4 fill-current" />
          ) : (
            <Play className="w-4 h-4 fill-current ml-0.5" />
          )}
        </button>

        <div className="flex-1 flex flex-col justify-center">
          <input
            type="range"
            min="0"
            max="100"
            value={progress}
            onChange={handleSeek}
            aria-label="Audio progress slider"
            className="w-full h-1.5 bg-[#DED9CE] rounded-lg appearance-none cursor-pointer accent-[#E8B44A]"
          />
        </div>

        <button
          type="button"
          onClick={restartAudio}
          aria-label="Replay audio from start"
          className="p-2 text-[#77766F] hover:text-[#171B1A] rounded-lg hover:bg-[#DCE5DB]/50 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={toggleMute}
          aria-label={isMuted ? "Unmute audio" : "Mute audio"}
          className="p-2 text-[#77766F] hover:text-[#171B1A] rounded-lg hover:bg-[#DCE5DB]/50 transition-colors cursor-pointer"
        >
          {isMuted ? <VolumeX className="w-4 h-4 text-[#C86F55]" /> : <Volume2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
