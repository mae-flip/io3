import type { OsPlatform } from "@/client"
import type { IconType } from "react-icons"
import {
  FaAndroid,
  FaApple,
  FaLaptop,
  FaLinux,
  FaWindows,
} from "react-icons/fa6"

import { cn } from "@/lib/utils"

export type IndexPlatformFilter = "web" | "windows" | "linux" | "apple"

export const INDEX_PLATFORM_FILTERS: {
  platform: IndexPlatformFilter
  label: string
}[] = [
  { platform: "web", label: "Web" },
  { platform: "windows", label: "Windows" },
  { platform: "linux", label: "Linux" },
  { platform: "apple", label: "Apple" },
]

const PLATFORM_ORDER: OsPlatform[] = [
  "web",
  "windows",
  "linux",
  "apple",
  "android",
]

const PLATFORM_ICONS: Record<OsPlatform, IconType> = {
  android: FaAndroid,
  windows: FaWindows,
  apple: FaApple,
  linux: FaLinux,
  web: FaLaptop,
}

export function orderPlatforms<T extends { platform: OsPlatform }>(
  platforms: T[],
): T[] {
  const order = new Map(PLATFORM_ORDER.map((platform, index) => [platform, index]))
  return [...platforms].sort(
    (left, right) =>
      (order.get(left.platform) ?? 99) - (order.get(right.platform) ?? 99),
  )
}

export function platformChipClassName(size: "sm" | "xs" = "sm") {
  const box = size === "xs" ? "h-5 w-5" : "h-6 w-6"
  const icon = size === "xs" ? "h-3 w-3" : "h-3.5 w-3.5"
  return {
    box: cn(
      "inline-flex items-center justify-center rounded-sm text-dark-grey",
      box,
    ),
    icon,
  }
}

export function platformIcon(platform: OsPlatform): IconType {
  return PLATFORM_ICONS[platform]
}
