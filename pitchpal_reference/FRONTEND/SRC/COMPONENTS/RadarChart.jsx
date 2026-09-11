import React from "react";
import { DIMENSIONS } from "../data/config";

// Six-axis radar rendered as raw SVG in the dashboard's forest-green palette.
// `dims` is a { key: value(1-10) } map. Display only.
export default function RadarChart({ dims, size = 300 }) {
  const c = size / 2;
  const maxR = size * 0.34;
  const n = DIMENSIONS.length;
  const angle = (i) => (i / n) * 2 * Math.PI - Math.PI / 2;
  const pt = (r, i) => [c + Math.cos(angle(i)) * r, c + Math.sin(angle(i)) * r];

  const ring = (level) =>
    DIMENSIONS.map((_, i) => pt((level / 5) * maxR, i).join(",")).join(" ");

  const shape = DIMENSIONS
    .map((d, i) => pt(((dims?.[d.key] ?? 0) / 10) * maxR, i).join(","))
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width="100%"
      height="auto"
      role="img"
      aria-label="Six-dimension score radar"
    >
      {/* concentric grid rings */}
      {[1, 2, 3, 4, 5].map((l) => (
        <polygon key={l} points={ring(l)} fill="none" stroke="#ddd8ce" strokeWidth="1" />
      ))}
      {/* spokes */}
      {DIMENSIONS.map((_, i) => {
        const [x, y] = pt(maxR, i);
        return <line key={i} x1={c} y1={c} x2={x} y2={y} stroke="#ddd8ce" strokeWidth="1" />;
      })}
      {/* score polygon */}
      <polygon
        points={shape}
        fill="rgba(59,110,69,0.15)"
        stroke="#3b6e45"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      {/* vertices */}
      {DIMENSIONS.map((d, i) => {
        const [x, y] = pt(((dims?.[d.key] ?? 0) / 10) * maxR, i);
        return <circle key={d.key} cx={x} cy={y} r="3.5" fill="#3b6e45" />;
      })}
      {/* axis labels */}
      {DIMENSIONS.map((d, i) => {
        const [x, y] = pt(maxR + 18, i);
        const anchor = Math.abs(x - c) < 4 ? "middle" : x > c ? "start" : "end";
        return (
          <text
            key={d.key}
            x={x}
            y={y}
            textAnchor={anchor}
            dominantBaseline="middle"
            fontSize="9.5"
            fontWeight="600"
            fill="#8a847c"
            fontFamily="Manrope, sans-serif"
          >
            {d.label.split(" ").map((w, wi) => (
              <tspan key={wi} x={x} dy={wi === 0 ? 0 : 11}>{w}</tspan>
            ))}
          </text>
        );
      })}
    </svg>
  );
}
