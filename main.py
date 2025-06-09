from interior_generator import InteriorGenerator
from dotenv import load_dotenv
import os

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

generator = InteriorGenerator(seed=444)

img = generator.generate_interior(ref_image_path='input/bauhaus.jpg',
                                  room_description='A lively entertainment room with a large screen and comfortable '
                                                   'seating')

img.save("output/bauhaus.png")
