import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, ReelProps, display, serif, mono } from "../theme";

const COUNT = 54;
const R = 560;
const golden = Math.PI * (3 - Math.sqrt(5));

const Tile: React.FC<{ i: number; label: string; appear: number }> = ({ i, label, appear }) => {
  const y = 1 - (i / (COUNT - 1)) * 2; // -1..1
  const lat = Math.asin(y) * (180 / Math.PI);
  const lon = ((i * golden) % (Math.PI * 2)) * (180 / Math.PI);
  const kind = i % 4;
  const bg = [C.cream, C.peach, C.ink, C.cream][i % 4 === 2 ? 2 : i % 3];
  const fg = bg === C.ink ? C.cream : C.ink;
  return (
    <div
      style={{
        position: "absolute",
        left: -80,
        top: -105,
        width: 160,
        height: 210,
        backgroundColor: bg,
        border: bg === C.ink ? `2px solid ${C.cream}55` : "none",
        backfaceVisibility: "hidden",
        transform: `rotateY(${lon}deg) rotateX(${-lat}deg) translateZ(${R * appear}px)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: fg,
        overflow: "hidden",
      }}
    >
      {kind === 0 && <div style={{ width: 80, height: 80, borderRadius: 40, border: `6px solid ${fg}` }} />}
      {kind === 1 && <div style={{ fontFamily: display, fontSize: 64 }}>{label}</div>}
      {kind === 2 && (
        <div style={{ width: 90, height: 45, borderRadius: "90px 90px 0 0", backgroundColor: C.peach }} />
      )}
      {kind === 3 && <div style={{ fontFamily: serif, fontStyle: "italic", fontSize: 54 }}>{i + 1}</div>}
    </div>
  );
};

export const Orbit: React.FC<ReelProps> = ({ brand, tiles }) => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [0, 45], [0.15, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const zoom = interpolate(frame, [0, 135], [0.78, 1.12]);
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <Interactive.Div
        name="Sphere"
        style={{
          position: "absolute",
          left: 540,
          top: 900,
          width: 0,
          height: 0,
          perspective: 1700,
          scale: zoom,
        }}
      >
        <div
          style={{
            transformStyle: "preserve-3d",
            transform: `rotateX(-14deg) rotateY(${frame * 1.4}deg)`,
          }}
        >
          {new Array(COUNT).fill(true).map((_, i) => (
            <Tile key={i} i={i} label={tiles} appear={appear} />
          ))}
        </div>
      </Interactive.Div>
      <Interactive.Div
        name="Orbit caption"
        style={{
          position: "absolute",
          left: 90,
          top: 1500,
          width: 900,
          color: C.cream,
          fontFamily: serif,
          fontStyle: "italic",
          fontSize: 110,
          lineHeight: 1.05,
          opacity: interpolate(frame, [30, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          translate: `0px ${interpolate(frame, [30, 60], [40, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px`,
        }}
      >
        everything, in orbit
      </Interactive.Div>
      <Interactive.Div
        name="Orbit label"
        style={{
          position: "absolute",
          left: 90,
          top: 150,
          fontFamily: mono,
          fontSize: 38,
          letterSpacing: 6,
          color: C.cream,
        }}
      >
        {`( ${brand} / 02 )`}
      </Interactive.Div>
    </AbsoluteFill>
  );
};
