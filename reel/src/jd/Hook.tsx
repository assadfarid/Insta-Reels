import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { J, head, monoJ, serifI } from "./theme";
import { Dot, MaskLine } from "./Mask";

export const JDHook: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: J.charcoal }}>
      <Img
        name="Skyline"
        src={staticFile("jd/jd-premium-hero.webp")}
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          height: 1920,
          width: "auto",
          translate: `${interpolate(frame, [0, 120], [-1300, -2500])}px 0px`,
          scale: interpolate(frame, [0, 120], [1.02, 1.12]),
        }}
      />
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${J.charcoal}AA 0%, ${J.charcoal}00 28%, ${J.charcoal}00 38%, ${J.charcoal}EE 100%)`,
        }}
      />
      <Interactive.Div
        name="Eyebrow"
        style={{
          position: "absolute",
          left: 90,
          top: 150,
          fontFamily: head,
          fontWeight: 600,
          fontSize: 38,
          letterSpacing: 8,
          color: J.cream,
          opacity: interpolate(frame, [4, 24], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        MIAMI · PRECONSTRUCCIÓN
      </Interactive.Div>
      <div style={{ position: "absolute", left: 90, top: 1060 }}>
        <MaskLine start={6} out={52} size={104}>
          BRICKELL
        </MaskLine>
        <MaskLine start={12} out={52} size={104}>
          NO ESTÁ
        </MaskLine>
        <MaskLine start={18} out={52} size={104}>
          CARO
          <Dot size={104} />
        </MaskLine>
      </div>
      <div style={{ position: "absolute", left: 90, top: 1000 }}>
        <MaskLine start={62} size={104}>
          BRICKELL
        </MaskLine>
        <MaskLine start={68} size={104}>
          ESTÁ
        </MaskLine>
        <MaskLine start={74} size={86} color={J.terra}>
          TEMPRANO
          <Dot size={86} />
        </MaskLine>
      </div>
      <Interactive.Div
        name="Subtitle"
        style={{
          position: "absolute",
          left: 90,
          width: 820,
          top: 1500,
          fontFamily: serifI,
          fontStyle: "italic",
          fontSize: 68,
          lineHeight: 1.1,
          color: J.cream,
          opacity: interpolate(frame, [88, 108], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: `0px ${interpolate(frame, [88, 108], [30, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px`,
        }}
      >
        Preconstrucción de lujo en Miami, con la voz de quien la vive.
      </Interactive.Div>
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 1790,
          fontFamily: monoJ,
          fontSize: 30,
          letterSpacing: 4,
          color: J.cream,
          opacity: 0.8,
        }}
      >
        25.76° N · 80.19° W
      </div>
    </AbsoluteFill>
  );
};
