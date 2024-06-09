import numpy as np


def cross(a, b):
    return np.cross(a, b)


def create_view_matrix(_from, to):
    from_np = np.array(_from)
    to_np = np.array(to)
    r = from_np - to_np
    n = (from_np - to_np) / np.linalg.norm(from_np - to_np)
    v = np.array([0, 1, 0])
    u = cross(v, n)
    u = u / np.linalg.norm(u)
    v = cross(n, u)

    view_matrix = np.array([
        [u[0], u[1], u[2], -np.dot(r, u)],
        [v[0], v[1], v[2], -np.dot(r, v)],
        [n[0], n[1], n[2], -np.dot(r, n)],
        [0, 0, 0, 1]
    ])

    return view_matrix


def create_projection_matrix(near, far, right, left, top, bottom):
    projection_matrix = np.array([[2.0 * near / (right - left), 0, (right + left) / (right - left), 0],
                                  [0, 2.0 * near / (top - bottom), (top + bottom) / (top - bottom), 0],
                                  [0, 0, -(far + near) / (far - near), -2.0 * (far * near) / (far - near)],
                                  [0, 0, -1, 0]])
    return projection_matrix


def create_scale_matrix(scale):
    scale_matrix = np.array([
        [scale[0], 0, 0, 0],
        [0, scale[1], 0, 0],
        [0, 0, scale[2], 0],
        [0, 0, 0, 1]
    ])

    return scale_matrix


def create_rotation_matrix(rotation):
    rotation_matrix = np.eye(4)
    if rotation[0] != 0:
        theta_x = np.radians(rotation[0])
        rotation_matrix_x = np.array([
            [1, 0, 0, 0],
            [0, np.cos(theta_x), -np.sin(theta_x), 0],
            [0, np.sin(theta_x), np.cos(theta_x), 0],
            [0, 0, 0, 1]
        ])
        rotation_matrix = np.dot(rotation_matrix, rotation_matrix_x)

    if rotation[1] != 0:
        theta_y = np.radians(rotation[1])
        rotation_matrix_y = np.array([
            [np.cos(theta_y), 0, np.sin(theta_y), 0],
            [0, 1, 0, 0],
            [-np.sin(theta_y), 0, np.cos(theta_y), 0],
            [0, 0, 0, 1]
        ])
        rotation_matrix = np.dot(rotation_matrix, rotation_matrix_y)

    if rotation[2] != 0:
        theta_z = np.radians(rotation[2])
        rotation_matrix_z = np.array([
            [np.cos(theta_z), -np.sin(theta_z), 0, 0],
            [np.sin(theta_z), np.cos(theta_z), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        rotation_matrix = np.dot(rotation_matrix, rotation_matrix_z)

    return rotation_matrix


def create_translation_matrix(translation):
    translation_matrix = np.array([
        [1, 0, 0, translation[0]],
        [0, 1, 0, translation[1]],
        [0, 0, 1, translation[2]],
        [0, 0, 0, 1]
    ])
    return translation_matrix


def create_model_matrix(scale, rotation, translation):
    model_matrix = np.eye(4)

    # Apply scaling
    if scale is not None:
        scale_matrix = create_scale_matrix(scale)
        model_matrix = np.dot(scale_matrix, model_matrix)

    # Apply rotation
    if rotation is not None:
        rotation_matrix = create_rotation_matrix(rotation)
        model_matrix = np.dot(rotation_matrix, model_matrix)

    # Apply translation
    if translation is not None:
        translation_matrix = create_translation_matrix(translation)
        model_matrix = np.dot(translation_matrix, model_matrix)

    return model_matrix


def create_normal_model_matrix(scale, rotation):
    normal_model_matrix = np.eye(4)

    # Apply scaling
    if scale is not None:
        scale_matrix = create_scale_matrix(scale)
        scale_matrix_inverse = np.linalg.inv(scale_matrix)
        normal_model_matrix = np.dot(scale_matrix_inverse.T, normal_model_matrix)

    # Apply rotation
    if rotation is not None:
        rotation_matrix = create_rotation_matrix(rotation)
        normal_model_matrix = np.dot(rotation_matrix, normal_model_matrix)

    return normal_model_matrix


def create_normal_model_scale_matrix(scale):
    normal_model_scale_matrix = np.eye(4)

    if scale is not None:
        scale_matrix = create_scale_matrix(scale)
        scale_matrix_inverse = np.linalg.inv(scale_matrix)
        normal_model_scale_matrix = np.dot(scale_matrix_inverse.T, normal_model_scale_matrix)

    return normal_model_scale_matrix
