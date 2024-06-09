import pipeline_config


def get_camera_parameter(scene):
    x_res = scene['scene']['camera']['resolution'][0] * pipeline_config.WIDTH
    y_res = scene['scene']['camera']['resolution'][1] * pipeline_config.HEIGHT
    _from = scene['scene']['camera']['from']
    to = scene['scene']['camera']['to']
    near = scene['scene']['camera']['bounds'][0]
    far = scene['scene']['camera']['bounds'][1]
    right = scene['scene']['camera']['bounds'][2]
    left = scene['scene']['camera']['bounds'][3]
    top = scene['scene']['camera']['bounds'][4]
    bottom = scene['scene']['camera']['bounds'][5]

    return x_res, y_res, _from, to, near, far, right, left, top, bottom


def get_transform_parameter(transforms):
    rotation = [0, 0, 0]
    scale = [1, 1, 1]
    translation = [0, 0, 0]
    for transform in transforms:
        if "Rx" in transform:
            rotation[0] = transform["Rx"]
            continue
        elif "Ry" in transform:
            rotation[1] = transform["Ry"]
            continue
        elif "Rz" in transform:
            rotation[2] = transform["Rz"]
            continue
        elif "S" in transform:
            scale = transform["S"]
            continue
        elif "T" in transform:
            translation = transform["T"]
            continue

    return rotation, scale, translation


def get_lights_parameter(scene):
    return scene['scene']['lights']