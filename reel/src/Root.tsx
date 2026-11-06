import { Composition } from "remotion";
import { Reel, TOTAL } from "./Reel";
import { FPS, HEIGHT, WIDTH, defaultProps } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Reel"
      component={Reel}
      durationInFrames={TOTAL}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      defaultProps={defaultProps}
    />
  );
};
