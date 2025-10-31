# tests/generate_test_image.py
from PIL import Image
img = Image.new('RGB', (1, 1), color='white')
img.save('tests/test_image.png')