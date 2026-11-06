import { Composition } from "remotion";
import { Reel, TOTAL } from "./Reel";
import { JDReel, JD_TOTAL } from "./jd/JDReel";
import { FPS, HEIGHT, WIDTH, defaultProps } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="JDLaunch"
        component={JDReel}
        durationInFrames={JD_TOTAL}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Reel"
        component={Reel}
        durationInFrames={TOTAL}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={defaultProps}
      />
    </>
  );
};
