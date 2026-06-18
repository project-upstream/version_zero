"use client";

import { useState, useEffect } from "react";

export function useCounter(target: number | null, duration = 800): number | null {
  const [value, setValue] = useState<number | null>(null);

  useEffect(() => {
    if (target === null) return;
    if (target === 0) {
      setValue(0);
      return;
    }
    const start = performance.now();
    let rafId: number;
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) {
        rafId = requestAnimationFrame(tick);
      }
    };
    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, [target, duration]);

  return value;
}
