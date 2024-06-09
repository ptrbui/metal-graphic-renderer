from PIL import Image
import json
import math
import numpy as np
import multiprocessing
import logging
import pipeline_config

from pipeline.scene_parameter import get_camera_parameter, get_transform_parameter, get_lights_parameter
from pipeline.create_matrix import create_view_matrix, create_projection_matrix, create_model_matrix, \
    create_normal_model_matrix, create_normal_model_scale_matrix, create_rotation_matrix
from pipeline.color import compute_tri_ads

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def render(f):
    logging.info("pid of current process: %s", multiprocessing.current_process().pid)
    pipeline_config.update_scene_path(f[3])
    pipeline_config.update_size(f[4], f[5])
    with open(pipeline_config.SCENE_PATH) as json_file:
        scene = json.load(json_file)

    with open(pipeline_config.GEOMETRY_PATH) as json_file:
        geom = json.load(json_file)

    x_res, y_res, _from, to, near, far, right, left, top, bottom = get_camera_parameter(scene)

    im = Image.new('RGB', (x_res, y_res), 0x000000)
    width, height = im.size

    z_buffer = np.full((height, width), np.inf, dtype=np.float64)

    view_matrix = create_view_matrix(_from, to)

    projection_matrix = create_projection_matrix(near=near, far=far, right=right, left=left, top=top, bottom=bottom)

    lights = get_lights_parameter(scene)

    def f_line(x, y, x_start, y_start, x_end, y_end):
        return (y_start - y_end) * x + (x_end - x_start) * y + x_start * y_end - x_end * y_start

    def draw_triangle(v0, v1, v2, z_buf, model_m, n_model_s, n_model_r, mat, view_mat, mode, dx, dy):
        v0_object_space = np.array([v0['v'][0], v0['v'][1], v0['v'][2], 1])
        v1_object_space = np.array([v1['v'][0], v1['v'][1], v1['v'][2], 1])
        v2_object_space = np.array([v2['v'][0], v2['v'][1], v2['v'][2], 1])

        n0_object_space = np.array([v0['n'][0], v0['n'][1], v0['n'][2]])
        n1_object_space = np.array([v1['n'][0], v1['n'][1], v1['n'][2]])
        n2_object_space = np.array([v2['n'][0], v2['n'][1], v2['n'][2]])
        n0_object_space = n0_object_space / np.linalg.norm(n0_object_space)
        n1_object_space = n1_object_space / np.linalg.norm(n1_object_space)
        n2_object_space = n2_object_space / np.linalg.norm(n2_object_space)

        n0_object_space = np.append(n0_object_space, 1)
        n1_object_space = np.append(n1_object_space, 1)
        n2_object_space = np.append(n2_object_space, 1)

        v0_world_space = np.dot(model_m, v0_object_space.T)
        v1_world_space = np.dot(model_m, v1_object_space.T)
        v2_world_space = np.dot(model_m, v2_object_space.T)

        n0_world_space = np.dot(n_model_s, n0_object_space.T)
        n1_world_space = np.dot(n_model_s, n1_object_space.T)
        n2_world_space = np.dot(n_model_s, n2_object_space.T)
        n0_world_space = n0_world_space[:3]
        n1_world_space = n1_world_space[:3]
        n2_world_space = n2_world_space[:3]
        n0_world_space = n0_world_space / np.linalg.norm(n0_world_space)
        n1_world_space = n1_world_space / np.linalg.norm(n1_world_space)
        n2_world_space = n2_world_space / np.linalg.norm(n2_world_space)
        n0_world_space = np.dot(n_model_r, np.append(n0_world_space, 1).T)
        n1_world_space = np.dot(n_model_r, np.append(n1_world_space, 1).T)
        n2_world_space = np.dot(n_model_r, np.append(n2_world_space, 1).T)

        v0_camera_space = np.dot(view_matrix, v0_world_space.T)
        v1_camera_space = np.dot(view_matrix, v1_world_space.T)
        v2_camera_space = np.dot(view_matrix, v2_world_space.T)
        v0_camera_space = v0_camera_space[:3]
        v1_camera_space = v1_camera_space[:3]
        v2_camera_space = v2_camera_space[:3]

        nv0_world_space = n0_world_space + v0_world_space
        nv1_world_space = n1_world_space + v1_world_space
        nv2_world_space = n2_world_space + v2_world_space
        nv0_world_space[3] = 1
        nv1_world_space[3] = 1
        nv2_world_space[3] = 1

        nv0_camera_space = np.dot(view_matrix, nv0_world_space.T)
        nv1_camera_space = np.dot(view_matrix, nv1_world_space.T)
        nv2_camera_space = np.dot(view_matrix, nv2_world_space.T)
        n0_camera_space = nv0_camera_space[:3] - v0_camera_space
        n1_camera_space = nv1_camera_space[:3] - v1_camera_space
        n2_camera_space = nv2_camera_space[:3] - v2_camera_space

        v0_ndc = np.dot(projection_matrix, np.append(v0_camera_space, 1).T)
        v1_ndc = np.dot(projection_matrix, np.append(v1_camera_space, 1).T)
        v2_ndc = np.dot(projection_matrix, np.append(v2_camera_space, 1).T)

        v0_ndc = v0_ndc[:3] / v0_ndc[3]
        v1_ndc = v1_ndc[:3] / v1_ndc[3]
        v2_ndc = v2_ndc[:3] / v2_ndc[3]
        v0_ndc = v0_ndc + np.array([dx, dy, 0])
        v1_ndc = v1_ndc + np.array([dx, dy, 0])
        v2_ndc = v2_ndc + np.array([dx, dy, 0])

        x0 = (v0_ndc[0] + 1.0) * ((width - 1) / 2)
        y0 = (1.0 - v0_ndc[1]) * ((height - 1) / 2)
        z0 = v0_ndc[2]
        x1 = (v1_ndc[0] + 1.0) * ((width - 1) / 2)
        y1 = (1.0 - v1_ndc[1]) * ((height - 1) / 2)
        z1 = v1_ndc[2]
        x2 = (v2_ndc[0] + 1.0) * ((width - 1) / 2)
        y2 = (1.0 - v2_ndc[1]) * ((height - 1) / 2)
        z2 = v2_ndc[2]

        x_min = math.floor(min(x0, x1, x2))
        x_max = math.ceil(max(x0, x1, x2))
        y_min = math.floor(min(y0, y1, y2))
        y_max = math.ceil(max(y0, y1, y2))

        for y in range(y_min, y_max + 1):
            for x in range(x_min, x_max + 1):
                if 0 <= x < width and 0 <= y < height:
                    d_alpha = f_line(x0, y0, x1, y1, x2, y2)
                    d_beta = f_line(x1, y1, x2, y2, x0, y0)
                    d_gamma = f_line(x2, y2, x0, y0, x1, y1)
                    if d_alpha != 0 and d_beta != 0 and d_gamma != 0:
                        alpha = f_line(x, y, x1, y1, x2, y2) / d_alpha
                        beta = f_line(x, y, x2, y2, x0, y0) / d_beta
                        gamma = f_line(x, y, x0, y0, x1, y1) / d_gamma

                        if alpha >= 0 and beta >= 0 and gamma >= 0:
                            z_at_pixel = alpha * z0 + beta * z1 + gamma * z2

                            if z_at_pixel < z_buf[y, x]:
                                color = (0, 0, 0)
                                if mode == 'phong':
                                    n_interpolated = alpha * n0_camera_space + beta * n1_camera_space + gamma * n2_camera_space
                                    v_shading = alpha * v0_camera_space + beta * v1_camera_space + gamma * v2_camera_space
                                    color = compute_tri_ads(material=mat, normal=n_interpolated, lights=lights,
                                                            view_matrix=view_mat, shading_p=v_shading)
                                if mode == 'gouraud':
                                    color0 = compute_tri_ads(material=mat, normal=n0_camera_space, lights=lights,
                                                             view_matrix=view_mat, shading_p=v0_camera_space)
                                    color1 = compute_tri_ads(material=mat, normal=n1_camera_space, lights=lights,
                                                             view_matrix=view_mat, shading_p=v1_camera_space)
                                    color2 = compute_tri_ads(material=mat, normal=n2_camera_space, lights=lights,
                                                             view_matrix=view_mat, shading_p=v2_camera_space)
                                    color = tuple(int(alpha * a + beta * b + gamma * c) for a, b, c in
                                                  zip(color0, color1, color2))

                                im.putpixel((x, y), color)
                                z_buf[y, x] = z_at_pixel

    delta_x = f[0] / (x_res - 1)
    delta_y = f[1] / (y_res - 1)
    for shape in scene['scene']['shapes']:
        rotation, scale, translation = get_transform_parameter(shape['transforms'])
        model_matrix = create_model_matrix(scale=scale, rotation=rotation, translation=translation)
        create_normal_model_matrix(scale=scale, rotation=rotation)
        normal_model_scale_matrix = create_normal_model_scale_matrix(scale=scale)
        normal_model_rotation_matrix = create_rotation_matrix(rotation=rotation)
        material = shape['material']
        for i in range(len(geom['data'])):
            v0_obj = geom['data'][i]['v0']
            v1_obj = geom['data'][i]['v1']
            v2_obj = geom['data'][i]['v2']
            draw_triangle(v0=v0_obj, v1=v1_obj, v2=v2_obj, z_buf=z_buffer, model_m=model_matrix,
                          n_model_s=normal_model_scale_matrix, n_model_r=normal_model_rotation_matrix, mat=material,
                          view_mat=view_matrix, mode=pipeline_config.SHADING_METHOD, dx=delta_x, dy=delta_y)

    return im