import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, AlertCircle, RefreshCw } from 'lucide-react';

const LANGUAGE_LABELS = {
  en: 'English (en-IN)',
  hi: 'हिन्दी (hi-IN)',
  te: 'తెలుగు (te-IN)'
};

export default function VoiceRecorder({ selectedLanguage, onAudioReady, isProcessing, processingStep, error, onRetry }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [permissionError, setPermissionError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  // Clean up media streams and timers on unmount
  useEffect(() => {
    return () => {
      stopTracks();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const stopTracks = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const startRecording = async () => {
    setPermissionError(null);
    audioChunksRef.current = [];
    setRecordingDuration(0);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setPermissionError("Your browser does not support microphone audio recording.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        }
      });
      streamRef.current = stream;

      // Determine best supported MIME type
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
        mimeType = 'audio/ogg';
      }

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        stopTracks();
        if (timerRef.current) clearInterval(timerRef.current);

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        if (audioBlob.size > 0) {
          onAudioReady(audioBlob);
        } else {
          setPermissionError("No audio was detected in the recording. Please try speaking again.");
        }
      };

      recorder.start(250); // Slice data into 250ms chunks
      setIsRecording(true);

      // Start duration timer (auto-stop at 28 seconds to comply with 30s limit)
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        setRecordingDuration(elapsed);
        if (elapsed >= 28) {
          stopRecording();
        }
      }, 500);

    } catch (err) {
      console.error("Microphone access error:", err);
      stopTracks();
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionError("Microphone permission was denied. Please allow microphone access in your browser to speak.");
      } else {
        setPermissionError("Could not access microphone: " + err.message);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins < 10 ? '0' : ''}${mins}:${remainder < 10 ? '0' : ''}${remainder}`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto my-6">
      <div className="bg-[#174B43] rounded-3xl p-6 sm:p-10 text-[#F3EFE5] shadow-2xl relative overflow-hidden">
        {/* Subtle decorative fine-line background rings */}
        <div className="absolute -right-20 -bottom-20 w-80 h-80 rounded-full border border-white/5 pointer-events-none"></div>
        <div className="absolute -left-20 -top-20 w-80 h-80 rounded-full border border-white/5 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col items-center text-center">
          {/* Header language indicator */}
          <div className="flex items-center gap-2 mb-6">
            <span className="text-xs uppercase tracking-wider font-semibold text-[#DCE5DB]">
              Input Language:
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#DCE5DB]/20 text-[#E8B44A] border border-[#E8B44A]/30 font-medium">
              {LANGUAGE_LABELS[selectedLanguage] || selectedLanguage}
            </span>
          </div>

          {/* Center Microphone Button */}
          <div className="relative my-4 flex items-center justify-center">
            {isRecording && (
              <div className="absolute w-36 h-36 rounded-full bg-[#E8B44A]/20 animate-ping"></div>
            )}
            {isRecording && (
              <div className="absolute w-44 h-44 rounded-full border border-[#E8B44A]/40 animate-pulse"></div>
            )}

            <button
              type="button"
              disabled={isProcessing}
              onClick={isRecording ? stopRecording : startRecording}
              aria-label={isRecording ? "Stop recording speech" : "Start recording speech"}
              className={`w-28 h-28 sm:w-32 sm:h-32 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-xl cursor-pointer ${
                isRecording
                  ? 'bg-[#C86F55] text-white scale-105 shadow-[#C86F55]/40 hover:bg-[#B25A42]'
                  : isProcessing
                  ? 'bg-[#DCE5DB]/20 text-[#DCE5DB] cursor-wait'
                  : 'bg-[#E8B44A] text-[#171B1A] hover:bg-[#D49E34] hover:scale-105 active:scale-95 shadow-[#E8B44A]/30 animate-warm-pulse'
              }`}
            >
              {isProcessing ? (
                <Loader2 className="w-10 h-10 animate-spin text-[#E8B44A]" />
              ) : isRecording ? (
                <Square className="w-9 h-9 fill-current" />
              ) : (
                <Mic className="w-11 h-11 text-[#171B1A]" />
              )}
            </button>
          </div>

          {/* Status Label and Waveform */}
          <div className="mt-4 min-h-[4rem] flex flex-col items-center justify-center">
            {isProcessing ? (
              <div className="flex flex-col items-center gap-2">
                <p className="text-sm font-medium text-[#E8B44A] tracking-wide">
                  {processingStep || "Processing speech with Gnani AI..."}
                </p>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#E8B44A] animate-bounce"></span>
                  <span className="w-2 h-2 rounded-full bg-[#E8B44A] animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-2 h-2 rounded-full bg-[#E8B44A] animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            ) : isRecording ? (
              <div className="flex flex-col items-center gap-2">
                <div className="flex items-center gap-2 text-rose-300 font-mono text-sm tracking-wider">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span>
                  <span>LISTENING ({formatTimer(recordingDuration)})</span>
                </div>
                {/* Visualizer Waveform */}
                <div className="flex items-center gap-1 h-6 mt-1">
                  {[30, 60, 95, 45, 80, 100, 70, 40, 85, 55, 30].map((h, i) => (
                    <span
                      key={i}
                      className="w-1 bg-[#E8B44A] rounded-full transition-all duration-150"
                      style={{
                        height: `${h}%`,
                        opacity: 0.7 + (i % 3) * 0.15
                      }}
                    />
                  ))}
                </div>
                <p className="text-xs text-[#DCE5DB]/80 mt-1">
                  Click the button to finish speaking
                </p>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-base font-serif tracking-wide text-[#F3EFE5]">
                  Tap to speak your question
                </p>
                <p className="text-xs text-[#DCE5DB]/70 mt-1">
                  Ask about attendance, upcoming events, examinations, or placements
                </p>
              </div>
            )}
          </div>

          {/* Permission or Runtime Error Message */}
          {(permissionError || error) && (
            <div className="mt-4 p-3.5 rounded-xl bg-[#C86F55]/20 border border-[#C86F55]/40 text-[#F3EFE5] text-xs flex items-center justify-between gap-3 w-full max-w-lg">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-[#E8B44A] shrink-0" />
                <span className="text-left">{permissionError || error}</span>
              </div>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="px-2.5 py-1 rounded bg-[#E8B44A] text-[#171B1A] font-semibold flex items-center gap-1 hover:bg-[#D49E34] transition-colors shrink-0"
                >
                  <RefreshCw className="w-3 h-3" /> Retry
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
