export const RAIL_WIDTH = 48
export const CORNER_RADIUS = 48

const STROKE_CENTER = RAIL_WIDTH / 2
const ARC_END_X = CORNER_RADIUS + RAIL_WIDTH
const ARC_END_Y = CORNER_RADIUS + STROKE_CENTER
const SVG_WIDTH = RAIL_WIDTH + CORNER_RADIUS
const CORNER_HEIGHT = ARC_END_Y + STROKE_CENTER

export const HEADER_HEIGHT = RAIL_WIDTH

const frameRight = "calc(-1 * var(--site-frame-padding))"
const railRight = "calc(-1 * var(--site-frame-padding) - 12px)"
const railWidth = "calc(var(--site-rail-width) + var(--site-frame-padding))"

export function SiteFrameRail() {
  return (
    <div
      className="pointer-events-none absolute inset-0 z-0 hidden md:block"
      aria-hidden
    >
      {/* Header bar — stops before the corner pocket so the curve stays visible */}
      <div
        className="absolute top-0 z-0 bg-orange"
        style={{
          left: frameRight,
          right: RAIL_WIDTH + 10,
          height: "var(--site-header-height)",
        }}
      />

      {/* Straight vertical rail below the curve */}
      <div
        className="absolute bottom-0 z-0 bg-orange"
        style={{
          width: railWidth,
          top: CORNER_HEIGHT,
          right: railRight,
        }}
      />

      {/* Corner curve — nudged left to align with the vertical rail edge */}
      <svg
        className="absolute top-0 z-10 overflow-visible"
        style={{ right: "var(--site-frame-padding)" }}
        width={SVG_WIDTH}
        height={CORNER_HEIGHT}
        viewBox={`0 0 ${SVG_WIDTH} ${CORNER_HEIGHT}`}
      >
        <path
          d={`M 0 ${STROKE_CENTER} H ${CORNER_RADIUS} A ${CORNER_RADIUS} ${CORNER_RADIUS} 0 0 1 ${ARC_END_X} ${ARC_END_Y} V ${CORNER_HEIGHT}`}
          stroke="#E19057"
          strokeWidth={RAIL_WIDTH}
          fill="none"
          strokeLinejoin="round"
          strokeLinecap="butt"
        />
      </svg>
    </div>
  )
}

export const siteFrameRailWidth = RAIL_WIDTH
