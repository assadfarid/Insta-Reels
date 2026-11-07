import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";

// 1) presenterSrc: the generated talking-avatar clip (public/avatar/presenter.mp4), full frame.
// 2) standInSrc: a still of the presenter with slow "breathing" camera motion (preview only, no lip-sync).
export const Presenter: React.FC<{
  src: string | null;
  standIn: string | null;
}> = ({ src, standIn }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  if (src) {
    return (
      <AbsoluteFill>
        <Video
          src={staticFile(src)}
          objectFit="cover"
          style={{ width: 1080, height: 1920 }}
        />
      </AbsoluteFill>
    );
  }
  if (standIn) {
    const push = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
      easing: Easing.inOut(Easing.quad),
    });
    const breathe = Math.sin(frame / 26) * 0.006;
    return (
      <AbsoluteFill style={{ backgroundColor: "#2b2724" }}>
        <Img
          src={staticFile(standIn)}
          style={{
            position: "absolute",
            left: -120,
            top: -60,
            width: 1320,
            height: 2200,
            objectFit: "cover",
            filter: "blur(40px) brightness(0.75) saturate(1.1)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 330,
            width: 1080,
            height: 1919,
            scale: push + breathe,
            transformOrigin: "50% 28%",
            translate: `${Math.sin(frame / 70) * 6}px 0px`,
            maskImage: "linear-gradient(180deg, transparent 0px, #000 260px)",
            WebkitMaskImage:
              "linear-gradient(180deg, transparent 0px, #000 260px)",
          }}
        >
          <Img
            src={staticFile(standIn)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              filter: "contrast(1.05) saturate(1.05)",
            }}
          />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #D9CDBE 0%, #8C7F70 100%)",
      }}
    />
  );
};
