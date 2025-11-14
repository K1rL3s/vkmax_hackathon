import { IconButton } from '@maxhub/max-ui'

type FloatingIconButtonProps = React.HTMLProps<HTMLButtonElement>

export function FloatingIconButton({
  children,
  onClick,
}: FloatingIconButtonProps) {
  return (
    <div className="fixed bottom-7 right-7">
      <IconButton onClick={onClick} size="large">
        {children}
      </IconButton>
    </div>
  )
}
