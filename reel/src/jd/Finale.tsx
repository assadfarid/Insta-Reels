import React from "react";
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { IgIcon } from "../IgIcon";
import { HANDLE, J, head, monoJ } from "./theme";
import { Dot, MaskLine } from "./Mask";

export const JDFinale: React.FC = () => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const fadeIn = (s: number) =>
    interpolate(frame, [s, s + 20], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    });
  const pulse = 1 + 0.04 * Math.sin(frame / 5);
  const toWhite = interpolate(frame, [50, 70], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: J.charcoal }}>
      <Interactive.Div
        name="JD logo"
        style={{
          position: "absolute",
          left: 90,
          top: 190,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 300,
          lineHeight: 1,
          color: J.cream,
          opacity: fadeIn(0),
          scale: interpolate(fadeIn(0), [0, 1], [0.85, 1], {
            output: "perceptual-scale",
          }),
          transformOrigin: "0% 50%",
        }}
      >
        JD
        <span
          style={{
            display: "inline-block",
            width: 48,
            height: 48,
            marginLeft: 10,
            backgroundColor: J.terra,
          }}
        />
      </Interactive.Div>
      <div style={{ position: "absolute", left: 90, top: 610 }}>
        <MaskLine start={14} size={80}>
          TU PRÓXIMA
        </MaskLine>
        <MaskLine start={19} size={80}>
          PROPIEDAD
        </MaskLine>
        <MaskLine start={24} size={80}>
          EMPIEZA
        </MaskLine>
        <MaskLine start={29} size={80}>
          CON UNA
        </MaskLine>
        <MaskLine start={34} size={62} color={J.terra}>
          CONVERSACIÓN
          <Dot size={62} />
        </MaskLine>
      </div>
      <Interactive.Div
        name="CTA button"
        style={{
          position: "absolute",
          left: 90,
          top: 1130,
          maxWidth: 760,
          textAlign: "center",
          padding: "34px 56px",
          backgroundColor: J.terra,
          color: J.cream,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 52,
          letterSpacing: 3,
          opacity: fadeIn(44),
          scale: pulse,
          transformOrigin: "0% 50%",
        }}
      >
        AGENDA UNA LLAMADA
      </Interactive.Div>
      <Interactive.Div
        name="Handle block"
        style={{
          position: "absolute",
          left: 90,
          top: 1430,
          display: "flex",
          alignItems: "center",
          gap: 36,
          opacity: fadeIn(56),
        }}
      >
        <div style={{ position: "relative", width: 150, height: 150 }}>
          <div style={{ position: "absolute", inset: 0, opacity: toWhite }}>
            <IgIcon size={150} stroke="url(#ig-grad)" strokeWidth={6} />
          </div>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - toWhite }}>
            <IgIcon size={150} stroke={J.cream} strokeWidth={6} />
          </div>
        </div>
        <div
          style={{
            fontFamily: head,
            fontWeight: 800,
            fontSize: 50,
            color: J.cream,
          }}
        >
          {HANDLE}
        </div>
      </Interactive.Div>
      <Interactive.Div
        name="Footer"
        style={{
          position: "absolute",
          left: 90,
          top: 1760,
          fontFamily: monoJ,
          fontSize: 32,
          letterSpacing: 5,
          color: J.cream,
          opacity: 0.75 * fadeIn(70),
        }}
      >
        SITIO WEB POR LAUNCH FORGE
      </Interactive.Div>
    </AbsoluteFill>
  );
};
