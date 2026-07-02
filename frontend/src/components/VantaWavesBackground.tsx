import { useEffect, useRef } from "react";
import * as THREE from "three";
import WAVES from "vanta/dist/vanta.waves.min";

export function VantaWavesBackground() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return undefined;

    const effect = WAVES({
      el: containerRef.current,
      THREE,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 900,
      minWidth: 200,
      scale: 1,
      scaleMobile: 1,
      color: 0x08758a,
      shininess: 92,
      waveHeight: 48,
      waveSpeed: 0.88,
      zoom: 1.14
    });

    return () => {
      effect.destroy();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      className="pointer-events-none fixed -inset-x-0 -top-[36vh] z-0 h-[150vh] opacity-100"
    />
  );
}
