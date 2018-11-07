# sentinel2-timelapse
Time lapse GIFs from Sentinel-2 imagery

Dependencies
----
Python 2.7
imageio
gdal
PIL

Usage
----

Usage: sentinel2_timelapse.py [options] 

Options:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input=INPUT_PATH
                        Input directory containing uncompressed L1C products
                        (.zip)
  -o OUTPUT_PATH, --output=OUTPUT_PATH
                        Output directory
  --product_list=PRODUCT_LIST
                        (Unused) Space separated list of products to process
                        (RGB432 RGB1184 RGB1283 NDVI NDVIb).
  --date_field=DATE_FIELD
                        (Unused) Date field position
  --orbit=ORBIT         Filter by relative orbit. ej.: R094
  --tile_id=TILE_ID     Filter by tile id. ej.: T30TUL
  --duration=DURATION   GIF frame duration in seconds
  --size=SIZE           Output image size %
  --font_size=FONT_SIZE
                        Text overlay font size. 0 for not overlay
  -r RED_COEF, --red=RED_COEF
                        Red band coeficient
  -g GREEN_COEF, --green=GREEN_COEF
                        Red band coeficient
  -b BLUE_COEF, --blue=BLUE_COEF
                        Blue band coeficient
  -d, --debug           Only print command

