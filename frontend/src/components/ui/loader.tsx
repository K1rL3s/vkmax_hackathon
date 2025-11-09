import { LoaderCircle } from 'lucide-react'

export function Loader({ size }: { size: number }) {
  return (
    <div className="h-full w-full grow flex items-center justify-center">
      <LoaderCircle
        size={size}
        className="animate-spin transition-transform duration-300"
      />
    </div>
  )
}
