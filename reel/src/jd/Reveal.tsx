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
import { J, head, serifI } from "./theme";
import { Dot, MaskLine } from "./Mask";

const SCREEN_W = 520;
const SCALE = SCREEN_W / 860; // site capture is 860px wide (2x of a 430px phone)

const Chip: React.FC<{
  text: string;
  start: number;
  style: React.CSSProperties;
}> = ({ text, start, style }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [start, start + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <div
      style={{
        position: "absolute",
        padding: "22px 34px",
        backgroundColor: J.terra,
        color: J.cream,
        fontFamily: head,
        fontWeight: 800,
        fontSize: 40,
        letterSpacing: 2,
        opacity: p,
        translate: `0px ${(1 - p) * 40}px`,
        boxShadow: "0 20px 50px #00000066",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

export const JDReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const phoneIn = interpolate(frame, [4, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const scroll = interpolate(
    frame,
    [0, 28, 58, 74, 102, 116, 146, 160, 178],
    [0, 0, 2500, 2500, 5200, 5200, 10300, 10300, 12900],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.65, 0, 0.35, 1),
    },
  );
  return (
    <AbsoluteFill style={{ backgroundColor: J.charcoal }}>
      <div style={{ position: "absolute", left: 90, top: 330 }}>
        <MaskLine start={4} size={140}>
          NUEVO
        </MaskLine>
        <MaskLine start={10} size={140}>
          SITIO
          <Dot size={140} />
        </MaskLine>
      </div>
      <Interactive.Div
        name="Phone"
        style={{
          position: "absolute",
          left: 540 - (SCREEN_W + 28) / 2,
          top: 790,
          width: SCREEN_W + 28,
          height: 1030,
          borderRadius: 84,
          backgroundColor: "#0A0B0D",
          boxShadow: `0 60px 120px #000000AA, 0 0 0 3px #3A3E45`,
          opacity: phoneIn,
          translate: `0px ${(1 - phoneIn) * 300}px`,
          rotate: `${interpolate(frame, [0, 180], [-4, 3])}deg`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 14,
            top: 14,
            width: SCREEN_W,
            height: 1002,
            borderRadius: 70,
            overflow: "hidden",
            backgroundColor: J.cream,
          }}
        >
          <Img
            name="Site capture"
            src={staticFile("jd/site-top.jpg")}
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              width: SCREEN_W,
              height: "auto",
              translate: `0px ${-scroll * SCALE}px`,
            }}
          />
        </div>
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: 30,
            width: 150,
            height: 40,
            marginLeft: -75,
            borderRadius: 20,
            backgroundColor: "#0A0B0D",
          }}
        />
      </Interactive.Div>
      <Chip text="ES · EN" start={34} style={{ left: 70, top: 900 }} />
      <Chip text="4 PROYECTOS" start={78} style={{ right: 60, top: 1280 }} />
      <Chip
        text="CONSULTA PRIVADA"
        start={120}
        style={{ left: 80, top: 1600 }}
      />
      <Interactive.Div
        name="Caption"
        style={{
          position: "absolute",
          left: 90,
          top: 665,
          width: 900,
          fontFamily: serifI,
          fontStyle: "italic",
          fontSize: 60,
          color: J.cream,
          opacity: interpolate(frame, [30, 50], [0, 0.9], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        la nueva casa digital de Jorge Dan
      </Interactive.Div>
    </AbsoluteFill>
  );
};
