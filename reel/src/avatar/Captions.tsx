import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { LINES } from "./script";
import { sans, serif } from "./fonts";

type Chunk = { words: string[]; start: number; end: number; keys: string[] };

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
  const i = chunks.findIndex((c) => t >= c.start && t < c.end + 0.1);
  if (i < 0) return null;
  const c = chunks[i];
  const p = interpolate(t, [c.start, c.start + 0.22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const out = interpolate(t, [c.end - 0.04, c.end + 0.1], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 72,
        width: 936,
        top: 1440,
        display: "flex",
        alignItems: "baseline",
        flexWrap: "wrap",
        gap: "0 24px",
        opacity: p * out,
        translate: `0px ${(1 - p) * 28}px`,
        filter: `blur(${(1 - p) * 10}px)`,
        textShadow: "0 4px 28px #00000066, 0 1px 2px #00000040",
      }}
    >
      {c.words.map((w, k) => {
        const key = c.keys.includes(w);
        return key ? (
          <span
            key={k}
            style={{
              fontFamily: serif,
              fontStyle: "italic",
              fontSize: 150,
              lineHeight: 1.05,
              color: "#fff",
              letterSpacing: -2,
            }}
          >
            {w.replace(/[.,?:]$/, "").toLowerCase()}
          </span>
        ) : (
          <span
            key={k}
            style={{
              fontFamily: sans,
              fontWeight: 600,
              fontSize: 80,
              lineHeight: 1.15,
              color: "#fff",
              letterSpacing: -2,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};
