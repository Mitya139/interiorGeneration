from interior_generator import InteriorGenerator
from dotenv import load_dotenv
import os

# parameters for generation
SEED = 444
REF_IMAGE_PATH = "input/bauhaus.jpg"
ROOM_DESCRIPTION = (
    "A lively entertainment room with a large screen "
    "and comfortable seating"
)
OUTPUT_IMAGE_PATH = "output/bauhaus.png"

load_dotenv()

user = os.getenv("PROXY_USER")
passwd = os.getenv("PROXY_PASS")
host = os.getenv("PROXY_HOST")
port = os.getenv("PROXY_PORT")

if host and port:
    if user and passwd:
        proxy = f'http://{user}:{passwd}@{host}:{port}'
    else:
        proxy = f'http://{host}:{port}'

    os.environ['HTTPS_PROXY'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    print(f'Connected to the proxy: {proxy}')

generator = InteriorGenerator(seed=SEED)

img = generator.generate_interior(ref_image_path=REF_IMAGE_PATH,
                                  room_description=ROOM_DESCRIPTION)

img.save(OUTPUT_IMAGE_PATH)
