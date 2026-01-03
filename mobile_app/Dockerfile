# Multi-stage Dockerfile for Flutter Web App

# Stage 1: Build the Flutter web app
FROM ghcr.io/cirruslabs/flutter:stable AS build

# Set working directory
WORKDIR /app

# Disable analytics and accept licenses
ENV PUB_CACHE=/tmp/.pub-cache
ENV FLUTTER_ROOT=/sdks/flutter
RUN flutter config --no-analytics

# Copy pubspec files
COPY pubspec.yaml pubspec.lock ./

# Get dependencies
RUN flutter pub get

# Copy the rest of the app
COPY . .

# Build the web app for production
RUN flutter build web --release --web-renderer canvaskit

# Stage 2: Serve the built app with Nginx
FROM nginx:alpine

# Copy the built web app from the build stage
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy custom nginx configuration template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Expose Railway's dynamic PORT (defaults to 8000)
EXPOSE ${PORT:-8000}

# Create startup script to substitute PORT variable
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'export PORT=${PORT:-8000}' >> /docker-entrypoint.sh && \
    echo 'envsubst "\$PORT" < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Start nginx with PORT substitution
CMD ["/docker-entrypoint.sh"]

