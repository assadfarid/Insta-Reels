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
import { J, head } from "../jd/theme";
import { DURATION_S, KEYWORD, LINES } from "./script";

export const AVATAR_TOTAL = DURATION_S * 30;

export type AvatarProps = {
  presenterSrc: string | null;
  voiceSrc: string | null;
  musicSrc: string | null;
};
export const avatarDefaults: AvatarProps = {
  presenterSrc: null,
  voiceSrc: null,
  musicSrc: "avatar-bed.mp3",
};

const FinalCta: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const from = LINES[LINES.length - 1].end + 0.3;
  const p = interpolate(t, [from, from + 0.5], [0, 1], {
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
        left: 0,
        width: 1080,
        top: 1360,
        textAlign: "center",
        opacity: p,
        scale: 0.9 + 0.1 * p,
      }}
    >
      <div
        style={{
          fontFamily: head,
          fontWeight: 800,
          fontSize: 100,
          color: "#fff",
          textShadow: "0 6px 30px #00000088",
        }}
      >
        Comment
      </div>
      <div
        style={{
          display: "inline-block",
          marginTop: 24,
          padding: "20px 44px",
          borderRadius: 100,
          backgroundColor: J.cream,
          color: J.charcoal,
          fontFamily: head,
          fontWeight: 800,
          fontSize: 72,
          letterSpacing: 1,
        }}
      >
        {KEYWORD}
      </div>
    </Interactive.Div>
  );
};

export const AvatarReel: React.FC<AvatarProps> = ({
  presenterSrc,
  voiceSrc,
  musicSrc,
}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const fadeEnd = interpolate(t, [DURATION_S - 1.2, DURATION_S], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lastEnd = LINES[LINES.length - 1].end + 0.3;
  const showCaptions = t < lastEnd;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Presenter src={presenterSrc} />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, #00000040 0%, #00000000 30%, #00000000 55%, #00000099 100%)",
        }}
      />
      <Cards />
      {showCaptions ? <Captions /> : null}
      <FinalCta />
      {voiceSrc ? <Audio src={staticFile(voiceSrc)} volume={1} /> : null}
      {musicSrc ? (
        <Audio src={staticFile(musicSrc)} volume={voiceSrc ? 0.32 : 0.9} />
      ) : null}
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: 1 - fadeEnd }} />
    </AbsoluteFill>
  );
};
