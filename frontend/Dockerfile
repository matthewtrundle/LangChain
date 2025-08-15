FROM node:18-alpine

WORKDIR /app

# Install Python and build dependencies for native modules
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./
COPY .npmrc ./

# Install dependencies - ignore optional dependencies and scripts
RUN npm ci --only=production --omit=optional --ignore-scripts || \
    npm ci --only=production --no-optional || \
    npm install --production --no-optional

# Copy app files
COPY . .

# Build the app
RUN npm run build

# Start the app
EXPOSE 3000
CMD ["npm", "start"]