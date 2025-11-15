import { Button, Container, Flex, Panel, Typography } from '@maxhub/max-ui'
import { Link } from '@tanstack/react-router'

export function ErrorComponent() {
  return (
    <Panel className="w-full h-screen!">
      <Container className="w-full h-full flex items-center justify-center">
        <Flex direction="column" align="center" gapY={32}>
          <Typography.Headline>Произошлка ошибка!</Typography.Headline>
          <Link to="/">
            <Button
              className="w-full"
              size="large"
              mode="secondary"
              appearance="negative"
            >
              На главную
            </Button>
          </Link>
        </Flex>
      </Container>
    </Panel>
  )
}
