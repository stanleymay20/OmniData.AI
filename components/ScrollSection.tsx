import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useInView } from 'react-intersection-observer';

gsap.registerPlugin(ScrollTrigger);

interface ScrollSectionProps {
  children: React.ReactNode;
  className?: string;
  snap?: boolean;
  parallax?: boolean;
  trigger?: boolean;
}

export const ScrollSection: React.FC<ScrollSectionProps> = ({
  children,
  className = '',
  snap = true,
  parallax = false,
  trigger = true,
}) => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: false,
  });

  useEffect(() => {
    if (!sectionRef.current || !trigger) return;

    const ctx = gsap.context(() => {
      if (parallax) {
        gsap.to(sectionRef.current, {
          y: '30%',
          ease: 'none',
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
          },
        });
      }

      if (inView) {
        gsap.fromTo(
          sectionRef.current,
          { opacity: 0, y: 50 },
          {
            opacity: 1,
            y: 0,
            duration: 1,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: sectionRef.current,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [inView, parallax, trigger]);

  return (
    <section
      ref={sectionRef}
      data-scroll-section
      className={`relative min-h-screen w-full ${
        snap ? 'snap-start snap-always' : ''
      } ${className}`}
    >
      <div ref={ref} className="h-full w-full">
        {children}
      </div>
    </section>
  );
}; 