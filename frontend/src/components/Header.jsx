import React from 'react';
import { Mic, Globe, Radio } from 'lucide-react';
import LanguageSelector from './LanguageSelector';

export default function Header({ selectedLanguage, onLanguageChange, backendStatus }) {
  const isOnline = backendStatus === 'healthy' || backendStatus === 'online';

  return (
    <header className="border-b border-[#DED9CE] bg-[#F3EFE5]/90 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-white border border-[#DED9CE] p-1 shadow-sm overflow-hidden flex items-center justify-center shrink-0">
            <img
              src="/logo.jpg"
              alt="CampusVoice Logo"
              className="w-full h-full object-contain rounded-xl"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-serif text-2xl font-bold tracking-tight text-[#171B1A]">
                CampusVoice
              </span>
              <span className="hidden sm:inline-block text-[11px] font-medium tracking-wider uppercase px-2 py-0.5 rounded bg-[#DCE5DB] text-[#174B43] border border-[#174B43]/20">
                Gnani AI
              </span>
            </div>
            <p className="text-xs text-[#77766F] font-sans">
              Your Campus. Your Language. Your Voice.
            </p>
          </div>
        </div>

        {/* Status & Language Controls */}
        <div className="flex items-center gap-3 sm:gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[#DED9CE] text-xs text-[#171B1A]">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-600' : 'bg-[#C86F55]'}`}></span>
            <span className="text-[11px] font-medium text-[#77766F]">
              {isOnline ? 'Speech Pipeline Ready' : 'Connecting'}
            </span>
          </div>

          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onLanguageChange={onLanguageChange}
          />
        </div>
      </div>
    </header>
  );
}
