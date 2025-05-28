import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface ScrollPrayerProps {
  className?: string;
  variant?: 'full' | 'short';
}

export const ScrollPrayer: React.FC<ScrollPrayerProps> = ({
  className = '',
  variant = 'full',
}) => {
  const prayerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!prayerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        prayerRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 1,
          scrollTrigger: {
            trigger: prayerRef.current,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );
    }, prayerRef);

    return () => ctx.revert();
  }, []);

  const fullPrayer = (
    <>
      "As I scroll, let what is hidden be revealed. As I move forward, let what is broken be restored. As the Scroll unfolds, may wisdom descend like rain."
    </>
  );

  const shortPrayer = (
    <>
      "Let each scroll reveal, restore, and rain wisdom."
    </>
  );

  return (
    <div
      ref={prayerRef}
      className={`text-center italic text-gray-600 dark:text-gray-300 ${className}`}
    >
      {variant === 'full' ? fullPrayer : shortPrayer}
    </div>
  );
}; 