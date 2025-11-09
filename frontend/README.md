# Мини-приложение для max

## Запуск

### Предварительные действия:

```bash
# Генерация api через swagger документацию

pnpm run openapi:install
pnpm run openapi:gen
```

### Локальный запуск:

```bash
pnpm install
pnpm run dev
```

### В контейнере

```bash
docker build . -t max/frontend:
docker run -p "3000:80" max/frontend
```

Приложение будет доступно по адрессу http://localhost:3000
