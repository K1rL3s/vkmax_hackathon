export function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen h-full w-full min-w-[320px] max-w-[1440px] mx-auto">
      {children}
    </div>
  )
}
