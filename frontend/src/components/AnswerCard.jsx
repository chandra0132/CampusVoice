import React from 'react';
import { Sparkles, BookOpen, AlertCircle, BookmarkCheck } from 'lucide-react';
import AudioPlayer from './AudioPlayer';

export default function AnswerCard({ answer, source, category, matched, audio, language }) {
  if (!answer) return null;

  const isTelugu = language?.includes('te');
  const isHindi = language?.includes('hi');
  const isFallback = !matched;
  const isSample = source?.includes('Sample Dataset');

  return (
    <div className="w-full max-w-2xl mx-auto my-4">
      <div className="bg-white border border-[#DED9CE] rounded-3xl p-6 sm:p-7 shadow-editorial">
        {/* Header Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-[#DED9CE]/60">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl bg-[#174B43] flex items-center justify-center text-[#E8B44A]">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="font-serif text-lg font-bold text-[#174B43]">
                CampusVoice Answer
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {category && (
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#DCE5DB] text-[#174B43] border border-[#174B43]/15">
                {category}
              </span>
            )}
            {isSample && (
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                Sample Data
              </span>
            )}
            {isFallback && (
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-orange-50 text-[#C86F55] border border-[#C86F55]/30">
                Official Fallback
              </span>
            )}
          </div>
        </div>

        {/* Answer Content */}
        <div className="my-3">
          <p className={`text-base sm:text-lg text-[#171B1A] leading-relaxed ${
            isTelugu ? 'font-telugu' : isHindi ? 'font-devanagari' : 'font-sans'
          }`}>
            {answer}
          </p>
        </div>

        {/* Source Citation */}
        <div className="mt-4 pt-3 border-t border-[#DED9CE]/60 flex items-start sm:items-center gap-2 text-xs text-[#77766F]">
          {isFallback ? (
            <AlertCircle className="w-4 h-4 text-[#C86F55] shrink-0 mt-0.5 sm:mt-0" />
          ) : (
            <BookmarkCheck className="w-4 h-4 text-[#174B43] shrink-0 mt-0.5 sm:mt-0" />
          )}
          <span className="font-medium text-[#171B1A]">Source:</span>
          <span className="text-[#77766F] italic">{source || "Campus Information Handbook"}</span>
        </div>

        {/* Audio Player */}
        {audio && (
          <AudioPlayer
            audioSrc={audio}
            autoPlay={true}
            title={isTelugu ? "వాయిస్ సమాధానం (Voice Response)" : isHindi ? "आवाज में उत्तर (Voice Response)" : "Gnani Timbre Voice Response"}
          />
        )}
      </div>
    </div>
  );
}
