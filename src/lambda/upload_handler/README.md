# Upload Handler Lambda Function

This AWS Lambda function handles image uploads for the ThumbFlow service.

## Features

- Validates image uploads based on size and file extension
- Stores images in S3
- Provides a clean domain-driven design architecture

## Development

### Prerequisites

- Python 3.12 or higher
- Docker (for local testing)

### Setup

1. Create a virtual environment:
   ```
   make venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```
   make install-dev
   ```

### Testing

Run tests with:
```
make test
```

### Building

Build the Lambda package with:
```
make package
```

### Local Testing

Test the Lambda function locally with:
```
make docker-flow
```

## Deployment

The Lambda function can be deployed using the AWS CLI or through CI/CD pipelines.