import React from 'react';
import Image from 'next/image';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface MiniScrollSealProps {
  size?: number;
  className?: string;
  animateOnHover?: boolean;
}

export const MiniScrollSeal: React.FC<MiniScrollSealProps> = ({
  size = 24,
  className = '',
  animateOnHover = true,
}) => {
  return (
    <div
      className={`relative w-${size} h-${size} opacity-50 hover:opacity-100 transition-opacity duration-300 ${
        animateOnHover ? 'hover:animate-scroll-spin' : ''
      } ${className}`}
    >
      <Image
        src="/scroll-seal.svg"
        alt="Scroll Seal"
        width={size}
        height={size}
        className="w-full h-full"
      />
    </div>
  );
}; 