# Spotify Playlist Generator

## Installation Instructions

### AWS Server

1. Download all four `.zip` files from the "Lambda Functions" folder.
2. Upload each `.zip` file to its respective Lambda function. Ensure that each Lambda function has the appropriate permissions and layers based on the libraries being used.
3. Create API endpoints in API Gateway for each Lambda function according to the provided API documentation.

### Python Client

1. Download all the remaining files.
2. Install the necessary libraries by running `pip install -r requirements.txt`.
3. Edit the `.env` file to include your own Spotify and OpenAI API keys (default keys are provided).
4. Update the `.ini` file with your own S3 bucket details and required keys.
5. Run `spotify_gui.py` to launch the application.
