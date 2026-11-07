import React from "react";
import {
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { J, head, monoJ } from "../jd/theme";
import { LINES } from "./script";

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const shadow = "0 30px 80px #00000066";

const Card: React.FC<{
  style: React.CSSProperties;
  children: React.ReactNode;
}> = ({ style, children }) => (
  <div
    style={{
      position: "absolute",
      borderRadius: 28,
      overflow: "hidden",
      backgroundColor: J.cream,
      boxShadow: shadow,
      border: "6px solid #ffffffDD",
      ...style,
    }}
  >
    {children}
  </div>
);

const Chip: React.FC<{ text: string; style: React.CSSProperties }> = ({
  text,
  style,
}) => (
  <div
    style={{
      position: "absolute",
      padding: "12px 22px",
      backgroundColor: J.terra,
      color: J.cream,
      fontFamily: head,
      fontWeight: 800,
      fontSize: 30,
      letterSpacing: 1,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {text}
  </div>
);

const photo = (name: string) => staticFile(`jd/${name}`);

const Phone: React.FC<{ frame: number }> = ({ frame }) => {
  const y = interpolate(
    frame,
    [0, 40, 80, 120, 160],
    [0, 2500, 5200, 10300, 12900],
    { extrapolateRight: "clamp", easing: Easing.bezier(0.65, 0, 0.35, 1) },
  );
  const W = 330;
  return (
    <div
      style={{
        position: "absolute",
        left: 375,
        top: 120,
        width: W + 20,
        height: 700,
        borderRadius: 60,
        backgroundColor: "#0A0B0D",
        boxShadow: shadow,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 10,
          top: 10,
          width: W,
          height: 680,
          borderRadius: 50,
          overflow: "hidden",
          backgroundColor: J.cream,
        }}
      >
        <Img
          src={photo("site-top.jpg")}
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: W,
            height: "auto",
            translate: `0px ${(-y * W) / 860}px`,
          }}
        />
      </div>
    </div>
  );
};

const CARDS: ((f: number) => React.ReactNode)[] = [
  () => (
    <>
      <Card style={{ left: 90, top: 190, width: 900, height: 430 }}>
        <Img
          src={photo("jd-premium-hero.webp")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "35% 50%",
          }}
        />
      </Card>
      <Chip text="NEW SITE" style={{ left: 120, top: 220 }} />
    </>
  ),
  () => (
    <>
      <Card style={{ left: 190, top: 150, width: 700, height: 560 }}>
        <Img
          src={photo("site-hero.png")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 56%",
          }}
        />
      </Card>
      <Chip text="THE CLIENT'S VOICE" style={{ left: 220, top: 640 }} />
    </>
  ),
  () => (
    <>
      <Card
        style={{ left: 70, top: 190, width: 300, height: 480, rotate: "-6deg" }}
      >
        <Img
          src={photo("site-top.jpg")}
          style={{ width: 300, height: "auto", translate: "0px -520px" }}
        />
      </Card>
      <Card style={{ left: 390, top: 130, width: 300, height: 480, zIndex: 2 }}>
        <Img
          src={photo("site-top.jpg")}
          style={{ width: 300, height: "auto", translate: "0px -1040px" }}
        />
      </Card>
      <Card
        style={{ left: 710, top: 190, width: 300, height: 480, rotate: "6deg" }}
      >
        <Img
          src={photo("jd-premium-p1-1280x1600.webp")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </Card>
      <Chip
        text="MANIFESTO · PROJECTS · FORM"
        style={{ left: 150, top: 700 }}
      />
    </>
  ),
  () => (
    <Card
      style={{
        left: 130,
        top: 190,
        width: 820,
        height: 470,
        backgroundColor: J.charcoal,
      }}
    >
      <div
        style={{
          padding: "36px 44px",
          fontFamily: monoJ,
          fontSize: 34,
          color: J.cream,
          lineHeight: 1.9,
        }}
      >
        <div
          style={{
            fontFamily: head,
            fontWeight: 800,
            fontSize: 50,
            marginBottom: 14,
          }}
        >
          WordPress · Divi
        </div>
        {["Hero", "Projects", "Form"].map((r) => (
          <div key={r}>
            <span style={{ color: J.terra }}>✓</span> {r}{" "}
            <span style={{ opacity: 0.55 }}>· client can edit</span>
          </div>
        ))}
      </div>
    </Card>
  ),
  (f) => <Phone frame={f} />,
  () => (
    <>
      <Card
        style={{
          left: 110,
          top: 230,
          width: 860,
          height: 300,
          backgroundColor: J.charcoal,
          border: `6px solid ${J.terra}`,
        }}
      >
        <div
          style={{
            textAlign: "center",
            paddingTop: 52,
            fontFamily: monoJ,
            fontSize: 34,
            letterSpacing: 6,
            color: J.cream,
          }}
        >
          COMMENT
          <div
            style={{
              marginTop: 18,
              fontFamily: head,
              fontWeight: 800,
              fontSize: 60,
              letterSpacing: 0,
              color: J.terra,
            }}
          >
            WORKFLOW
          </div>
        </div>
      </Card>
    </>
  ),
];

export const Cards: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <>
      {LINES.map((line, i) => {
        const from = line.start - 0.3;
        const to = (LINES[i + 1]?.start ?? line.end - 0.2) - 0.1;
        if (t < from || t > to + 0.4) return null;
        const inn = interpolate(t, [from, from + 0.5], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: ease,
        });
        const out = interpolate(t, [to, to + 0.35], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset: 0,
              opacity: inn * out,
              translate: `0px ${(1 - inn) * 80}px`,
              scale: 0.94 + 0.06 * inn,
            }}
          >
            {CARDS[line.card](Math.max(0, frame - Math.round(from * fps)))}
          </div>
        );
      })}
    </>
  );
};
