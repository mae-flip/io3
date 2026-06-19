import { SectionShell, SectionTitle } from "@/components/Home/SectionShell"

export function WelcomeSection() {
  return (
    <SectionShell id="about" className="min-w-0 flex-1 bg-white p-4 md:p-5">
      <SectionTitle>Welcome to Our Index</SectionTitle>
      <p className="mt-2 font-sans text-sm leading-snug md:text-base">
        <strong className="font-semibold">
          Tell us about your project. We want to see it.
        </strong>{" "}
        Index of our own is a fully independent indexer for de-listed content.
        Developed in the wake of mass efforts to get advertisement and
        payment-processor unfriendly content deindexed across the internet, io3
        exists as a way to discover art that has been suppressed. Think of us as
        an alternative to itch.io&apos;s front page, specifically designed for
        and by queer and erotic indie game developers.
      </p>
      <p className="mt-3 font-sans text-xs leading-snug text-dark-grey md:text-sm">
        <strong className="font-semibold text-black">Note:</strong> io3 is
        queer-run and celebrates queer art. We index all adult content, but we
        will not feature overtly queerphobic content.
      </p>
    </SectionShell>
  )
}
