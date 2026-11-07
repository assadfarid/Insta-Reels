import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { J, head, serifI } from "../jd/theme";
import { LINES } from "./script";

type Chunk = { words: string[]; start: number; end: number; keys: string[] };

// Split each line into 1-3 word chunks, timed proportionally to character count.
const chunks: Chunk[] = LINES.flatMap((line) => {
  const words = line.text.split(" ");
  const groups: string[][] = [];
  let cur: string[] = [];
  for (const w of words) {
    cur.push(w);
    if (
      cur.length >= 3 ||
      /[,.:?!]$/.test(w) ||
      (cur.length === 2 && w.length > 6)
    ) {
      groups.push(cur);
      cur = [];
    }
  }
  if (cur.length) groups.push(cur);
  const total = groups.reduce((s, g) => s + g.join(" ").length, 0);
  let t = line.start;
  return groups.map((g) => {
    const d = ((line.end - line.start) * g.join(" ").length) / total;
    const c = { words: g, start: t, end: t + d, keys: line.keys };
    t += d;
    return c;
  });
});

const ease = Easing.bezier(0.16, 1, 0.3, 1);

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const i = chunks.findIndex((c) => t >= c.start && t < c.end + 0.12);
  if (i < 0) return null;
  const c = chunks[i];
  const p = interpolate(t, [c.start, c.start + 0.18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        width: 960,
        top: 1360,
        display: "flex",
        justifyContent: "center",
        alignItems: "baseline",
        flexWrap: "wrap",
        gap: "0 26px",
        opacity: p,
        scale: 0.9 + 0.1 * p,
        textShadow: "0 6px 30px #00000088",
      }}
    >
      {c.words.map((w, k) => {
        const key = c.keys.includes(w);
        return key ? (
          <span
            key={k}
            style={{
              fontFamily: serifI,
              fontStyle: "italic",
              fontSize: 150,
              lineHeight: 1,
              color: J.cream,
            }}
          >
            {w.replace(/[.,?:]$/, "").toLowerCase()}
          </span>
        ) : (
          <span
            key={k}
            style={{
              fontFamily: head,
              fontWeight: 800,
              fontSize: 84,
              lineHeight: 1.15,
              color: "#fff",
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};
