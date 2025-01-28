# Use a lightweight Node.js image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Expose the port Vite will run on (default 5173)
EXPOSE 5173

# Command to start the development server
CMD ["npm", "run", "dev", "--", "--host"]
