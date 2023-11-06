
# JPG2000 Image Generator

## Description

This script is a JPG2000 Image Generator that utilizes Google Maps API to fetch satellite imagery based on specific coordinates and parameters. Users can input latitude, longitude, and other criteria to generate a JPG2000 format image with multiple resolution levels.

## Features

- Fetch and stitch satellite imagery from Google Maps.
- Process images into JPG2000 format with multiple resolution levels.
- Interactive UI with Streamlit for parameter adjustments and previews.

## Getting Started

### Prerequisites

- Python 3.6 or later.
- A Google Maps API key with access to the Static Maps API.

### Setting Up the Development Environment

1. Clone the repository to your local machine.
2. Set up a virtual environment to manage dependencies:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On Unix or MacOS:
     ```
     source venv/bin/activate
     ```
4. Install the necessary Python packages using `pip`:
   ```
   pip install -r requirements.txt
   ```

### Obtaining a Google Maps API Key

- Visit [Google Cloud Platform](https://cloud.google.com/maps-platform/).
- Create a new project.
- Enable the Static Maps API for your project.
- Generate an API key from the Credentials page.

## Usage

1. Run the Streamlit application locally with increased message size to handle large images:
   ```
   streamlit run app.py --server.maxMessageSize 2048
   ```
2. Input the required parameters in the Streamlit UI, including your Google Maps API key.
3. Use the interface to preview and download the generated JPG2000 image.

## Configuration

- The script can be customized to adjust the size of the image, the level of detail (scale), and the type of map (satellite, roadmap, terrain).
- Additional filters and enhancements can be applied to the image before generating the final JPG2000 file.


## Important Notes

- The use of Google Maps API is subject to its terms of service and billing. Ensure that you understand the associated costs and limitations before using the API extensively.
- This script is for educational and development purposes. Ensure you have the right to use and distribute the images generated with this tool.
