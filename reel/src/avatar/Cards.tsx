import React from "react";
import {
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { LINES } from "./script";
import { sans, serif } from "./fonts";

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const photo = (name: string) => staticFile(`jd/${name}`);

// A UI card that blurs/scales in, then floats gently.
const FloatCard: React.FC<{
  f: number;
  delay?: number;
  seed?: number;
  rot?: number;
  style: React.CSSProperties;
  children: React.ReactNode;
}> = ({ f, delay = 0, seed = 0, rot = 0, style, children }) => {
  const p = interpolate(f, [delay, delay + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  return (
    <div
      style={{
        position: "absolute",
        borderRadius: 26,
        overflow: "hidden",
        backgroundColor: "#F6F3EE",
        boxShadow:
          "0 1px 2px #0000002e, 0 10px 24px #00000030, 0 40px 90px #0000004d",
        outline: "1.5px solid #ffffffb3",
        opacity: p,
        filter: `blur(${(1 - p) * 14}px)`,
        scale: 0.9 + 0.1 * p,
        translate: `0px ${(1 - p) * 70 + Math.sin(f / 22 + seed) * 7}px`,
        rotate: `${rot + Math.sin(f / 34 + seed) * 0.8}deg`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// Hand-drawn style annotation: serif italic label plus an arrow that draws itself.
const Note: React.FC<{
  f: number;
  delay: number;
  text: string;
  x: number;
  y: number;
  flip?: boolean;
}> = ({ f, delay, text, x, y, flip }) => {
  const p = interpolate(f, [delay, delay + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const d = interpolate(f, [delay + 6, delay + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        opacity: p,
        translate: `0px ${(1 - p) * 14}px`,
      }}
    >
      <div
        style={{
          fontFamily: serif,
          fontStyle: "italic",
          fontSize: 58,
          color: "#fff",
          textShadow: "0 3px 18px #00000088",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
      <svg
        width="120"
        height="90"
        viewBox="0 0 120 90"
        style={{
          position: "absolute",
          left: flip ? -90 : 20,
          top: 56,
          scale: flip ? "-1 1" : "1 1",
        }}
        fill="none"
      >
        <path
          d="M8 6 C 50 0, 96 26, 100 74"
          stroke="#fff"
          strokeWidth="3.5"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - d}
        />
        <path
          d="M88 62 L100 76 L112 60"
          stroke="#fff"
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity={d > 0.9 ? 1 : 0}
        />
      </svg>
    </div>
  );
};

const Phone: React.FC<{ f: number }> = ({ f }) => {
  const y = interpolate(
    f,
    [8, 48, 88, 128, 168],
    [0, 2500, 5200, 10300, 12900],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.65, 0, 0.35, 1),
    },
  );
  const W = 320;
  return (
    <FloatCard
      f={f}
      seed={1.3}
      rot={-3}
      style={{
        left: 380,
        top: 110,
        width: W + 22,
        height: 640,
        borderRadius: 56,
        backgroundColor: "#0A0B0D",
        outline: "2px solid #3a3e45",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 11,
          top: 11,
          width: W,
          height: 618,
          borderRadius: 46,
          overflow: "hidden",
          backgroundColor: "#F6F3EE",
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
    </FloatCard>
  );
};

const CARDS: ((f: number) => React.ReactNode)[] = [
  (f) => (
    <>
      <FloatCard
        f={f}
        seed={0.4}
        rot={-1.5}
        style={{ left: 90, top: 150, width: 900, height: 440 }}
      >
        <Img
          src={photo("jd-premium-hero.webp")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "35% 50%",
          }}
        />
      </FloatCard>
      <Note f={f} delay={14} text="the result" x={720} y={610} />
    </>
  ),
  (f) => (
    <>
      <FloatCard
        f={f}
        seed={1.1}
        rot={1.2}
        style={{ left: 170, top: 130, width: 740, height: 520 }}
      >
        <Img
          src={photo("site-hero.png")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 56%",
          }}
        />
      </FloatCard>
      <Note f={f} delay={14} text="their voice" x={110} y={640} flip />
    </>
  ),
  (f) => (
    <>
      <FloatCard
        f={f}
        delay={0}
        seed={0.2}
        rot={-6}
        style={{ left: 60, top: 190, width: 300, height: 470 }}
      >
        <Img
          src={photo("site-top.jpg")}
          style={{ width: 300, height: "auto", translate: "0px -520px" }}
        />
      </FloatCard>
      <FloatCard
        f={f}
        delay={6}
        seed={1.7}
        rot={0}
        style={{ left: 390, top: 120, width: 300, height: 470, zIndex: 2 }}
      >
        <Img
          src={photo("site-top.jpg")}
          style={{ width: 300, height: "auto", translate: "0px -1040px" }}
        />
      </FloatCard>
      <FloatCard
        f={f}
        delay={12}
        seed={2.6}
        rot={6}
        style={{ left: 720, top: 190, width: 300, height: 470 }}
      >
        <Img
          src={photo("jd-premium-p1-1280x1600.webp")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </FloatCard>
      <Note f={f} delay={22} text="the sections" x={380} y={640} />
    </>
  ),
  (f) => (
    <>
      <FloatCard
        f={f}
        seed={0.9}
        rot={-1}
        style={{
          left: 120,
          top: 150,
          width: 840,
          height: 460,
          backgroundColor: "#1d1f23",
          outline: "1.5px solid #ffffff22",
        }}
      >
        <div
          style={{ padding: "40px 48px", fontFamily: sans, color: "#F6F3EE" }}
        >
          <div style={{ fontWeight: 700, fontSize: 52, letterSpacing: -1 }}>
            WordPress · Divi
          </div>
          {["Hero", "Projects", "Form"].map((r, i) => (
            <div
              key={r}
              style={{
                marginTop: 22,
                fontSize: 40,
                fontWeight: 500,
                display: "flex",
                alignItems: "center",
                gap: 18,
                opacity: interpolate(f, [16 + i * 8, 28 + i * 8], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              <span style={{ color: "#F4C9B2" }}>✓</span> {r}{" "}
              <span style={{ opacity: 0.5 }}>· editable</span>
            </div>
          ))}
        </div>
      </FloatCard>
      <Note f={f} delay={34} text="client can edit" x={650} y={620} />
    </>
  ),
  (f) => (
    <>
      <Phone f={f} />
      <Note f={f} delay={16} text="on mobile" x={90} y={330} flip />
    </>
  ),
  (f) => (
    <FloatCard
      f={f}
      seed={0.5}
      style={{
        left: 110,
        top: 220,
        width: 860,
        height: 290,
        backgroundColor: "#1d1f23",
        outline: "1.5px solid #F4C9B2aa",
      }}
    >
      <div
        style={{
          textAlign: "center",
          paddingTop: 44,
          fontFamily: sans,
          color: "#F6F3EE",
        }}
      >
        <div
          style={{
            fontWeight: 500,
            fontSize: 36,
            letterSpacing: 6,
            opacity: 0.8,
          }}
        >
          COMMENT
        </div>
        <div
          style={{
            marginTop: 10,
            fontWeight: 700,
            fontSize: 104,
            letterSpacing: -2,
            color: "#F4C9B2",
          }}
        >
          WORKFLOW
        </div>
      </div>
    </FloatCard>
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
        if (t < from || t > to + 0.5) return null;
        const out = interpolate(t, [to, to + 0.4], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset: 0,
              opacity: out,
              filter: `blur(${(1 - out) * 12}px)`,
              scale: 1 + (1 - out) * 0.03,
            }}
          >
            {CARDS[line.card](Math.max(0, frame - Math.round(from * fps)))}
          </div>
        );
      })}
    </>
  );
};
