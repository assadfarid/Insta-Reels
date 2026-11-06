import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { head, J } from "./theme";

// One line of headline text that rises out of a mask.
export const MaskLine: React.FC<{
  children: React.ReactNode;
  start: number;
  size: number;
  color?: string;
  out?: number;
  weight?: number;
}> = ({ children, start, size, color = J.cream, out, weight = 800 }) => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const inY = interpolate(frame, [start, start + 24], [112, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const outY =
    out === undefined
      ? 0
      : interpolate(frame, [out, out + 18], [0, -112], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.7, 0, 0.84, 0),
        });
  return (
    <div style={{ overflow: "hidden", height: size * 1.08 }}>
      <div
        style={{
          fontFamily: head,
          fontWeight: weight,
          fontSize: size,
          lineHeight: 1.08,
          color,
          whiteSpace: "pre",
          translate: `0px ${inY + outY}%`,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Dot: React.FC<{ size: number }> = ({ size }) => (
  <span
    style={{
      display: "inline-block",
      width: size * 0.16,
      height: size * 0.16,
      marginLeft: size * 0.04,
      backgroundColor: J.terra,
    }}
  />
);
