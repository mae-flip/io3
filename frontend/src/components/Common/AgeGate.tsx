import { useState } from "react"

import { Button } from "@/components/retroui/Button"
import { isAgeVerified, setAgeVerified } from "@/lib/ageVerification"

interface AgeGateProps {
  children: React.ReactNode
}

export function AgeGate({ children }: AgeGateProps) {
  const [verified, setVerified] = useState(isAgeVerified)

  if (!verified) {
    return (
      <div className="fixed inset-0 z-[100] flex min-h-svh items-center justify-center bg-faded-plastic p-6">
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="age-gate-title"
          className="w-full max-w-lg space-y-6 border-2 border-black bg-white p-8 retro-shadow"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <span className="font-head text-2xl text-orange uppercase">
              Index of Our Own
            </span>
            <p className="font-sans text-dark-grey text-sm font-medium tracking-wide uppercase">
              Adults only
            </p>
          </div>

          <div className="space-y-3 text-center">
            <h1
              id="age-gate-title"
              className="font-head-md text-2xl uppercase tracking-wide"
            >
              18+ content warning
            </h1>
            <p className="font-sans text-sm leading-relaxed text-dark-grey">
              io3 indexes queer and erotic indie games, including titles with
              explicit or adult themes. This site may link to pages with mature
              imagery and content.
            </p>
            <p className="font-sans text-sm leading-relaxed text-dark-grey">
              By entering, you confirm that you are at least 18 years old (or the
              age of majority in your jurisdiction).
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Button
              type="button"
              variant="pink"
              className="w-full sm:w-auto"
              onClick={() => {
                setAgeVerified()
                setVerified(true)
              }}
            >
              I am 18 or older — enter
            </Button>
            <Button
              type="button"
              variant="default"
              className="w-full sm:w-auto"
              onClick={() => {
                window.location.href = "https://itch.io"
              }}
            >
              Leave
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return children
}
