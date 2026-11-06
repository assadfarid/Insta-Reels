import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { IgIcon } from "./IgIcon";
import { mono } from "./theme";

// Persistent "follow me" badge: top-right icon + handle that pulses to the Instagram
// gradient every 2 seconds, plus a vertical credit on the left edge.
export const Overlay: React.FC<{ handle: string; credit: string; hideFrom: number }> = ({
  handle,
  credit,
  hideFrom,
}) => {
  const frame = useCurrentFrame();
  const phase = frame % 60;
  const pulse = interpolate(phase, [0, 6, 18, 28], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const intro = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const outro = interpolate(frame, [hideFrom, hideFrom + 12], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ mixBlendMode: "difference", opacity: intro * outro }}>
      <Interactive.Div
        name="Badge"
        style={{
          position: "absolute",
          right: 80,
          top: 150,
          width: 220,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: 10,
          scale: 1 + pulse * 0.12,
          transformOrigin: "100% 0%",
        }}
      >
        <div style={{ position: "relative", width: 76, height: 76 }}>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - pulse }}>
            <IgIcon size={76} stroke="#fff" />
          </div>
          <div style={{ position: "absolute", inset: 0, opacity: pulse }}>
            <IgIcon size={76} stroke="url(#ig-grad)" />
          </div>
        </div>
        <div style={{ fontFamily: mono, fontSize: 32, color: "#fff", letterSpacing: 1 }}>{handle}</div>
      </Interactive.Div>
      <Interactive.Div
        name="Credit"
        style={{
          position: "absolute",
          left: 44,
          bottom: 520,
          fontFamily: mono,
          fontSize: 30,
          color: "#fff",
          letterSpacing: 4,
          writingMode: "vertical-rl",
          rotate: "180deg",
        }}
      >
        {credit}
      </Interactive.Div>
    </AbsoluteFill>
  );
};
