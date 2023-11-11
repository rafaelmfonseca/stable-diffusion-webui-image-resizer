from PIL import Image,features
import modules.scripts as scripts
from modules import images
from modules.processing import process_images
from modules.processing import fix_seed
from modules.shared import opts
import io
import gradio as gr
import subprocess
import os
import sys
import uuid

script_dir = scripts.basedir()

def borderPixelHandles():
    handles = [ "ConstantExtension", "HalfSampleSymmetric", "WholeSampleSymmetric", "WrapAround" ]
    return handles

def methods():
    methods = [ "NearestNeighbor <GDI+>", "Bilinear <GDI+>", "Bicubic <GDI+>", "HighQualityBilinear <GDI+>", "HighQualityBicubic <GDI+>", "Rectangular", "Bicubic", "Schaum2", "Schaum3", "BSpline2", "BSpline3", "BSpline5", "BSpline7", "BSpline9", "BSpline11", "OMoms3", "OMoms5", "OMoms7", "Triangular", "Welch", "Hann", "Hamming", "Blackman", "Nuttal", "BlackmanNuttal", "BlackmanHarris", "FlatTop", "PowerOfCosine", "Cosine", "Gauss", "Tukey", "Poisson", "BartlettHann", "HanningPoisson", "Bohman", "Cauchy", "Lanczos", "-50% Scanlines", "+50% Scanlines", "+100% Scanlines", "-50% VScanlines", "+50% VScanlines", "+100% VScanlines", "MAME TV 2x", "MAME TV 3x", "MAME RGB 2x", "MAME RGB 3x", "Hawkynt TV 2x", "Hawkynt TV 3x", "Bilinear Plus Original", "Bilinear Plus", "Eagle 2x", "Eagle 3x", "Eagle 3xB", "SuperEagle", "SaI 2x", "Super SaI", "AdvInterp 2x", "AdvInterp 3x", "Scale 2x", "Scale 3x", "EPXB", "EPXC", "EPX3", "Reverse AA", "DES", "DES II", "2xSCL", "Super 2xSCL", "Ultra 2xSCL", "XBR 2x <NoBlend>", "XBR 3x <NoBlend>", "XBR 3x (modified) <NoBlend>", "XBR 4x <NoBlend>", "XBR 2x", "XBR 3x", "XBR 3x (modified)", "XBR 4x", "XBR 5x (legacy)", "XBRz 2x", "XBRz 3x", "XBRz 4x", "XBRz 5x", "HQ 2x", "HQ 2x Bold", "HQ 2x Smart", "HQ 2x3", "HQ 2x3 Bold", "HQ 2x3 Smart", "HQ 2x4", "HQ 2x4 Bold", "HQ 2x4 Smart", "HQ 3x", "HQ 3x Bold", "HQ 3x Smart", "HQ 4x", "HQ 4x Bold", "HQ 4x Smart", "LQ 2x", "LQ 2x Bold", "LQ 2x Smart", "LQ 2x3", "LQ 2x3 Bold", "LQ 2x3 Smart", "LQ 2x4", "LQ 2x4 Bold", "LQ 2x4 Smart", "LQ 3x", "LQ 3x Bold", "LQ 3x Smart", "LQ 4x", "LQ 4x Bold", "LQ 4x Smart", "Red", "Green", "Blue", "Alpha", "Luminance", "ChrominanceU", "ChrominanceV", "u", "v", "Hue", "Hue Colored", "Brightness", "Min", "Max", "ExtractColors", "ExtractDeltas" ];
    return methods

class Script(scripts.Script):
    def title(self):
        return "Image Resizer"
    def show(self, is_img2img):
        return True
    def ui(self, is_img2img):
        with gr.Row():
            method = gr.Dropdown(choices=methods(), label="Method", value="NearestNeighbor <GDI+>", type="value")
        with gr.Row():
            width = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Width")
            height = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Height")
        with gr.Row():
            keep_aspect = gr.Checkbox(label='Keep Aspect', value=False)
        with gr.Row():
            pixel_handling_horizontally = gr.Dropdown(choices=borderPixelHandles(), label="Horizontally", value="None", type="value")
            pixel_handling_vertically = gr.Dropdown(choices=borderPixelHandles(), label="Vertically", value="None", type="value")
        with gr.Row():
            use_thresholds = gr.Checkbox(label='Use Thresholds', value=False)
            thresholds_repeat = gr.Slider(minimum=1, maximum=512, step=1, value=1, label="Repeat")
            use_centered_grid = gr.Checkbox(label='Use Centered Grid', value=False)
            centered_grid_repeat = gr.Slider(minimum=1, maximum=512, step=1, value=1, label="Repeat")
        return [method, width, height, keep_aspect, pixel_handling_horizontally, pixel_handling_vertically, use_thresholds, thresholds_repeat, use_centered_grid, centered_grid_repeat]
    def run(self, p, method, width, height, keep_aspect, pixel_handling_horizontally, pixel_handling_vertically, use_thresholds, thresholds_repeat, use_centered_grid, centered_grid_repeat):
        fix_seed(p)
        
        def resize_image(im):
            temp_image_path = os.path.join(script_dir)
            images.save_image(processed.images[0], temp_image_path, "prompt_matrix", prompt=processed.prompt, seed=processed.seed, grid=True, p=p)
            # temp_image_path = os.path.join(script_dir, f'temp.png')
            # im = im.convert("RGB")
            # im.save(temp_image_path)
            # imageresizer_path = os.path.join(script_dir, "2dimagefilter", "ImageResizer-r129.exe")
            # cmd = f'{imageresizer_path} /load "{temp_image_path}" /resize auto "{method}" /resize w{width} h{height} "HighQualityBilinear <GDI+>" /save output.png'
            # os.system(cmd)
            # os.remove(temp_image_path)
            return im
        # out = process_images(p)
        # for i in range(len(out.images)):
        #     out.images[i] = resize_image(out.images[i])

        processed = process_images(p)

        for i in range(len(processed.images)):
            processed.images[i] = resize_image(processed.images[i])

        