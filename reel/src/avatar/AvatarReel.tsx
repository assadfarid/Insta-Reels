import React from "react";
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import { Presenter } from "./Presenter";
import { Captions } from "./Captions";
import { Cards } from "./Cards";
import { Grain } from "../Grain";
import { PEACH, sans, serif } from "./fonts";
import { DURATION_S, KEYWORD, LINES } from "./script";

export const AVATAR_TOTAL = DURATION_S * 30;

export type AvatarProps = {
  /** Generated talking-avatar clip in public/, e.g. "avatar/presenter.mp4". Wins over standInSrc. */
  presenterSrc: string | null;
  /** Still photo used as a preview stand-in (no lip-sync), e.g. "avatar/stand-in.jpg". */
  standInSrc: string | null;
  voiceSrc: string | null;
  musicSrc: string | null;
};
export const avatarDefaults: AvatarProps = {
  presenterSrc: null,
  standInSrc: null,
  voiceSrc: null,
  musicSrc: "avatar-bed.mp3",
};

const FinalCta: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const from = LINES[LINES.length - 1].end + 0.3;
  const p = interpolate(t, [from, from + 0.6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  if (p <= 0) return null;
  return (
    <Interactive.Div
      name="Final CTA"
      style={{
        position: "absolute",
        left: 72,
        top: 1420,
        opacity: p,
        translate: `0px ${(1 - p) * 30}px`,
        filter: `blur(${(1 - p) * 10}px)`,
      }}
    >
      <div
        style={{
          fontFamily: sans,
          fontWeight: 600,
          fontSize: 96,
          letterSpacing: -3,
          color: "#fff",
          textShadow: "0 4px 28px #00000066",
        }}
      >
        Comment
      </div>
      <div
        style={{
          display: "inline-block",
          marginTop: 22,
          padding: "16px 48px 20px",
          borderRadius: 100,
          backgroundColor: "#F6F3EE",
          color: "#1d1f23",
          fontFamily: serif,
          fontStyle: "italic",
          fontSize: 104,
          letterSpacing: -1,
          boxShadow: "0 20px 60px #00000055",
        }}
      >
        {KEYWORD.toLowerCase()}
      </div>
      <div
        style={{
          marginTop: 26,
          fontFamily: sans,
          fontWeight: 500,
          fontSize: 44,
          color: PEACH,
          letterSpacing: -0.5,
        }}
      >
        and I'll send it to you
      </div>
    </Interactive.Div>
  );
};

export const AvatarReel: React.FC<AvatarProps> = ({
  presenterSrc,
  standInSrc,
  voiceSrc,
  musicSrc,
}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const fadeEnd = interpolate(t, [DURATION_S - 1.2, DURATION_S], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeStart = interpolate(t, [0, 0.5], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lastEnd = LINES[LINES.length - 1].end + 0.3;
  const showCaptions = t < lastEnd;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Presenter src={presenterSrc} standIn={standInSrc} />
      {/* warm grade + vignette: darker at top for cards, darker at bottom for captions */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, #1a120a66 0%, #1a120a00 30%, #1a120a00 52%, #120c0699 100%), radial-gradient(120% 90% at 50% 45%, #00000000 55%, #00000066 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundColor: "#F4C9B2",
          mixBlendMode: "soft-light",
          opacity: 0.18,
        }}
      />
      <Cards />
      {showCaptions ? <Captions /> : null}
      <FinalCta />
      <Grain opacity={0.07} />
      {voiceSrc ? <Audio src={staticFile(voiceSrc)} volume={1} /> : null}
      {musicSrc ? (
        <Audio src={staticFile(musicSrc)} volume={voiceSrc ? 0.3 : 0.85} />
      ) : null}
      <AbsoluteFill
        style={{
          backgroundColor: "#000",
          opacity: Math.max(1 - fadeEnd, fadeStart),
        }}
      />
    </AbsoluteFill>
  );
};
