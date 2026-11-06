import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { J, head, monoJ, serifI } from "./theme";

type P = { n: string; name: string; place: string; img: string; stage: string };
const PROJECTS: P[] = [
  {
    n: "01",
    name: "AURELIA",
    place: "BRICKELL, MIAMI",
    img: "jd/jd-premium-p1-1280x1600.webp",
    stage: "donde la ciudad se encuentra con la bahía",
  },
  {
    n: "02",
    name: "MAREA",
    place: "EDGEWATER, MIAMI",
    img: "jd/jd-premium-p11-1280x1600.webp",
    stage: "frente a Biscayne Bay, al amanecer",
  },
  {
    n: "03",
    name: "SOLIS",
    place: "MID-BEACH, MIAMI BEACH",
    img: "jd/jd-premium-p9-1280x720.webp",
    stage: "el océano como vecino",
  },
  {
    n: "04",
    name: "VELA",
    place: "COCONUT GROVE, MIAMI",
    img: "jd/jd-premium-p3-1280x853.webp",
    stage: "privacidad entre el follaje",
  },
];

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const Slide: React.FC<{ p: P; index: number }> = ({ p, index }) => {
  const frame = useCurrentFrame();
  const inn = interpolate(frame, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const text = (start: number) =>
    interpolate(frame, [start, start + 18], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: J.charcoal,
        clipPath: `inset(0 0 0 ${(1 - inn) * 100}%)`,
      }}
    >
      <Img
        src={staticFile(p.img)}
        style={{
          position: "absolute",
          inset: -80,
          width: 1240,
          height: 2080,
          objectFit: "cover",
          filter: "blur(36px) brightness(0.38)",
        }}
      />
      <Interactive.Div
        name="Number"
        style={{
          position: "absolute",
          left: 90,
          top: 110,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 230,
          lineHeight: 1,
          color: "transparent",
          WebkitTextStroke: `4px ${J.terra}`,
          opacity: text(4),
          translate: `${(1 - text(4)) * -60}px 0px`,
        }}
      >
        {p.n}
      </Interactive.Div>
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 410,
          width: 900,
          height: 960,
          overflow: "hidden",
          boxShadow: "0 40px 100px #000000AA",
        }}
      >
        <Img
          src={staticFile(p.img)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            scale: interpolate(frame, [0, 54], [1.18, 1.04]),
          }}
        />
      </div>
      <Interactive.Div
        name="Project name"
        style={{
          position: "absolute",
          left: 90,
          top: 1420,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 112,
          lineHeight: 1,
          color: J.cream,
          opacity: text(10),
          translate: `0px ${(1 - text(10)) * 50}px`,
        }}
      >
        {p.name}
        <span
          style={{
            display: "inline-block",
            width: 24,
            height: 24,
            marginLeft: 8,
            backgroundColor: J.terra,
          }}
        />
      </Interactive.Div>
      <Interactive.Div
        name="Place"
        style={{
          position: "absolute",
          left: 90,
          top: 1566,
          fontFamily: monoJ,
          fontSize: 34,
          letterSpacing: 5,
          color: J.terra,
          opacity: text(18),
        }}
      >
        {p.place}
      </Interactive.Div>
      <Interactive.Div
        name="Line"
        style={{
          position: "absolute",
          left: 90,
          top: 1626,
          width: 900,
          fontFamily: serifI,
          fontStyle: "italic",
          fontSize: 54,
          color: J.cream,
          opacity: text(24),
        }}
      >
        {p.stage}
      </Interactive.Div>
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 1790,
          display: "flex",
          gap: 14,
        }}
      >
        {PROJECTS.map((_, i) => (
          <div
            key={i}
            style={{
              width: i === index ? 120 : 44,
              height: 6,
              backgroundColor: i === index ? J.terra : `${J.cream}55`,
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const JDProjects: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: J.charcoal }}>
    {PROJECTS.map((p, i) => (
      <Sequence
        key={p.name}
        name={p.name}
        from={i * 50}
        durationInFrames={i === PROJECTS.length - 1 ? 50 : 50 + 18}
      >
        <Slide p={p} index={i} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
