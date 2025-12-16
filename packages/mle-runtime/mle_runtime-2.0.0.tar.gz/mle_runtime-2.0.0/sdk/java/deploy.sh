#!/bin/bash
# Java SDK Deployment Script
# Builds and publishes to Maven Central

set -e

echo "========================================="
echo "Java SDK - Build & Deploy"
echo "========================================="
echo ""

# Clean and build
echo "Building Java SDK..."
mvn clean install

# Run tests
echo ""
echo "Running tests..."
mvn test

# Package
echo ""
echo "Creating Maven artifacts..."
mvn package

# Show artifacts
echo ""
echo "Artifacts ready:"
ls -lh target/*.jar

echo ""
echo "========================================="
echo "Ready to deploy!"
echo "========================================="
echo ""
echo "To deploy to Maven Central:"
echo "  1. Configure settings.xml with credentials"
echo "  2. Run: mvn deploy"
echo ""
echo "To install locally:"
echo "  mvn install:install-file -Dfile=target/mle-runtime-1.0.0.jar"
echo ""
echo "To test locally:"
echo "  java -cp target/mle-runtime-1.0.0.jar com.mle.runtime.MLEEngine"
echo ""
