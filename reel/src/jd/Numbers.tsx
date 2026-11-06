import React from "react";
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  Sequence,
  useCurrentFrame,
} from "remotion";
import { J, head, monoJ, serifI } from "./theme";
import { Dot, MaskLine } from "./Mask";

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const Quote: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Interactive.Div
        name="Manifest label"
        style={{
          position: "absolute",
          left: 90,
          top: 150,
          fontFamily: monoJ,
          fontSize: 34,
          letterSpacing: 6,
          color: J.charcoal,
        }}
      >
        MANIFIESTO
      </Interactive.Div>
      <div style={{ position: "absolute", left: 90, top: 800 }}>
        <MaskLine start={2} out={64} size={90} color={J.charcoal}>
          NO VENDO
        </MaskLine>
        <div style={{ overflow: "hidden", height: 200 }}>
          <div
            style={{
              fontFamily: serifI,
              fontStyle: "italic",
              fontSize: 200,
              lineHeight: 1,
              color: J.terra,
              translate: `0px ${
                interpolate(frame, [10, 34], [112, 0], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: ease,
                }) +
                interpolate(frame, [64, 82], [0, -112], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })
              }%`,
            }}
          >
            antes
          </div>
        </div>
        <MaskLine start={18} out={64} size={90} color={J.charcoal}>
          DE
        </MaskLine>
        <MaskLine start={24} out={64} size={90} color={J.charcoal}>
          ENTENDER
          <Dot size={90} />
        </MaskLine>
      </div>
    </AbsoluteFill>
  );
};

const Steps: React.FC = () => {
  const frame = useCurrentFrame();
  const count = Math.round(
    interpolate(frame, [4, 50], [0, 18], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    }),
  );
  const steps = [
    ["01", "ENTENDER", "Para qué buscas: vivir, invertir o ambas."],
    ["02", "DEFINIR", "Un rango, no una cifra cerrada."],
    ["03", "ELEGIR", "Solo entonces, los proyectos que encajan."],
  ];
  return (
    <AbsoluteFill style={{ translate: "0px 230px" }}>
      <Interactive.Div
        name="Number"
        style={{
          position: "absolute",
          left: 90,
          top: 330,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 200,
          lineHeight: 1,
          color: J.charcoal,
        }}
      >
        {`$${count}M`}
        <span
          style={{
            display: "inline-block",
            width: 34,
            height: 34,
            marginLeft: 8,
            backgroundColor: J.terra,
          }}
        />
      </Interactive.Div>
      <Interactive.Div
        name="Number caption"
        style={{
          position: "absolute",
          left: 90,
          top: 590,
          width: 880,
          fontFamily: serifI,
          fontStyle: "italic",
          fontSize: 70,
          lineHeight: 1.08,
          color: J.charcoal,
          opacity: interpolate(frame, [30, 50], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        en preconstrucción, en sus primeros cuatro meses en Miami.
      </Interactive.Div>
      <div style={{ position: "absolute", left: 90, top: 870, width: 900 }}>
        {steps.map(([n, t, d], i) => {
          const p = interpolate(
            frame,
            [26 + i * 12, 26 + i * 12 + 18],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: ease,
            },
          );
          return (
            <div
              key={n}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 30,
                borderTop: `3px solid ${J.charcoal}`,
                padding: "28px 0 30px",
                opacity: p,
                translate: `0px ${(1 - p) * 40}px`,
              }}
            >
              <div style={{ fontFamily: monoJ, fontSize: 36, color: J.terra }}>
                {n}
              </div>
              <div>
                <div
                  style={{
                    fontFamily: head,
                    fontWeight: 800,
                    fontSize: 74,
                    color: J.charcoal,
                    lineHeight: 1,
                  }}
                >
                  {t}
                </div>
                <div
                  style={{
                    fontFamily: head,
                    fontWeight: 600,
                    fontSize: 40,
                    color: J.charcoal,
                    marginTop: 10,
                  }}
                >
                  {d}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const JDNumbers: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: J.tan }}>
    <Sequence name="Manifiesto" durationInFrames={84} premountFor={15}>
      <Quote />
    </Sequence>
    <Sequence name="Número y pasos" from={82} premountFor={15}>
      <Steps />
    </Sequence>
  </AbsoluteFill>
);
