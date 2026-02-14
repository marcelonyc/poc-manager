FROM node:20-alpine

ARG USER_ID=${USER_ID:-1000}
ARG GROUP_ID=${GROUP_ID:-1000}
RUN addgroup --gid ${GROUP_ID} appuser && \
    adduser -u ${USER_ID} -D -G appuser appuser

WORKDIR /app
RUN chown appuser:appuser /app

USER appuser

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3001

# Start development server
CMD ["npm", "run", "dev"]
