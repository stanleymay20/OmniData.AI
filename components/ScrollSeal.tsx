import React, { useEffect, useRef } from 'react';
import Image from 'next/image';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface ScrollSealProps {
  size?: number;
  className?: string;
  animateOnScroll?: boolean;
}

export const ScrollSeal: React.FC<ScrollSealProps> = ({
  size = 80,
  className = '',
  animateOnScroll = true,
}) => {
  const sealRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!animateOnScroll || !sealRef.current) return;

    const ctx = gsap.context(() => {
      gsap.to(sealRef.current, {
        rotation: 360,
        duration: 20,
        repeat: -1,
        ease: 'none',
        scrollTrigger: {
          trigger: sealRef.current,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 0.5,
        },
      });
    }, sealRef);

    return () => ctx.revert();
  }, [animateOnScroll]);

  return (
    <div
      ref={sealRef}
      className={`flex justify-center items-center ${className}`}
    >
      <Image
        src="/scroll-seal.svg"
        alt="Scroll Seal"
        width={size}
        height={size}
        className="transition-opacity duration-300 hover:opacity-80"
      />
    </div>
  );
}; 