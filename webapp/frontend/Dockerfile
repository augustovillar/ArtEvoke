FROM node:20 AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build-time API URL for React
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Create production build
RUN npm run build

#
# Production image: serve the static build, no webpack-dev-server / websockets
#
FROM node:20-alpine AS production

WORKDIR /usr/src/app

# Lightweight static file server
RUN npm install -g serve

# Copy compiled frontend from build stage
COPY --from=build /app/build ./build

EXPOSE 3000

# Serve pre-built static files (production mode, no HMR / dev websocket)
CMD ["serve", "-s", "build", "-l", "3000"]