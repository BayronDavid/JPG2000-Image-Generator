
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

## Image Quality Considerations

When generating satellite images, it's important to balance the number of segments, image dimensions, and the necessary image cropping to achieve optimal quality. Based on our testing, here are some considerations to keep in mind:

- **Dimension vs. Cropping**: The amount of cropping required to get a clean image edge does not increase linearly with image dimensions or segment count. Instead, the optimal cropping value depends on various factors, including the number of segments and the specific longitude and latitude.

- **Quality Plateau**: There is a point beyond which increasing the number of segments does not enhance the image quality. This could be due to the maximum resolution provided by the Google Maps API or limitations in the image processing method.

- **Optimal Segments**: For certain longitude values and segment counts, there is an optimal point where the image quality is satisfactory with minimal cropping required.

### Recommended Parameters

Based on empirical results, we recommend the following segment counts for various longitude values to achieve the best image quality without unnecessary processing overhead:

- For a 1 KM image:
  - Use 1 segment with 218px cropping for quick results.
  - Use 4 segments with 218px cropping for higher quality.

- For larger images (2 KM and above):
  - Increment the number of segments judiciously. Doubling the segments doesn't always equate to doubling the quality.
  - Keep an eye on the cropping parameter; it might need adjustment when changing the number of segments.

Please note that these recommendations are based on specific tests and may vary based on the actual coordinates and the current data provided by Google Maps. Always perform a few tests with your target coordinates to determine the optimal settings for your use case.

| Length (KM) | Optimal Segments | Dimensions (px*px) | Cropping (px*px) |
|-------------|------------------|--------------------|------------------|
| 1           | 4                | 1688*1688          | 218              |
| 2           | 16               | 3376*3376          | 218              |
| 3           | 36               | 5064*5064          | 218              |
| 4           | 36               | 6768*6768          | 76               |
| 5           | 64               | 8448*8448          | 112              |
| 10          | 36               | 4200*4200          | 290              |
| 20          | 16               | 4240*4240          | 110              |
| 30          | 36               | 6360*6360          | 110              |

