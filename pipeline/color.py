import numpy as np


def compute_tri_ads(material, normal, lights, view_matrix, shading_p):
    ambient_color = np.array([0, 0, 0], dtype='float64')
    diffuse_color = np.array([0, 0, 0], dtype='float64')
    specular_color = np.array([0, 0, 0], dtype='float64')

    for light in lights:
        le = np.array(light['color']) * light['intensity']
        if light['type'] == 'ambient':
            ambient_color += material['Ka'] * le

        if light['type'] == 'directional':
            n = normalize(normal)
            light_from_world_space = np.array([light['from'][0], light['from'][1], light['from'][2]])
            light_to_world_space = np.array([light['to'][0], light['to'][1], light['to'][2]])
            light_from_cam_space = np.dot(view_matrix, np.append(light_from_world_space, 1).T)
            light_to_cam_space = np.dot(view_matrix, np.append(light_to_world_space, 1).T)
            light_from_cam_space = light_from_cam_space[:3]
            light_to_cam_space = light_to_cam_space[:3]
            l = normalize(light_from_cam_space - light_to_cam_space)
            diffuse_color += material['Kd'] * le * material['Cs'] * max(np.dot(n, l), 0)
            r = reflect(n, l)
            v = normalize(np.array([0, 0, 0]) - shading_p)
            specular_color += material['Ks'] * le * pow(max(np.dot(r, v), 0), material['n'])

    color = ambient_color + diffuse_color + specular_color
    color = np.clip(color, 0, 1)
    tri_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))

    return tri_color


def normalize(vector):
    return vector / np.linalg.norm(vector)


def reflect(n_vector, l_vector):
    return 2 * np.dot(n_vector, l_vector) * n_vector - l_vector
