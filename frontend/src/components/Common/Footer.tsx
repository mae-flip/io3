export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t py-6 px-6 mt-auto">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 sm:flex-row">
        <div className="text-center sm:text-left">
          <p className="font-medium">io3</p>
          <p className="text-dark-grey text-sm">
            A community index for queer and erotic indie games de-indexed on
            itch.io. Links only — we never host game files.
          </p>
        </div>
        <div className="flex flex-col items-center gap-2 sm:items-end">
          <a
            href="https://ko-fi.com/indexofourown"
            target="_blank"
            rel="noopener noreferrer"
            className="text-black text-sm underline hover:no-underline"
          >
            Support hosting via Ko-fi
          </a>
          <p className="text-dark-grey text-sm">© {currentYear} io3</p>
        </div>
      </div>
    </footer>
  )
}
