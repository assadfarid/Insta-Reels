import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadSerif } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadMono } from "@remotion/google-fonts/SpaceMono";

export const display = loadAnton("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily;
export const serif = loadSerif("italic", { weights: ["400"], subsets: ["latin"] }).fontFamily;
export const mono = loadMono("normal", { weights: ["400"], subsets: ["latin"] }).fontFamily;

export const C = {
  cream: "#EFE9E2",
  ink: "#0B0B0B",
  peach: "#F2B9A0",
  clay: "#D9805F",
};

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

export type ReelProps = {
  brand: string;
  handle: string;
  line1: string;
  line2: string;
  line3: string;
  tagline: string;
  tiles: string;
};

export const defaultProps: ReelProps = {
  brand: "YOUR BRAND",
  handle: "@yourhandle",
  line1: "MADE",
  line2: "TO BE",
  line3: "FELT",
  tagline: "a daily ritual",
  tiles: "NO.01",
};
