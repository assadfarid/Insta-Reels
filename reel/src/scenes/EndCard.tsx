import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, ReelProps, display, serif, mono } from "../theme";
import { IgIcon } from "../IgIcon";

export const EndCard: React.FC<ReelProps> = ({ brand, handle }) => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const inn = interpolate(frame, [4, 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const toWhite = interpolate(frame, [40, 60], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ring = interpolate(frame % 45, [0, 45], [0, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <Interactive.Div
        name="Glow"
        style={{
          position: "absolute",
          left: 140,
          top: 560,
          width: 800,
          height: 800,
          borderRadius: 400,
          background: `radial-gradient(circle, ${C.clay}66, ${C.ink}00 65%)`,
          opacity: inn,
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 36 }}>
        <Interactive.Div
          name="Icon"
          style={{
            position: "relative",
            width: 300,
            height: 300,
            opacity: inn,
            scale: interpolate(inn, [0, 1], [0.6, 1], { output: "perceptual-scale" }),
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: 90,
              border: `3px solid ${C.cream}`,
              opacity: 0.5 * (1 - ring),
              scale: 1 + ring * 0.6,
            }}
          />
          <div style={{ position: "absolute", inset: 0, opacity: toWhite }}>
            <IgIcon size={300} stroke="url(#ig-grad)" strokeWidth={6} />
          </div>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - toWhite }}>
            <IgIcon size={300} stroke={C.cream} strokeWidth={6} />
          </div>
        </Interactive.Div>
        <Interactive.Div
          name="Handle"
          style={{ fontFamily: display, fontSize: 120, color: C.cream, letterSpacing: 2, opacity: inn }}
        >
          {handle.toUpperCase()}
        </Interactive.Div>
        <Interactive.Div
          name="Follow line"
          style={{
            fontFamily: serif,
            fontStyle: "italic",
            fontSize: 76,
            color: C.peach,
            opacity: interpolate(frame, [30, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          follow for more
        </Interactive.Div>
      </AbsoluteFill>
      <Interactive.Div
        name="Brand footer"
        style={{
          position: "absolute",
          left: 0,
          width: 1080,
          textAlign: "center",
          top: 1480,
          fontFamily: mono,
          fontSize: 40,
          letterSpacing: 10,
          color: C.cream,
          opacity: 0.8 * interpolate(frame, [40, 65], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        {brand}
      </Interactive.Div>
    </AbsoluteFill>
  );
};
