# frontend/Dockerfile
FROM node:18-alpine

# Set the working directory
WORKDIR /frontend

# Copy package.json and yarn.lock to install dependencies
COPY package.json yarn.lock ./

# Install Yarn dependencies, including dev dependencies
RUN yarn install

# Copy the frontend code
COPY . .

# Expose the port that the frontend will run on
EXPOSE 3000

# Command to start the frontend server
CMD ["yarn", "run","dev","--host"]
