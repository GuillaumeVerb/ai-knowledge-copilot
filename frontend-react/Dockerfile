FROM node:20-alpine

WORKDIR /app

COPY frontend-react/package*.json ./
RUN npm ci

COPY frontend-react ./

RUN npm run build

EXPOSE 4173

CMD ["sh", "-c", "npm run start"]
