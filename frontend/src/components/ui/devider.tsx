import clsx from 'clsx'

export function Devider({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        'h-0.5 w-full bg-(--background-surface-tertiary) my-4',
        className,
      )}
    />
  )
}
