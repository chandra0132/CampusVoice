import React from 'react';
import { ArrowUpRight, HelpCircle } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  {
    lang: 'en',
    label: 'English',
    text: 'What are the attendance requirements?',
    category: 'Attendance'
  },
  {
    lang: 'hi',
    label: 'हिन्दी',
    text: 'कॉलेज में परीक्षा के नियम क्या हैं?',
    category: 'Examinations'
  },
  {
    lang: 'te',
    label: 'తెలుగు',
    text: 'కాలేజీలో పరీక్షల నియమాలు ఏమిటి?',
    category: 'Examinations'
  }
];

export default function WelcomeSection({ onSelectQuestion, selectedLanguage }) {
  return (
    <section className="text-center max-w-3xl mx-auto pt-8 pb-10 px-4">
      {/* Editorial Tag */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#DCE5DB] border border-[#174B43]/20 text-[#174B43] text-xs font-medium mb-6">
        <span className="w-1.5 h-1.5 rounded-full bg-[#174B43]"></span>
        <span>Multilingual Voice AI for Higher Education</span>
      </div>

      {/* Main Editorial Headline */}
      <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl text-[#171B1A] tracking-tight leading-[1.15] mb-5">
        Your campus information,{' '}
        <span className="text-[#174B43] italic font-serif">accessible</span> in your{' '}
        <span className="text-[#C86F55] font-serif">language</span>.
      </h1>

      <p className="text-base sm:text-lg text-[#77766F] max-w-xl mx-auto leading-relaxed mb-8">
        Speak naturally in Telugu, Hindi, or English. CampusVoice transcribes your speech, retrieves grounded campus notices, and answers with spoken AI voice.
      </p>

      {/* Suggested Questions Section */}
      <div className="pt-2">
        <div className="flex items-center justify-center gap-2 mb-3">
          <HelpCircle className="w-4 h-4 text-[#C86F55]" />
          <span className="text-xs font-semibold uppercase tracking-wider text-[#77766F]">
            Suggested Questions (Click to Ask)
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {SUGGESTED_QUESTIONS.map((q, idx) => {
            const isMatchLang = selectedLanguage === q.lang;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectQuestion(q.text, q.lang)}
                className={`group p-4 rounded-xl text-left border transition-all duration-200 cursor-pointer flex flex-col justify-between ${
                  isMatchLang
                    ? 'bg-white border-[#E8B44A] shadow-md hover:border-[#174B43]'
                    : 'bg-white/80 border-[#DED9CE] hover:border-[#174B43]/40 hover:bg-white'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#DCE5DB] text-[#174B43]">
                    {q.label}
                  </span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-[#77766F] group-hover:text-[#174B43] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
                <p className={`text-sm font-medium text-[#171B1A] leading-snug ${
                  q.lang === 'te' ? 'font-telugu' : q.lang === 'hi' ? 'font-devanagari' : 'font-sans'
                }`}>
                  "{q.text}"
                </p>
                <span className="text-[11px] text-[#77766F] mt-2 block">
                  {q.category}
                </span>
              </button>
            );
          })}
        </div>

        {/* Sample Data Disclaimer Note */}
        <p className="text-[11px] text-[#77766F] mt-3 italic">
          Note: Displays sample college FAQ notices until institution administration datasets are officially verified.
        </p>
      </div>
    </section>
  );
}
