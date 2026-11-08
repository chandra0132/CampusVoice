import React from 'react';
import { Sparkles, AlertCircle, BookmarkCheck, ExternalLink, ShieldCheck, Info } from 'lucide-react';
import AudioPlayer from './AudioPlayer';

export default function AnswerCard({
  answer,
  source,
  source_url,
  applicable_regulation,
  category,
  matched,
  is_sample,
  verified = true,
  audio,
  language
}) {
  if (!answer) return null;

  const isTelugu = language?.includes('te');
  const isHindi = language?.includes('hi');
  const isFallback = !matched;
  const isSample = is_sample || source?.includes('Sample Dataset');

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

          <div className="flex flex-wrap items-center gap-2">
            {category && (
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#DCE5DB] text-[#174B43] border border-[#174B43]/15">
                {category.replace('_', ' ')}
              </span>
            )}
            {applicable_regulation && (
              <span className="text-[11px] font-semibold tracking-wide px-2 py-0.5 rounded-full bg-[#F3EFE5] text-[#171B1A] border border-[#DED9CE]">
                {applicable_regulation}
              </span>
            )}
            {verified && !isFallback && !isSample && (
              <span className="text-[11px] font-semibold tracking-wide px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-600" />
                Verified
              </span>
            )}
            {isSample && (
              <span className="text-[11px] font-semibold tracking-wide px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-900 border border-amber-300">
                Sample Dataset
              </span>
            )}
            {isFallback && (
              <span className="text-[11px] font-semibold tracking-wide px-2.5 py-0.5 rounded-full bg-orange-50 text-[#C86F55] border border-[#C86F55]/30">
                Administration Fallback
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

        {/* Informative Disclaimer for Sample vs Verified Data */}
        {isSample && (
          <div className="mt-3 p-2.5 rounded-xl bg-[#F3EFE5]/80 border border-[#DED9CE] text-[11px] text-[#77766F] flex items-center gap-2">
            <Info className="w-3.5 h-3.5 text-[#E8B44A] shrink-0" />
            <span>
              This answer is from sample campus notices for the AI Challenge demo. Official institution policies will be reflected once administrative verification is complete.
            </span>
          </div>
        )}

        {/* Source Citation */}
        <div className="mt-4 pt-3 border-t border-[#DED9CE]/60 flex items-start sm:items-center gap-2 text-xs text-[#77766F]">
          {isFallback ? (
            <AlertCircle className="w-4 h-4 text-[#C86F55] shrink-0 mt-0.5 sm:mt-0" />
          ) : (
            <BookmarkCheck className="w-4 h-4 text-[#174B43] shrink-0 mt-0.5 sm:mt-0" />
          )}
          <span className="font-medium text-[#171B1A] shrink-0">Source:</span>
          {source_url ? (
            <a
              href={source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#174B43] hover:text-[#0E352F] hover:underline inline-flex items-center gap-1 italic break-words"
            >
              <span>{source || "NBKRIST Official Documentation"}</span>
              <ExternalLink className="w-3 h-3 shrink-0" />
            </a>
          ) : (
            <span className="text-[#77766F] italic break-words">{source || "NBKRIST Information Handbook"}</span>
          )}
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
