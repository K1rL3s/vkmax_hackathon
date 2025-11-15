FROM docker.io/library/node:25.2.0-alpine3.21 AS build-stage

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml* ./

RUN pnpm install --frozen-lockfile

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
ENV API_URL=${VITE_API_URL}

RUN pnpm run build

FROM docker.io/library/nginx:1.29.3-alpine3.22

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
