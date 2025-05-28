'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ScrollSpinnerProps {
  size?: number;
  className?: string;
}

export const ScrollSpinner: React.FC<ScrollSpinnerProps> = ({
  size = 64,
  className = '',
}) => {
  return (
    <div className={`w-${size} h-${size} mx-auto my-24 text-scroll-purple ${className}`}>
      <motion.svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 120 120"
        fill="none"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
      >
        <circle
          cx="60"
          cy="60"
          r="58"
          stroke="currentColor"
          strokeWidth="4"
          className="opacity-20"
        />
        <path
          d="M60 20 Q80 30 80 60 Q80 90 60 100 Q40 90 40 60 Q40 30 60 20Z"
          stroke="currentColor"
          strokeWidth="4"
          fill="none"
          className="opacity-50"
        />
        <circle
          cx="60"
          cy="60"
          r="6"
          fill="currentColor"
          className="animate-scroll-pulse"
        />
      </motion.svg>
    </div>
  );
}; 