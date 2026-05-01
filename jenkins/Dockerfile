FROM jenkins/jenkins:lts
USER root

# Install the Docker CLI and Docker Compose directly from Debian repositories
RUN apt-get update && \
    apt-get install -y docker.io docker-compose && \
    apt-get clean

USER jenkins