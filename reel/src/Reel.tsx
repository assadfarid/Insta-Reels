import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { fade } from "@remotion/transitions/fade";
import { ReelProps } from "./theme";
import { Hook } from "./scenes/Hook";
import { Orbit } from "./scenes/Orbit";
import { Build } from "./scenes/Build";
import { EndCard } from "./scenes/EndCard";
import { Overlay } from "./Overlay";

export const T = 15;
export const SCENES = { hook: 135, orbit: 135, build: 135, end: 105 };
export const TOTAL = SCENES.hook + SCENES.orbit + SCENES.build + SCENES.end - 3 * T;

export const Reel: React.FC<ReelProps> = (props) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence name="Hook" durationInFrames={SCENES.hook}>
          <Hook {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={linearTiming({ durationInFrames: T })} />
        <TransitionSeries.Sequence name="Orbit" durationInFrames={SCENES.orbit}>
          <Orbit {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={wipe({ direction: "from-left" })} timing={linearTiming({ durationInFrames: T })} />
        <TransitionSeries.Sequence name="Build" durationInFrames={SCENES.build}>
          <Build {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: T })} />
        <TransitionSeries.Sequence name="End card" durationInFrames={SCENES.end}>
          <EndCard {...props} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Overlay handle={props.handle} credit="made in code" hideFrom={TOTAL - SCENES.end - 8} />
    </AbsoluteFill>
  );
};
