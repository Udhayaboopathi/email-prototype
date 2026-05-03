"use client";

import { useEffect, useRef } from "react";

export function useInfiniteScroll(onReachEnd: () => void) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!sentinelRef.current) return;
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        onReachEnd();
      }
    });
    observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [onReachEnd]);

  return sentinelRef;
}
