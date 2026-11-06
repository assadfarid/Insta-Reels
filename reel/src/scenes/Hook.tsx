import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, ReelProps, display, serif, mono } from "../theme";
import { Grain } from "../Grain";

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const Line: React.FC<{ text: string; start: number; color: string }> = ({ text, start, color }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ overflow: "hidden", height: 300, display: "flex" }}>
      {text.split("").map((ch, i) => (
        <div
          key={i}
          style={{
            fontFamily: display,
            fontSize: 330,
            lineHeight: "300px",
            color,
            whiteSpace: "pre",
            translate: `0px ${interpolate(frame, [start + i * 2, start + i * 2 + 22], [320, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: ease,
            })}px`,
          }}
        >
          {ch}
        </div>
      ))}
    </div>
  );
};

export const Hook: React.FC<ReelProps> = ({ line1, line2, line3, tagline, brand }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: C.cream }}>
      <Interactive.Div
        name="Peach sun"
        style={{
          position: "absolute",
          left: 250,
          top: 560,
          width: 900,
          height: 900,
          borderRadius: 450,
          backgroundColor: C.peach,
          scale: interpolate(frame, [0, 60], [0.2, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: ease,
            output: "perceptual-scale",
          }),
          translate: `0px ${interpolate(frame, [0, 135], [60, -90])}px`,
        }}
      />
      <Interactive.Div
        name="Brand label"
        style={{
          position: "absolute",
          left: 90,
          top: 150,
          fontFamily: mono,
          fontSize: 38,
          letterSpacing: 6,
          color: C.ink,
          opacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        {`( ${brand} )`}
      </Interactive.Div>
      <div style={{ position: "absolute", left: 90, top: 520 }}>
        <Line text={line1} start={8} color={C.ink} />
        <Line text={line2} start={20} color={C.ink} />
        <Line text={line3} start={32} color={C.clay} />
      </div>
      <Interactive.Div
        name="Rule"
        style={{
          position: "absolute",
          left: 90,
          top: 1500,
          height: 4,
          backgroundColor: C.ink,
          width: interpolate(frame, [50, 85], [0, 900], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: ease,
          }),
        }}
      />
      <Interactive.Div
        name="Tagline"
        style={{
          position: "absolute",
          left: 90,
          top: 1540,
          fontFamily: serif,
          fontStyle: "italic",
          fontSize: 96,
          color: C.ink,
          opacity: interpolate(frame, [62, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          translate: `0px ${interpolate(frame, [62, 90], [30, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: ease,
          })}px`,
        }}
      >
        {tagline}
      </Interactive.Div>
      <Grain />
    </AbsoluteFill>
  );
};
