from PIL import Image,features
import modules.scripts as scripts
from modules import images
from modules.processing import process_images, fix_seed
from modules.shared import opts
import io
import gradio as gr
import subprocess
import os
import sys
import uuid

script_dir = scripts.basedir()
image_resizer_path = os.path.join(script_dir, "2dimagefilter", "ImageResizer-r129.exe")

# (width, height, horizontal, vertical)
def interpolators_type_methods():
    handles = [ "NearestNeighbor <GDI+>", "Bilinear <GDI+>", "Bicubic <GDI+>", "HighQualityBilinear <GDI+>", "HighQualityBicubic <GDI+>" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": True,
            "enable_height": True,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": False,
            "enable_repeat": False,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

# (width, height, horizontal, vertical, use_centered_grid)
def kernels_type_methods():
    handles = [ "Rectangular", "Bicubic", "Schaum2", "Schaum3", "BSpline2", "BSpline3", "BSpline5", "BSpline7", "BSpline9", "BSpline11", "OMoms3", "OMoms5", "OMoms7" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": True,
            "enable_height": True,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": False,
            "enable_repeat": False,
            "enable_use_centered_grid": True,
            "enable_radius": False
        }
        for item in handles
    ]

# (width, height, horizontal, vertical, use_centered_grid, radius)
def windowing_functions_type_methods():
    handles = [ "Triangular", "Welch", "Hann", "Hamming", "Blackman", "Nuttal", "BlackmanNuttal", "BlackmanHarris", "FlatTop", "PowerOfCosine", "Cosine", "Gauss", "Tukey", "Poisson", "BartlettHann", "HanningPoisson", "Bohman", "Cauchy", "Lanczos" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": True,
            "enable_height": True,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": False,
            "enable_repeat": False,
            "enable_use_centered_grid": True,
            "enable_radius": True
        }
        for item in handles
    ]

# (horizontal, vertical, use_thresholds, repeat)
# /resize auto
def pixel_scaler_type_methods():
    handles = [ "-50% Scanlines", "+50% Scanlines", "+100% Scanlines", "-50% VScanlines", "+50% VScanlines", "+100% VScanlines", "MAME TV 2x", "MAME TV 3x", "MAME RGB 2x", "MAME RGB 3x", "Hawkynt TV 2x", "Hawkynt TV 3x", "Bilinear Plus Original", "Bilinear Plus", "Eagle 2x", "Eagle 3x", "Eagle 3xB", "SuperEagle", "SaI 2x", "Super SaI", "AdvInterp 2x", "AdvInterp 3x", "Scale 2x", "Scale 3x", "EPXB", "EPXC", "EPX3", "Reverse AA", "DES", "DES II", "2xSCL", "Super 2xSCL", "Ultra 2xSCL" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": False,
            "enable_height": False,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": True,
            "enable_repeat": True,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

# (horizontal, vertical, use_thresholds, repeat)
# /resize auto
def xbr_scaler_type_methods():
    handles = [ "XBR 2x <NoBlend>", "XBR 3x <NoBlend>", "XBR 3x (modified) <NoBlend>", "XBR 4x <NoBlend>", "XBR 2x", "XBR 3x", "XBR 3x (modified)", "XBR 4x", "XBR 5x (legacy)" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": False,
            "enable_height": False,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": True,
            "enable_repeat": True,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

# (horizontal, vertical, use_thresholds, repeat)
# /resize auto
def xbrz_scaler_type_methods():
    handles = [ "XBRz 2x", "XBRz 3x", "XBRz 4x", "XBRz 5x" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": False,
            "enable_height": False,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": True,
            "enable_repeat": True,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

# (horizontal, vertical, use_thresholds, repeat)
# /resize auto
def nq_scaler_type_methods():
    handles = [ "HQ 2x", "HQ 2x Bold", "HQ 2x Smart", "HQ 2x3", "HQ 2x3 Bold", "HQ 2x3 Smart", "HQ 2x4", "HQ 2x4 Bold", "HQ 2x4 Smart", "HQ 3x", "HQ 3x Bold", "HQ 3x Smart", "HQ 4x", "HQ 4x Bold", "HQ 4x Smart", "LQ 2x", "LQ 2x Bold", "LQ 2x Smart", "LQ 2x3", "LQ 2x3 Bold", "LQ 2x3 Smart", "LQ 2x4", "LQ 2x4 Bold", "LQ 2x4 Smart", "LQ 3x", "LQ 3x Bold", "LQ 3x Smart", "LQ 4x", "LQ 4x Bold", "LQ 4x Smart" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": False,
            "enable_height": False,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": True,
            "enable_repeat": True,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

# (horizontal, vertical)
# /resize auto
def planes_type_methods():
    handles = [ "Red", "Green", "Blue", "Alpha", "Luminance", "ChrominanceU", "ChrominanceV", "u", "v", "Hue", "Hue Colored", "Brightness", "Min", "Max", "ExtractColors", "ExtractDeltas" ]
    return [
        {
            "label": item,
            "value": item,
            "enable_width": False,
            "enable_height": False,
            "enable_hbounds": True,
            "enable_vbounds": True,
            "enable_use_thresholds": False,
            "enable_repeat": False,
            "enable_use_centered_grid": False,
            "enable_radius": False
        }
        for item in handles
    ]

class Script(scripts.Script):
    def __init__(self):
        self.border_pixel_handles = [
            { "label": "ConstantExtension", "value": "const" },
            { "label": "HalfSampleSymmetric", "value": "half" },
            { "label": "WholeSampleSymmetric", "value": "whole" },
            { "label": "WrapAround", "value": "wrap" }
        ]

        self.methods = []
        self.methods.extend(interpolators_type_methods())
        self.methods.extend(kernels_type_methods())
        self.methods.extend(windowing_functions_type_methods())
        self.methods.extend(pixel_scaler_type_methods())
        self.methods.extend(xbr_scaler_type_methods())
        self.methods.extend(xbrz_scaler_type_methods())
        self.methods.extend(nq_scaler_type_methods())
        self.methods.extend(planes_type_methods())

    def title(self):
        return "Image Resizer"
        
    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        gr.HTML("<br />")
        
        with gr.Row():
            method_index = gr.Dropdown(choices=[x["label"] for x in self.methods], label="Method", value=0, type="index")

        gr.HTML("<br />")

        with gr.Row().style():
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem('Target Resolution'):
                        width = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Width")
                        height = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Height")
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem('Border pixel handling'):
                        hbounds_index = gr.Dropdown(choices=[x["label"] for x in self.border_pixel_handles], label="Horizontally", value=0, type="index")
                        vbounds_index = gr.Dropdown(choices=[x["label"] for x in self.border_pixel_handles], label="Vertically", value=0, type="index")

        gr.HTML("<br />")

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem('Advanced'):
                    with gr.Row():
                        use_thresholds = gr.Checkbox(label='Use Thresholds', value=False)
                    with gr.Row():
                        repeat = gr.Slider(minimum=1, maximum=512, step=1, value=1, label="Repeat")
                    with gr.Row():
                        use_centered_grid = gr.Checkbox(label='Use Centered Grid', value=False)
                    with gr.Row():
                        radius = gr.Slider(minimum=0.5, maximum=100, step=0.1, value=1, label="Radius")
        
        return [method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius]

    def run(self, p, method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius):
        fix_seed(p)
        
        random_key = uuid.uuid4().hex
        processed = process_images(p)
        temp_image_path = os.path.join(script_dir, "temp", random_key)

        method = self.methods[method_index]
        
        for i in range(len(processed.images)):
            fullfn, txt_fullfn = images.save_image(processed.images[i], temp_image_path, "prompt_matrix", prompt=processed.prompt, seed=processed.seed, grid=True, p=p)

            filename = os.path.join(temp_image_path, f'output_{i}.png')

            paramslist = []

            if method["enable_use_thresholds"] and use_thresholds:
                paramslist.append(f'thresholds=1')
            if method["enable_repeat"] and repeat:
                paramslist.append(f'repeat={repeat}')

            if method["enable_use_centered_grid"] and use_centered_grid:
                paramslist.append(f'centered=1')
            if method["enable_radius"] and radius:
                paramslist.append(f'radius={radius}')

            if method["enable_vbounds"] and vbounds_index > 0:
                paramslist.append(f'vbounds={self.border_pixel_handles[vbounds_index]["value"]}')
            if method["enable_hbounds"] and hbounds_index > 0:
                paramslist.append(f'hbounds={self.border_pixel_handles[hbounds_index]["value"]}')

            params = ""
            if len(paramslist) > 0:
                params = "(" + ",".join(paramslist) + ")"

            size_param = "auto"
            if method["enable_width"] and method["enable_height"]:
                size_param = f'{width}x{height}'

            args = []
            args.append(image_resizer_path)
            args.extend(["/load", fullfn])
            args.extend(["/resize", size_param, f'{method["value"]}{params}'])
            args.extend(["/save", filename])

            print(f"Running: {args}")

            subprocess.run(args, capture_output=True, shell=False)

            new_image = Image.open(filename).convert('RGB')
            images.save_image(new_image, p.outpath_samples, f'resized_{i}.png', processed.all_seeds[i], processed.all_prompts[i], opts.samples_format, info=processed.info, p=p)
            processed.images.insert(0, new_image)

        # os.remove(temp_image_path)
        return processed
