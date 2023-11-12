from PIL import Image
import modules.scripts as scripts
from modules import images
from modules.processing import process_images, fix_seed
from modules.ui_components import ToolButton
from modules.shared import opts
from modules import shared
import io
import gradio as gr
import subprocess
import os
import sys
import uuid
import json

script_dir = scripts.basedir()
image_resizer_path = os.path.join(script_dir, "2dimagefilter", "ImageResizer-r129.exe")
save_symbol = '\U0001f4be'  # 💾
paste_symbol = '\u2199\ufe0f'  # ↙

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
            method_index = gr.Dropdown(choices=[x["label"] for x in self.methods], label="Method", value="NearestNeighbor <GDI+>", type="index")
            save_resize_config = ToolButton(value=save_symbol)
            paste_resize_config = ToolButton(value=paste_symbol)

        gr.HTML("<br />")

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem('Target Resolution'):
                        with gr.Row() as resolution_panel:
                            width = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Width", elem_id="image_resizer_width")
                            height = gr.Slider(minimum=1, maximum=512, step=1, value=48, label="Height", elem_id="image_resizer_height")
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem('Border pixel handling'):
                        with gr.Row() as bounds_panel:
                            hbounds_index = gr.Dropdown(choices=[x["label"] for x in self.border_pixel_handles], label="Horizontally", value="ConstantExtension", type="index")
                            vbounds_index = gr.Dropdown(choices=[x["label"] for x in self.border_pixel_handles], label="Vertically", value="ConstantExtension", type="index")

        gr.HTML("<br />")

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem('Advanced'):
                    with gr.Row() as thresholds_panel:
                        use_thresholds = gr.Checkbox(label='Use Thresholds', value=False)
                    with gr.Row() as repeat_panel:
                        repeat = gr.Slider(minimum=1, maximum=10, step=1, value=1, label="Repeat")
                    with gr.Row() as centered_grid_panel:
                        use_centered_grid = gr.Checkbox(label='Use Centered Grid', value=False)
                    with gr.Row() as radius_panel:
                        radius = gr.Slider(minimum=0.5, maximum=100, step=0.1, value=1, label="Radius")

        gr.HTML("<br />")

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem('Extras'):
                    with gr.Row():
                        resize_to_original = gr.Checkbox(label='Resize to 512x512 (Pixelated)', value=False)
        
        def toggles_panels(mi):
            return gr.update(visible=self.methods[mi]["enable_width"]), gr.update(visible=self.methods[mi]["enable_hbounds"]), gr.update(visible=self.methods[mi]["enable_use_thresholds"]), gr.update(visible=self.methods[mi]["enable_repeat"]), gr.update(visible=self.methods[mi]["enable_use_centered_grid"]), gr.update(visible=self.methods[mi]["enable_radius"])

        method_index.change(fn=toggles_panels, inputs=[method_index], outputs=[resolution_panel, bounds_panel, thresholds_panel, repeat_panel, centered_grid_panel, radius_panel])

        def save_configs(mi, w, h, hi, vi, ut, r, ucg, rad, rto):
            config_value = {
                "method_index": mi,
                "width": w,
                "height": h,
                "hbounds_index": hi,
                "vbounds_index": vi,
                "use_thresholds": ut,
                "repeat": r,
                "use_centered_grid": ucg,
                "radius": rad,
                "resize_to_original": rto
            }
            section = ('image-resize', "Image Resize")
            shared.opts.add_option("image_resizer_config", shared.OptionInfo(json.dumps(config_value), "Saved config for image resizer", section=section))
            shared.opts.save(shared.config_filename)

        save_resize_config.click(
            fn=save_configs,
            _js=None,
            inputs=[method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius, resize_to_original],
            outputs=None
        )

        def paste_configs():
            config_value = json.loads(opts.image_resizer_config)
            if config_value is None:
                return
            return gr.update(value=self.methods[config_value["method_index"]]["label"]), gr.update(value=int(config_value["width"])), gr.update(value=int(config_value["height"])), gr.update(value=self.border_pixel_handles[config_value["hbounds_index"]]["label"]), gr.update(value=self.border_pixel_handles[config_value["vbounds_index"]]["label"]), gr.update(value=config_value["use_thresholds"]), gr.update(value=config_value["repeat"]), gr.update(value=config_value["use_centered_grid"]), gr.update(value=config_value["radius"]), gr.update(value=config_value["resize_to_original"])

        paste_resize_config.click(
            fn=paste_configs,
            _js=None,
            inputs=None,
            outputs=[method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius, resize_to_original]
        )

        return [method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius, resize_to_original]

    def run(self, p, method_index, width, height, hbounds_index, vbounds_index, use_thresholds, repeat, use_centered_grid, radius, resize_to_original):
        fix_seed(p)
        
        random_key = uuid.uuid4().hex
        processed = process_images(p)
        temp_image_path = os.path.join(script_dir, "temp", random_key)

        method = self.methods[method_index]
        
        for i in range(len(processed.images)):
            fullfn, txt_fullfn = images.save_image(processed.images[i], temp_image_path, "prompt_matrix", prompt=processed.prompt, seed=processed.seed, grid=True, p=p)

            filename = os.path.join(temp_image_path, f'output_{i}.png')

            paramslist = []

            if method["enable_use_thresholds"]:
                paramslist.append(f'thresholds={use_thresholds and 1 or 0}')
            if method["enable_repeat"] and repeat:
                paramslist.append(f'repeat={repeat}')

            if method["enable_use_centered_grid"]:
                paramslist.append(f'centered={use_centered_grid and 1 or 0}')
            if method["enable_radius"] and radius:
                paramslist.append(f'radius={radius}')

            if method["enable_vbounds"] and vbounds_index is not None and vbounds_index > 0:
                paramslist.append(f'vbounds={self.border_pixel_handles[vbounds_index]["value"]}')
            if method["enable_hbounds"] and hbounds_index is not None and hbounds_index > 0:
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
            if resize_to_original:
                args.extend(["/resize", "w512", "NearestNeighbor <GDI+>"])
            args.extend(["/save", filename])

            print(f"Running: {args}")

            subprocess.run(args, capture_output=True, shell=False)

            new_image = Image.open(filename).convert('RGB')
            images.save_image(new_image, p.outpath_samples, f'resized_{i}.png', processed.all_seeds[i], processed.all_prompts[i], opts.samples_format, info=processed.info, p=p)
            processed.images.insert(0, new_image)

        # os.remove(temp_image_path)
        return processed
