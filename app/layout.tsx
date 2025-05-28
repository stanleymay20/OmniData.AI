'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/src/locomotive-scroll.scss';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    let scroll: LocomotiveScroll;

    if (containerRef.current) {
      scroll = new LocomotiveScroll({
        el: containerRef.current,
        smooth: true,
        multiplier: 1,
        class: 'is-revealed',
        lerp: 0.05,
        smartphone: {
          smooth: false,
        },
        tablet: {
          smooth: false,
        },
      });
    }

    return () => {
      if (scroll) {
        scroll.destroy();
      }
    };
  }, []);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo(0, 0);
    }
  }, [pathname]);

  return (
    <html lang="en" className="scroll-smooth">
      <body>
        <div
          ref={containerRef}
          data-scroll-container
          className="min-h-screen w-full overflow-x-hidden"
        >
          {children}
        </div>
      </body>
    </html>
  );
} 