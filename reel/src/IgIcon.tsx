import React from "react";

export const IgIcon: React.FC<{ size: number; stroke: string; strokeWidth?: number }> = ({
  size,
  stroke,
  strokeWidth = 7,
}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
    <defs>
      <linearGradient id="ig-grad" x1="0" y1="1" x2="1" y2="0">
        <stop offset="0" stopColor="#FEDA77" />
        <stop offset="0.35" stopColor="#F58529" />
        <stop offset="0.6" stopColor="#DD2A7B" />
        <stop offset="1" stopColor="#8134AF" />
      </linearGradient>
    </defs>
    <rect x="9" y="9" width="82" height="82" rx="24" stroke={stroke} strokeWidth={strokeWidth} />
    <circle cx="50" cy="50" r="19" stroke={stroke} strokeWidth={strokeWidth} />
    <circle cx="73" cy="27" r="4.5" fill={stroke} />
  </svg>
);
