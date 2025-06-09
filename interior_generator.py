import os

from PIL.ImageFile import ImageFile
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from pathlib import Path

PROMPT_EXTRACT_STYLE = (
    "Highlight the style from the image of this piece of furniture, send the answer in strict "
    "form - just the name of the style and that's it (don't write anything extra besides the "
    "name of the style)"
)

PROMPT_TEMPLATE_GEN = (
    "Generate a photorealistic interior image with a given description and style.\n"
    "Room description: {room_desc}\n"
    "Style: {style}\n"
    "Deliver a single high-resolution photo. "
)


class InteriorGenerator:
    """Helper around two Gemini models (one text → text, one text → image)."""
    extracting_style_model = 'gemini-2.5-flash-preview-05-20'
    image_generating_model = 'gemini-2.0-flash-preview-image-generation'
    temperature = 0

    def __init__(self, seed: int):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY is not found in the .env file or environment variables.")
        self.client = genai.Client(api_key=api_key)
        self.seed = seed

        model_names = {i.name for i in self.client.models.list()}
        if f'models/{self.image_generating_model}' not in model_names:
            raise RuntimeError(f'{self.image_generating_model} not available for your API key/region.')
        if f'models/{self.extracting_style_model}' not in model_names:
            raise RuntimeError(f'{self.extracting_style_model} not available for your API key/region.')

    def extract_style(self, image_path: str | Path) -> str:
        """Return plain style name detected on image_path."""
        img = Image.open(image_path)
        response = self.client.models.generate_content(
            model=self.extracting_style_model,
            config=types.GenerateContentConfig(
                temperature=self.temperature
            ),
            contents=[img, PROMPT_EXTRACT_STYLE],
        )
        return response.text

    def generate_interior(self, ref_image_path: str | Path, room_description: str) -> ImageFile:
        """Generate an interior image in the same style as the reference furniture."""
        style = self.extract_style(image_path=ref_image_path)
        print(f'Extracted style: {style}')
        prompt = PROMPT_TEMPLATE_GEN.format(room_desc=room_description, style=style)
        response = self.client.models.generate_content(
            model=self.image_generating_model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                temperature=self.temperature,
                seed=self.seed
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return Image.open(BytesIO(part.inline_data.data))

        raise RuntimeError('Gemini did not return the image.')
