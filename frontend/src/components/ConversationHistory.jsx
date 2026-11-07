import React, { useState } from 'react';
import { History, Volume2, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

export default function ConversationHistory({ history, onClearHistory, onPlayAudio }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!history || history.length === 0) return null;

  return (
    <section className="w-full max-w-2xl mx-auto my-10 pt-6 border-t border-[#DED9CE]">
      <div className="flex items-center justify-between mb-4">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm font-bold text-[#171B1A] hover:text-[#174B43] transition-colors cursor-pointer"
        >
          <History className="w-4 h-4 text-[#C86F55]" />
          <span>Session Conversation History ({history.length})</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        <button
          type="button"
          onClick={onClearHistory}
          className="text-xs text-[#77766F] hover:text-[#C86F55] flex items-center gap-1 transition-colors cursor-pointer p-1"
          title="Clear current session history"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear History</span>
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-3">
          {history.map((item, index) => (
            <div
              key={index}
              className="bg-white border border-[#DED9CE] rounded-2xl p-4 shadow-sm hover:border-[#174B43]/30 transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-[#77766F] mb-1.5">
                <span className="font-semibold text-[#174B43] uppercase tracking-wider text-[10px] px-2 py-0.5 rounded bg-[#DCE5DB]">
                  {item.language?.toUpperCase() || 'QUERY'}
                </span>
                <span className="text-[11px]">{item.timestamp}</span>
              </div>

              <div className="mb-2">
                <p className="text-xs text-[#77766F] font-medium">Question:</p>
                <p className="text-sm font-semibold text-[#171B1A]">
                  "{item.transcript}"
                </p>
              </div>

              <div>
                <p className="text-xs text-[#77766F] font-medium">Answer:</p>
                <p className="text-sm text-[#171B1A] leading-relaxed line-clamp-3">
                  {item.answer}
                </p>
              </div>

              {item.audio && onPlayAudio && (
                <div className="mt-3 pt-2 border-t border-[#DED9CE]/60 flex items-center justify-between">
                  <span className="text-[11px] text-[#77766F] italic">
                    Source: {item.source}
                  </span>
                  <button
                    type="button"
                    onClick={() => onPlayAudio(item.audio)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#DCE5DB] text-[#174B43] hover:bg-[#174B43] hover:text-[#F3EFE5] transition-colors cursor-pointer"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>Listen</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

