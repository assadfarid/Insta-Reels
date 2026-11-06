import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, ReelProps, display, mono } from "../theme";
import { Grain } from "../Grain";

const W = 380;
const H = 900;
const CX = 540;
const TOP = 1010 - H / 2;

// The object, drawn in layers. `drop(n)` returns how far layer n is still above its resting place.
const Capsule: React.FC<{ drop: (n: number) => number; bob: number; brand: string }> = ({ drop, bob, brand }) => {
  const layer = (n: number): React.CSSProperties => ({
    translate: `0px ${-drop(n)}px`,
    opacity: drop(n) > 1400 ? 0 : 1,
  });
  return (
    <div style={{ position: "absolute", left: CX - W / 2, top: TOP + bob, width: W, height: H }}>
      <div
        style={{
          position: "absolute",
          left: 20,
          top: H + 40,
          width: W - 40,
          height: 50,
          borderRadius: 100,
          backgroundColor: "#00000033",
          filter: "blur(18px)",
          ...layer(0),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: H / 2,
          width: W,
          height: H / 2,
          borderRadius: `0 0 ${W / 2}px ${W / 2}px`,
          backgroundColor: C.peach,
          ...layer(1),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: W,
          height: H / 2,
          borderRadius: `${W / 2}px ${W / 2}px 0 0`,
          backgroundColor: C.ink,
          ...layer(2),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -10,
          top: H / 2 - 22,
          width: W + 20,
          height: 44,
          backgroundColor: C.cream,
          borderTop: `3px solid ${C.ink}`,
          borderBottom: `3px solid ${C.ink}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: mono,
          fontSize: 24,
          letterSpacing: 8,
          color: C.ink,
          ...layer(3),
        }}
      >
        {brand}
      </div>
      <div
        style={{
          position: "absolute",
          left: 44,
          top: 90,
          width: 34,
          height: H - 180,
          borderRadius: 20,
          background: "linear-gradient(#ffffff88, #ffffff00)",
          ...layer(4),
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: H / 2 + 80,
          width: W,
          textAlign: "center",
          fontFamily: display,
          fontSize: 120,
          color: C.ink,
          ...layer(5),
        }}
      >
        01
      </div>
    </div>
  );
};

export const Build: React.FC<ReelProps> = ({ brand }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const bob = Math.sin(frame / 14) * 10;
  const full = () => 0;
  const building = (n: number) =>
    (1 - spring({ frame: frame - (14 + n * 16), fps, config: { damping: 18, stiffness: 120 } })) * 1500;

  const half = (side: "left" | "right", drop: (n: number) => number) => (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: side === "left" ? 0 : 540,
        width: 540,
        height: 1920,
        overflow: "hidden",
        backgroundColor: side === "left" ? C.cream : "#E4DACB",
      }}
    >
      <div style={{ position: "absolute", left: side === "left" ? 0 : -540, top: 0, width: 1080, height: 1920 }}>
        <Capsule drop={drop} bob={bob} brand={brand} />
      </div>
    </div>
  );

  return (
    <AbsoluteFill style={{ backgroundColor: C.cream }}>
      {half("left", full)}
      {half("right", building)}
      <Interactive.Div
        name="Split line"
        style={{
          position: "absolute",
          left: 538,
          top: 0,
          width: 4,
          height: interpolate(frame, [0, 20], [0, 1920], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          backgroundColor: C.clay,
        }}
      />
      <Interactive.Div
        name="Left tag"
        style={{ position: "absolute", left: 70, top: 1600, fontFamily: mono, fontSize: 36, color: C.ink, letterSpacing: 4 }}
      >
        ( finished )
      </Interactive.Div>
      <Interactive.Div
        name="Right tag"
        style={{ position: "absolute", left: 610, top: 1600, fontFamily: mono, fontSize: 36, color: C.ink, letterSpacing: 4 }}
      >
        ( built )
      </Interactive.Div>
      <Grain opacity={0.1} />
    </AbsoluteFill>
  );
};
