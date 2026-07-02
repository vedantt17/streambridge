declare module "vanta/dist/vanta.waves.min" {
  import type { Mesh, Object3D, Scene } from "three";

  export interface VantaEffect {
    destroy: () => void;
    plane?: Mesh;
    resize?: () => void;
    scene?: Scene;
    setOptions?: (options: Record<string, unknown>) => void;
    triggerMouseMove?: (x: number, y: number) => void;
  }

  export interface VantaWavesOptions {
    el: HTMLElement;
    THREE: typeof import("three");
    mouseControls?: boolean;
    touchControls?: boolean;
    gyroControls?: boolean;
    minHeight?: number;
    minWidth?: number;
    scale?: number;
    scaleMobile?: number;
    color?: number;
    shininess?: number;
    waveHeight?: number;
    waveSpeed?: number;
    zoom?: number;
    cameraPosition?: Object3D["position"];
  }

  export default function WAVES(options: VantaWavesOptions): VantaEffect;
}
