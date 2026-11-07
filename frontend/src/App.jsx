import React, { useState } from 'react';
import { Mic, Volume2, Globe, Sparkles, Building2, BookOpen, Calendar, Award } from 'lucide-react';

export default function App() {
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  const languages = [
    { code: 'te', label: 'తెలుగు (Telugu)' },
    { code: 'hi', label: 'हिन्दी (Hindi)' },
    { code: 'en', label: 'English' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0d17] text-slate-100 flex flex-col justify-between selection:bg-purple-600 selection:text-white">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/40 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Mic className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                CampusVoice
              </h1>
              <p className="text-xs text-slate-400">Your Campus. Your Language. Your Voice.</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-indigo-400" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-4xl mx-auto px-4 py-12 flex-1 flex flex-col items-center justify-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-700/50 text-indigo-300 text-xs font-medium mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multilingual Voice-First Campus AI Assistant</span>
        </div>

        <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight max-w-2xl text-slate-100 mb-4 leading-tight">
          How can I help you today?
        </h2>
        <p className="text-slate-400 max-w-xl mb-10 text-base sm:text-lg">
          Ask questions naturally in Telugu, Hindi, or English. Get instant voice and text answers about events, examinations, attendance, and placements.
        </p>

        {/* Foundation Microphone Placeholder */}
        <div className="relative group mb-10">
          <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-500 opacity-30 blur-xl group-hover:opacity-75 transition duration-500"></div>
          <button
            type="button"
            className="relative w-28 h-28 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-700 text-white flex flex-col items-center justify-center shadow-2xl shadow-indigo-500/40 hover:scale-105 active:scale-95 transition-all duration-200"
          >
            <Mic className="w-10 h-10" />
            <span className="text-xs font-semibold mt-1">Tap to Speak</span>
          </button>
        </div>

        {/* Categories Preview */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-2xl text-left">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <Calendar className="w-5 h-5 text-indigo-400 mb-2" />
            <div className="text-sm font-semibold text-slate-200">Events</div>
            <div className="text-xs text-slate-400">Technical fest & hackathons</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <BookOpen className="w-5 h-5 text-purple-400 mb-2" />
            <div className="text-sm font-semibold text-slate-200">Academics</div>
            <div className="text-xs text-slate-400">Exams & syllabus schedules</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <Building2 className="w-5 h-5 text-pink-400 mb-2" />
            <div className="text-sm font-semibold text-slate-200">Attendance</div>
            <div className="text-xs text-slate-400">Eligibility & regulations</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <Award className="w-5 h-5 text-amber-400 mb-2" />
            <div className="text-sm font-semibold text-slate-200">Placements</div>
            <div className="text-xs text-slate-400">Drives & campus statistics</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-500">
        <p>CampusVoice &bull; Built for the Great Indian AI Internship Challenge &bull; Powered by Gnani AI</p>
      </footer>
    </div>
  );
}
