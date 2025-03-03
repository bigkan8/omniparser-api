# OmniParser API for Render

This repository contains the code for deploying OmniParser as an API service on Render.com.

## Overview

OmniParser is a tool for parsing screenshots into structured elements. It detects UI elements, extracts text, and provides information about the screen structure.

This API service exposes a simple endpoint to parse screenshots and return structured data about the elements on the screen.

## Deployment

This service is designed to be deployed on [Render.com](https://render.com) using the provided `render.yaml` blueprint file.

### Prerequisites

- A Render.com account
- Git installed on your local machine

### Deployment Steps

1. Fork this repository to your GitHub account
2. Create a new Blueprint on Render.com
3. Connect your GitHub repository
4. Configure your environment variables (if needed)
5. Deploy the service

## API Usage

Once deployed, the API will be available at the URL provided by Render.

### Parse Endpoint

`POST /parse`

Request body:
```json
{
  "base64_image": "base64_encoded_image_data"
}
```

Response:
```json
{
  "success": true,
  "som_image_base64": "base64_encoded_annotated_image",
  "elements": [
    {
      "type": "text",
      "content": "Example Text",
      "box": [0.1, 0.2, 0.3, 0.4],
      "confidence": 0.95
    },
    ...
  ],
  "latency": 1.23
}
```

### Health Check

`GET /health`

Response:
```json
{
  "status": "healthy",
  "models": {
    "som_model_path": "weights/icon_detect/model.pt",
    "caption_model_name": "florence2",
    "caption_model_path": "microsoft/Florence-2-base"
  },
  "device": "cpu"
}
```

## Local Development

To run the service locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Download the OmniParser repository: `git clone https://github.com/microsoft/OmniParser.git OmniParser-master`
4. Download model weights: `python download_weights.py`
5. Start the server: `python server.py`

## License

This project references code from [Microsoft OmniParser](https://github.com/microsoft/OmniParser) which is under the MIT License. 