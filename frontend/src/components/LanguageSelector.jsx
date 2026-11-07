import React from 'react';

const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English', fontClass: 'font-sans' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी', fontClass: 'font-devanagari' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు', fontClass: 'font-telugu' }
];

export default function LanguageSelector({ selectedLanguage, onLanguageChange }) {
  return (
    <div
      role="radiogroup"
      aria-label="Select speech language"
      className="inline-flex p-1 rounded-xl bg-white border border-[#DED9CE] shadow-sm"
    >
      {LANGUAGES.map((lang) => {
        const isSelected = selectedLanguage === lang.code;
        return (
          <button
            key={lang.code}
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onLanguageChange(lang.code)}
            className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 cursor-pointer ${lang.fontClass} ${
              isSelected
                ? 'bg-[#174B43] text-[#F3EFE5] shadow-sm font-semibold'
                : 'text-[#171B1A] hover:bg-[#DCE5DB]/50'
            }`}
          >
            <span>{lang.native}</span>
          </button>
        );
      })}
    </div>
  );
}

