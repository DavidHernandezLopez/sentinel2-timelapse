# -*- coding: iso-8859-1 -*-

import ntpath
import imageio
import os
from PIL import Image, ImageDraw, ImageFont
import optparse
import collections
from osgeo import gdal
import numpy as np

def create_gif(file_names, duration, output_dir, font_size=20):
    ordered_file_names = collections.OrderedDict(sorted(file_names.items()))
    images = []
    script_dir_str = ntpath.dirname(os.path.realpath(__file__))
    font = ImageFont.truetype(os.path.join(script_dir_str, 'DejaVuSans-Bold.ttf'), font_size)
    # for file_name in file_names:
    for key, value in ordered_file_names.items():
        if font_size != 0:
            img = Image.open(value).convert('RGBA')
            dinamic_font_size = img.size[0] * 3 / 100
            font = ImageFont.truetype(os.path.join(script_dir_str, 'font/DejaVuSans-Bold.ttf'), int(dinamic_font_size))
            txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt)
            date_srt = ntpath.basename(value).split("_")[0]
            # d.rectangle(((5, 8), (130, 35)), fill="black")
            d.rectangle(((dinamic_font_size*0.3, dinamic_font_size*0.5),
                         (dinamic_font_size*7, dinamic_font_size*1.8)), fill="black")
            d.text((dinamic_font_size*0.6, dinamic_font_size*0.6), date_srt, fill=(255, 255, 0, 255), font=font)
            # d.text((10, 10), date_srt, fill=(255, 255, 0, 255), font=font)
            out = Image.alpha_composite(img, txt)
            out.save(value)
        images.append(imageio.imread(value))
    output_file_name = 'S2_MSIL1C_timelapse_{0}sec.gif'.format(duration)
    imageio.mimsave(os.path.join(output_dir, output_file_name), images, duration=duration)
    for key, value in ordered_file_names.items():
        if os.path.exists(value):
            os.remove(value)
        if os.path.exists('{0}.aux.xml'.format(value)):
            os.remove('{0}.aux.xml'.format(value))


def compute_rgb432(l1c_xml_path, output_file_path, coef_r = 0.05, coef_g = 0.05, coef_b = 0.05, size = 100):
    l1c_10cm_vrt = output_file_path + ".vrt"
    tmp_output_file_path = output_file_path + "_original_size.tif"

    # *****************************************
    # generate l1c vrt (gdal translate)
    # ****************************************
    ds = gdal.Open(l1c_xml_path, gdal.GA_ReadOnly)
    subdatasets = ds.GetSubDatasets()
    ds_10m = gdal.Open(subdatasets[0][0])

    if size > 100:
        size = 100

    gdal.Translate(l1c_10cm_vrt, ds_10m, options='-of VRT -outsize {0}% {0}%'.format(size))
    ds_resized = gdal.Open(l1c_10cm_vrt, gdal.GA_ReadOnly)

    # *****************************************
    # apply coeficient to bands
    # ****************************************
    b4_array = np.array(ds_resized.GetRasterBand(1).ReadAsArray()) * coef_r
    b3_array = np.array(ds_resized.GetRasterBand(2).ReadAsArray()) * coef_g
    b2_array = np.array(ds_resized.GetRasterBand(3).ReadAsArray()) * coef_b

    # *****************************************
    # generate RGB output file (gdal_merge.py)
    # ****************************************
    dst_ds = gdal.GetDriverByName('GTiff').Create(tmp_output_file_path,
                                                  ds_resized.RasterYSize, ds_resized.RasterXSize,
                                                  3, gdal.GDT_Byte)
    geotransform = ds_10m.GetGeoTransform()
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(ds_10m.GetProjection())  # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(b4_array)  # write r-band to the raster
    dst_ds.GetRasterBand(2).WriteArray(b3_array)  # write g-band to the raster
    dst_ds.GetRasterBand(3).WriteArray(b2_array)  # write b-band to the raster
    dst_ds.FlushCache()  # write to disk
    dst_ds = None

    # *********************************************
    # Translate to PNG and resize  (gdal_translate)
    # *********************************************
    ds_gtiff = gdal.Open(tmp_output_file_path, gdal.GA_ReadOnly)
    gdal.Translate(output_file_path, ds_gtiff, options='-of PNG')

    os.remove(l1c_10cm_vrt)
    os.remove(tmp_output_file_path)


if __name__ == "__main__":

    class OptionParser(optparse.OptionParser):
        def check_required(self, opt):
            option = self.get_option(opt)

            # Assumes the option's 'default' is set to None!
            if getattr(self.values, option.dest) is None:
                self.error("%s option not supplied" % option)


    ###########################################################################

    # ==================
    # parse command line
    # ==================
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="input_path", action="store", type="string",
                      help="Input directory containing uncompressed L1C products", default=None)
    parser.add_option("-o", "--output", dest="output_path", action="store", type="string",
                      help="Output directory", default=None)
    parser.add_option("--product_list", dest="product_list", action="store", type="string",
                      help="(Unused) Space separated list of products to process (RGB432 RGB1184 RGB1283 NDVI NDVIb).",
                      default="RGB1184 RGB1283 NDVI NDVIb NDVIb_mosaic")
    parser.add_option("--date_field", dest="date_field", action="store", type="int",
                      help="(Unused) Date field position", default=3)
    parser.add_option("--orbit", dest="orbit", action="store", type="string",
                      help="Filter by relative orbit. ej.: R094", default=None)
    parser.add_option("--tile_id", dest="tile_id", action="store", type="string",
                      help="Filter by tile id. ej.: T30TUL", default=None)
    parser.add_option("--duration", dest="duration", action="store", type="int",
                      help="GIF frame duration in seconds", default=2)
    parser.add_option("--size", dest="size", action="store", type="int",
                      help="Output image size %", default=10)
    parser.add_option("--font_size", dest="font_size", action="store", type="int",
                      help="Text overlay font size. 0 for not overlay", default=20)
    parser.add_option("-r", "--red", dest="red_coef", action="store", type="float",
                      help="Red band coeficient (default 0.05)", default=0.05)
    parser.add_option("-g", "--green", dest="green_coef", action="store", type="float",
                      help="Red band coeficient (default 0.05)", default=0.05)
    parser.add_option("-b", "--blue", dest="blue_coef", action="store", type="float",
                      help="Blue band coeficient (default 0.05)", default=0.05)
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="Only print command")

    (options, args) = parser.parse_args()

    if not options.input_path or not options.output_path:
        parser.print_help()
        exit(0)

    duration = options.duration
    input_dir = options.input_path
    output_dir = options.output_path

    if os.path.exists(input_dir):
        # file_names = []
        file_names = {}
        for file_name in os.listdir(input_dir):
            if os.path.isdir(os.path.join(input_dir,file_name)):
                if file_name.startswith('S2A_MSIL1C_') or file_name.startswith('S2B_MSIL1C_'):
                    if os.path.exists(os.path.join(input_dir, file_name, 'MTD_MSIL1C.xml')):
                        sensing_date = file_name.split('_')[2].split('T')[0]
                        granule_id = file_name.split('_')[5]
                        orbit_id = file_name.split('_')[4]
                        platform_id = file_name.split('_')[0]
                        if orbit_id != options.orbit and options.orbit is not None:
                            continue
                        if granule_id != options.tile_id and options.tile_id is not None:
                            continue
                        rgb432_file = sensing_date + '_' + platform_id + '_' + granule_id + '_' + \
                                      orbit_id + '_RGB432.png'
                        s2_metadata_path = os.path.join(input_dir, file_name, 'MTD_MSIL1C.xml')
                        rgb432_file_path = os.path.join(output_dir, rgb432_file)
                        compute_rgb432(s2_metadata_path, rgb432_file_path, options.red_coef, options.green_coef,
                                       options.blue_coef, options.size)
                        # file_names.append(rgb432_file_path)
                        file_names[sensing_date]=rgb432_file_path
        if len(file_names) > 0:
            create_gif(file_names, duration, output_dir, font_size=options.font_size)
