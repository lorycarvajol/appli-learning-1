# Multi-stage build for React frontend

# Development stage
FROM node:18-alpine as development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev"]

# Production build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# ⚠️ Vite **fige** les `VITE_*` dans le bundle au moment du build : elles ne
# sont pas relues à l'exécution. Passer l'URL de l'API par `environment:` dans
# la compose n'aurait donc aucun effet — il faut la fournir ici, en argument de
# construction. Une image construite avec la mauvaise valeur pointe vers
# localhost et l'application semble « ne pas répondre » en production.
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Production serve stage
FROM nginx:alpine as production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
