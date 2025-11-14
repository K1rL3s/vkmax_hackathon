import { Avatar as MaxAvatar } from '@maxhub/max-ui'

type AvatarProps = {
  size:
    | 16
    | 20
    | 24
    | 28
    | 32
    | 36
    | 40
    | 44
    | 48
    | 54
    | 56
    | 64
    | 72
    | 80
    | 88
    | 96
  firstName?: string
  lastName?: string
  image_url?: string | undefined
}

export function Avatar({
  size = 24,
  firstName,
  lastName,
  image_url,
}: AvatarProps) {
  return (
    <MaxAvatar.Container size={size}>
      {image_url ? (
        <MaxAvatar.Image src={image_url} alt={`${firstName} ${lastName}`} />
      ) : (
        <MaxAvatar.Text>
          {firstName?.charAt(0).toUpperCase()}
          {lastName?.charAt(0).toUpperCase()}
        </MaxAvatar.Text>
      )}
    </MaxAvatar.Container>
  )
}
