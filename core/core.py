import multiprocessing
import numpy as np
import metalcompute as mc
from PIL import Image

import pipeline_config
from pipeline_config import ANTIALIASING_FILTER as af
from pipeline.renderer import render


def render_sequential(scene_path, width, height):
    images = []
    af_append = [(a, b, c, scene_path, width, height) for a, b, c in af]
    for f in af_append:
        image = render(f)
        images.append(image)

    return images


def render_parallel(scene_path, width, height):
    with multiprocessing.Pool() as pool:
        af_append = [(a, b, c, scene_path, width, height) for a, b, c in af]
        images = pool.map(render, af_append)

    return images


def weighted_averaging(images):
    """
    Do the weighed-averaging process pixel by pixel

    :param images: a list of six float32 numpy arrays of an Image type
    :return: a list of float32 numpy array of an Image type
    """
    output = Image.new('RGB', (pipeline_config.WIDTH, pipeline_config.HEIGHT), 0x000000)
    output_width, output_height = output.size

    for y in range(output_height):
        for x in range(output_width):
            weighted_avg_rgb = images[0][y, x] * af[0][2] + images[1][y, x] * af[1][2] + \
                               images[2][y, x] * af[2][2] + images[3][y, x] * af[3][2] + \
                               images[4][y, x] * af[4][2] + images[5][y, x] * af[5][2]
            output.putpixel((x, y), tuple(weighted_avg_rgb.astype(int)))

    return output


def weighted_averaging_metal(images):
    """
    Do the weighed-averaging process with a Metal kernel

    :param images: a list of six float32 numpy arrays of an Image type
    :return: a list of float32 numpy array of an Image type
    """

    program = """
            #include <metal_stdlib>
            using namespace metal;

            kernel void weighted_avg(
            const device float *a [[ buffer(0) ]],
            const device float *b [[ buffer(1) ]],
            const device float *c [[ buffer(2) ]],
            const device float *d [[ buffer(3) ]],
            const device float *e [[ buffer(4) ]],
            const device float *f [[ buffer(5) ]],
            const device float *w [[ buffer(6) ]],
            device float *g [[ buffer(7) ]],
            uint id [[ thread_position_in_grid ]]) {
                g[id] = a[id] * w[0] + b[id] * w[1] + c[id] * w[2] + d[id] * w[3] + e[id] * w[4] + f[id] * w[5]; 
            }
        """
    dev = mc.Device()
    kernel = dev.kernel(program)
    weighted_avg_fn = kernel.function("weighted_avg")

    count = pipeline_config.WIDTH * pipeline_config.HEIGHT * 3
    a_np = np.ravel(images[0])
    b_np = np.ravel(images[1])
    c_np = np.ravel(images[2])
    d_np = np.ravel(images[3])
    e_np = np.ravel(images[4])
    f_np = np.ravel(images[5])
    w_np = np.array([af[0][2], af[1][2], af[2][2], af[3][2], af[4][2], af[5][2]], dtype='f')
    g_np = np.zeros(count, dtype='f')

    a = dev.buffer(a_np)
    b = dev.buffer(b_np)
    c = dev.buffer(c_np)
    d = dev.buffer(d_np)
    e = dev.buffer(e_np)
    f = dev.buffer(f_np)
    w = dev.buffer(w_np)
    g = dev.buffer(g_np)
    handle = weighted_avg_fn(count, a, b, c, d, e, f, w, g)

    # Will block until the computation has finished
    del handle
    g_result = np.frombuffer(g, dtype='f').astype(np.uint8).reshape(pipeline_config.HEIGHT, pipeline_config.WIDTH, 3)
    output = Image.fromarray(g_result)

    return output


def images_to_numpy(images):
    images_np = []
    for image in images:
        im_np = np.array(image, dtype='f')
        images_np.append(im_np)

    return images_np
