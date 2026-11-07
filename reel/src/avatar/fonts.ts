import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadSerif } from "@remotion/google-fonts/InstrumentSerif";

export const sans = loadInter("normal", {
  weights: ["500", "600", "700"],
  subsets: ["latin"],
}).fontFamily;
export const serif = loadSerif("italic", {
  weights: ["400"],
  subsets: ["latin"],
}).fontFamily;
export const PEACH = "#F4C9B2";
