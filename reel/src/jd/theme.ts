import { loadFont as loadSyne } from "@remotion/google-fonts/Syne";
import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";
import { loadFont as loadMono } from "@remotion/google-fonts/SpaceMono";

export const head = loadSyne("normal", {
  weights: ["600", "800"],
  subsets: ["latin"],
}).fontFamily;
export const serifI = loadSerif("italic", {
  weights: ["400"],
  subsets: ["latin"],
}).fontFamily;
export const monoJ = loadMono("normal", {
  weights: ["400"],
  subsets: ["latin"],
}).fontFamily;

export const J = {
  charcoal: "#22252A",
  cream: "#F5F0E8",
  tan: "#D8BF98",
  terra: "#C6795B",
};

export const HANDLE = "@jorgedan.miami";
