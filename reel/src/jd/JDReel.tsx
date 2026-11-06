import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { fade } from "@remotion/transitions/fade";
import { JDHook } from "./Hook";
import { JDReveal } from "./Reveal";
import { JDProjects } from "./Projects";
import { JDNumbers } from "./Numbers";
import { JDFinale } from "./Finale";
import { Overlay } from "../Overlay";
import { HANDLE } from "./theme";

const T = 15;
const D = { hook: 120, reveal: 180, projects: 200, numbers: 170, finale: 120 };
export const JD_TOTAL =
  D.hook + D.reveal + D.projects + D.numbers + D.finale - 4 * T;

export const JDReel: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <TransitionSeries>
      <TransitionSeries.Sequence name="Hook" durationInFrames={D.hook}>
        <JDHook />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={wipe({ direction: "from-left" })}
        timing={linearTiming({ durationInFrames: T })}
      />
      <TransitionSeries.Sequence name="Reveal" durationInFrames={D.reveal}>
        <JDReveal />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: T })}
      />
      <TransitionSeries.Sequence name="Projects" durationInFrames={D.projects}>
        <JDProjects />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={slide({ direction: "from-bottom" })}
        timing={linearTiming({ durationInFrames: T })}
      />
      <TransitionSeries.Sequence name="Numbers" durationInFrames={D.numbers}>
        <JDNumbers />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: T })}
      />
      <TransitionSeries.Sequence name="Finale" durationInFrames={D.finale}>
        <JDFinale />
      </TransitionSeries.Sequence>
    </TransitionSeries>
    <Overlay
      handle={HANDLE}
      credit="web by launch forge"
      hideFrom={JD_TOTAL - D.finale - 4}
    />
  </AbsoluteFill>
);
