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
      color: 0x0a7486,
      shininess: 112,
      waveHeight: 64,
      waveSpeed: 0.92,
      zoom: 0.9
    });

    // Reuse Vanta's animated mesh so the live wave geometry stays visible under glass panels.
    const waveLineMaterial = new THREE.MeshBasicMaterial({
      color: 0xb6fbff,
      wireframe: true,
      transparent: true,
      opacity: 0.11,
      depthTest: false
    });
    const waveLines = effect.plane?.geometry ? new THREE.Mesh(effect.plane.geometry, waveLineMaterial) : null;
    if (waveLines && effect.scene) {
      waveLines.position.y += 0.7;
      effect.scene.add(waveLines);
    }

    const tuneWaveLighting = () => {
      effect.scene?.children?.forEach((child: THREE.Object3D) => {
        const light = child as THREE.Object3D & { isAmbientLight?: boolean; isPointLight?: boolean; intensity: number };

        if (light.isAmbientLight) light.intensity = 0.62;
        if (light.isPointLight) {
          light.intensity = 1.9;
          light.position.set(-180, 330, 120);
        }
      });

      const planeMaterial = effect.plane?.material as THREE.MeshPhongMaterial | undefined;
      if (planeMaterial?.specular) {
        planeMaterial.specular.set(0xe8fdff);
      }
    };

    const setPresentationAngle = () => {
      if (!containerRef.current || typeof effect.triggerMouseMove !== "function") return;

      const bounds = containerRef.current.getBoundingClientRect();
      effect.triggerMouseMove(bounds.width * 0.78, bounds.height * 0.28);
    };

    tuneWaveLighting();
    const frameId = window.requestAnimationFrame(setPresentationAngle);
    window.addEventListener("resize", setPresentationAngle);

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", setPresentationAngle);
      if (waveLines && effect.scene) {
        effect.scene.remove(waveLines);
      }
      waveLineMaterial.dispose();
      effect.destroy();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 opacity-100 brightness-110 contrast-150 saturate-150"
    />
  );
}
