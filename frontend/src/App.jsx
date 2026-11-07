import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import WelcomeSection from './components/WelcomeSection';
import VoiceRecorder from './components/VoiceRecorder';
import TranscriptCard from './components/TranscriptCard';
import AnswerCard from './components/AnswerCard';
import ConversationHistory from './components/ConversationHistory';
import { checkHealth, askQuestion, queryText } from './services/api';

export default function App() {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [error, setError] = useState(null);
  const [lastFailedAudio, setLastFailedAudio] = useState(null);

  // Active interaction
  const [currentInteraction, setCurrentInteraction] = useState(null);

  // Session history
  const [history, setHistory] = useState([]);

  // Check backend health on initial load
  useEffect(() => {
    let mounted = true;
    async function verifyBackend() {
      const health = await checkHealth();
      if (mounted) {
        setBackendStatus(health.status || 'offline');
      }
    }
    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // Main voice pipeline execution
  const handleAudioReady = async (audioBlob) => {
    setError(null);
    setLastFailedAudio(audioBlob);
    setIsProcessing(true);
    setProcessingStep('Transcribing speech with Gnani Prisma...');

    try {
      // Step update for user visibility
      setTimeout(() => {
        setProcessingStep('Retrieving verified campus information...');
      }, 700);

      const result = await askQuestion(audioBlob, selectedLanguage);

      setProcessingStep('Synthesizing speech with Gnani Timbre...');

      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const interactionRecord = {
        transcript: result.transcript,
        answer: result.answer,
        source: result.source,
        category: result.category,
        is_sample: result.is_sample,
        matched: result.matched,
        audio: result.audio,
        language: result.detected_language || selectedLanguage,
        timestamp
      };

      setCurrentInteraction(interactionRecord);
      setHistory((prev) => [interactionRecord, ...prev]);
      setLastFailedAudio(null);
    } catch (err) {
      console.error('Ask question pipeline error:', err);
      setError(err.message || 'Failed to process voice query. Please try speaking again.');
    } finally {
      setIsProcessing(false);
      setProcessingStep('');
    }
  };

  // Text query execution for suggested questions
  const handleSelectQuestion = async (text, lang) => {
    setError(null);
    if (lang && lang !== selectedLanguage) {
      setSelectedLanguage(lang);
    }
    const targetLang = lang || selectedLanguage;

    setIsProcessing(true);
    setProcessingStep('Searching campus knowledge base...');

    try {
      const result = await queryText(text, targetLang);

      setProcessingStep('Synthesizing speech with Gnani Timbre...');

      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const interactionRecord = {
        transcript: text,
        answer: result.answer,
        source: result.source,
        category: result.category,
        is_sample: result.is_sample,
        matched: result.matched,
        audio: result.audio,
        language: targetLang,
        timestamp
      };

      setCurrentInteraction(interactionRecord);
      setHistory((prev) => [interactionRecord, ...prev]);
    } catch (err) {
      console.error('Suggested question error:', err);
      setError(err.message || 'Could not fetch answer for the selected question.');
    } finally {
      setIsProcessing(false);
      setProcessingStep('');
    }
  };

  const handleRetry = () => {
    if (lastFailedAudio) {
      handleAudioReady(lastFailedAudio);
    } else {
      setError(null);
    }
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  const handlePlayHistoricalAudio = (audioDataUri) => {
    if (currentInteraction) {
      setCurrentInteraction((prev) => ({
        ...prev,
        audio: audioDataUri
      }));
    }
  };

  return (
    <div className="min-h-screen bg-[#F3EFE5] text-[#171B1A] flex flex-col justify-between selection:bg-[#E8B44A] selection:text-[#171B1A]">
      {/* Editorial Header */}
      <Header
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
        backendStatus={backendStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8">
        {/* Welcome Section with Headline & Suggested Questions */}
        <WelcomeSection
          onSelectQuestion={handleSelectQuestion}
          selectedLanguage={selectedLanguage}
        />

        {/* Centerpiece Voice Interaction Panel */}
        <VoiceRecorder
          selectedLanguage={selectedLanguage}
          onAudioReady={handleAudioReady}
          isProcessing={isProcessing}
          processingStep={processingStep}
          error={error}
          onRetry={lastFailedAudio ? handleRetry : null}
        />

        {/* Live Interaction Panels */}
        {currentInteraction && (
          <div className="transition-all duration-500 ease-in-out">
            <TranscriptCard
              transcript={currentInteraction.transcript}
              language={currentInteraction.language}
            />

            <AnswerCard
              answer={currentInteraction.answer}
              source={currentInteraction.source}
              category={currentInteraction.category}
              is_sample={currentInteraction.is_sample}
              matched={currentInteraction.matched}
              audio={currentInteraction.audio}
              language={currentInteraction.language}
            />
          </div>
        )}

        {/* Session Conversation History */}
        <ConversationHistory
          history={history}
          onClearHistory={handleClearHistory}
          onPlayAudio={handlePlayHistoricalAudio}
        />
      </main>

      {/* Editorial Footer */}
      <footer className="border-t border-[#DED9CE] bg-[#F3EFE5] py-8 text-center text-xs text-[#77766F] font-sans">
        <div className="max-w-4xl mx-auto px-4 space-y-2">
          <p className="font-serif text-sm font-semibold text-[#174B43]">
            CampusVoice — Your Campus. Your Language. Your Voice.
          </p>
          <p>
            Built for the <strong className="text-[#171B1A]">Great Indian AI Internship Challenge</strong> organized by <strong className="text-[#174B43]">Gnani AI</strong>.
          </p>
          <p className="text-[11px] text-[#77766F]/80">
            Powered by Gnani Prisma v3.0 (STT) &amp; Timbre v2.5 (TTS) • Submission Target: November 10, 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
