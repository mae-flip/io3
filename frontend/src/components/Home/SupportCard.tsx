import { PixelIcon } from "@/components/Common/PixelIcon"
import { buttonVariants } from "@/components/retroui/Button"
import { cn } from "@/lib/utils"

export function SupportCard() {
  return (
    <section className="flex w-full shrink-0 flex-col justify-between gap-4 border-2 border-black bg-pink p-4 retro-shadow md:w-60 md:p-5">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <PixelIcon name="heart" className="text-white" size={24} />
          <h2
            className="font-head-sm text-lg uppercase tracking-wide text-white"
            style={{ textShadow: "2px 2px 0 #000" }}
          >
            Support io3
          </h2>
        </div>
        <p className="font-sans text-sm leading-snug text-pink-light">
          io3 is independent and community-run. Chip in to help keep the index
          online.
        </p>
      </div>

      <a
        href="https://ko-fi.com/indexofourown"
        target="_blank"
        rel="noopener noreferrer"
        className={cn(
          buttonVariants({ variant: "default", size: "lg" }),
          "w-full font-head-sm uppercase tracking-wide",
        )}
      >
        Donate via Ko-fi
      </a>
    </section>
  )
}
