import os
import pytest
from dotenv import load_dotenv
import imagehash

from interior_generator import InteriorGenerator


@pytest.fixture(scope="session", autouse=True)
def _env_variables():
    """Get .env + proxy before all tests start."""
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

    if os.getenv("GEMINI_API_KEY") is None:
        pytest.skip("GEMINI_API_KEY not found - skip tests.")


def _generate_twice(tmp_path, seed: int):
    gen = InteriorGenerator(seed=seed)

    desc = "Amazing good room with tv on the wall, two beds and big mirror"
    input_img = "input/farmhouse.jpg"

    style1 = gen.extract_style(input_img)
    style2 = gen.extract_style(input_img)

    out1 = gen.generate_interior(input_img, desc)
    out2 = gen.generate_interior(input_img, desc)
    return out1, out2, style1, style2


def test_repeatability_phash(tmp_path):
    """Check if the selected styles are identical and compare images using pHash"""
    seed = 129212
    img1, img2, style1, style2 = _generate_twice(tmp_path, seed)

    assert style1 == style2, f'Style mismatch: {style1} vs {style2}'

    h1 = imagehash.phash(img1)
    h2 = imagehash.phash(img2)

    diff = h1 - h2
    print(f'pHash difference: {diff}')
    assert diff == 0, f'Images differ, pHash distance = {diff}'
