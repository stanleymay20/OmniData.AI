'use client';

import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollSeal } from './ScrollSeal';

gsap.registerPlugin(ScrollTrigger);

interface ScrollSceneProps {
  children: React.ReactNode;
  className?: string;
  showSeal?: boolean;
  sealPosition?: 'top' | 'bottom' | 'left' | 'right';
  parallax?: boolean;
}

export const ScrollScene: React.FC<ScrollSceneProps> = ({
  children,
  className = '',
  showSeal = true,
  sealPosition = 'bottom',
  parallax = false,
}) => {
  const sceneRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sceneRef.current || !contentRef.current) return;

    const ctx = gsap.context(() => {
      // Base animation for content
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, y: 100 },
        {
          opacity: 1,
          y: 0,
          duration: 1.5,
          scrollTrigger: {
            trigger: sceneRef.current,
            start: 'top 80%',
            end: 'bottom 20%',
            scrub: true,
          },
        }
      );

      // Parallax effect if enabled
      if (parallax) {
        gsap.to(contentRef.current, {
          y: '30%',
          ease: 'none',
          scrollTrigger: {
            trigger: sceneRef.current,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
          },
        });
      }
    }, sceneRef);

    return () => ctx.revert();
  }, [parallax]);

  const sealClasses = {
    top: 'absolute top-4 left-1/2 transform -translate-x-1/2',
    bottom: 'absolute bottom-4 left-1/2 transform -translate-x-1/2',
    left: 'absolute left-4 top-1/2 transform -translate-y-1/2',
    right: 'absolute right-4 top-1/2 transform -translate-y-1/2',
  };

  return (
    <section
      ref={sceneRef}
      className={`relative min-h-screen w-full flex items-center justify-center snap-start ${className}`}
    >
      <div
        ref={contentRef}
        className="relative z-10 w-full max-w-4xl px-4 py-16 text-center"
      >
        {children}
      </div>
      {showSeal && (
        <div className={sealClasses[sealPosition]}>
          <ScrollSeal size={40} animateOnScroll={true} />
        </div>
      )}
    </section>
  );
}; 