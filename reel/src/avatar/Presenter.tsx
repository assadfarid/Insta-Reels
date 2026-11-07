import React from "react";
import { AbsoluteFill, Interactive, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { J, head, monoJ } from "../jd/theme";

// Drop the generated avatar clip at public/avatar/presenter.mp4 and pass presenterSrc="avatar/presenter.mp4".
export const Presenter: React.FC<{ src: string | null }> = ({ src }) => {
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
  return (
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(180deg, #D9CDBE 0%, #BFB1A0 55%, #8C7F70 100%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: 360,
          backgroundColor: "#7A5C3E",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 290,
          top: 700,
          width: 500,
          height: 640,
          borderRadius: "250px 250px 60px 60px",
          backgroundColor: "#00000022",
          border: "4px dashed #00000044",
        }}
      />
      <Interactive.Div
        name="Placeholder label"
        style={{
          position: "absolute",
          left: 0,
          width: 1080,
          top: 960,
          textAlign: "center",
          fontFamily: head,
          fontWeight: 800,
          fontSize: 44,
          letterSpacing: 4,
          color: J.charcoal,
          opacity: 0.55,
        }}
      >
        PRESENTER CLIP GOES HERE
        <div
          style={{
            fontFamily: monoJ,
            fontWeight: 400,
            fontSize: 30,
            letterSpacing: 2,
            marginTop: 14,
          }}
        >
          public/avatar/presenter.mp4
        </div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
