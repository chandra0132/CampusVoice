import React from 'react';
import { User, Volume2 } from 'lucide-react';

export default function TranscriptCard({ transcript, language }) {
  if (!transcript) return null;

  const isTelugu = language?.includes('te');
  const isHindi = language?.includes('hi');

  return (
    <div className="w-full max-w-2xl mx-auto my-4">
      <div className="bg-[#DCE5DB]/60 border border-[#DED9CE] rounded-2xl p-4 sm:p-5 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#174B43] flex items-center justify-center text-[#F3EFE5]">
              <User className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-wider text-[#174B43]">
              Your Question
            </span>
          </div>

          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white border border-[#DED9CE] text-[#171B1A]">
            {language?.toUpperCase() || 'AUDIO'}
          </span>
        </div>

        <p className={`text-base sm:text-lg text-[#171B1A] font-medium leading-relaxed pl-8 ${
          isTelugu ? 'font-telugu' : isHindi ? 'font-devanagari' : 'font-sans'
        }`}>
          "{transcript}"
        </p>
      </div>
    </div>
  );
}
