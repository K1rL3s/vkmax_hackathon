import { Container, Panel, Typography } from '@maxhub/max-ui'
import { createFileRoute } from '@tanstack/react-router'
import { Smartphone } from 'lucide-react'
import { Card } from '@/components/card'

export const Route = createFileRoute('/max-error')({
  component: MaxErrorPage,
})

function MaxErrorPage() {
  return (
    <Panel centeredX centeredY className="h-screen! w-full text-red-500">
      <Container className="w-full h-full flex items-center justify-center">
        <Card className="w-fit! h-fit! py-5 px-4">
          <div className="flex space-y-8 w-full flex-col items-center">
            <Smartphone size={100} />
            <Typography.Headline>Откройте в приложении MAX</Typography.Headline>
            <Typography.Body className="text-center">
              Это сервис доступен только через
              <br />
              официальное приложение мессенджера MAX.
            </Typography.Body>
            <a></a>
          </div>
        </Card>
      </Container>
    </Panel>
  )
}
