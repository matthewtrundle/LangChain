FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY .npmrc ./

# Install dependencies
RUN npm ci --only=production

# Copy app files
COPY . .

# Build the app
RUN npm run build

# Start the app
EXPOSE 3000
CMD ["npm", "start"]