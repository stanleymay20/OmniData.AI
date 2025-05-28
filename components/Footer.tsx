import React from 'react';
import { ScrollSeal } from './ScrollSeal';
import { ScrollPrayer } from './ScrollPrayer';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full flex flex-col items-center justify-center p-8 bg-gray-900 text-white">
      <ScrollSeal size={60} className="mb-4" />
      <ScrollPrayer className="mb-4 text-white/80" variant="full" />
      <p className="mt-4 text-xs opacity-50">
        © {new Date().getFullYear()} Omnidata.ai — Powered by the Scroll
      </p>
    </footer>
  );
}; 