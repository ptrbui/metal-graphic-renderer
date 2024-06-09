SHADING_METHOD = "phong"
ANTIALIASING_FILTER = [(-0.52, 0.38, 0.128),
                       (0.41, 0.56, 0.119),
                       (0.27, 0.08, 0.294),
                       (-0.17, -0.29, 0.249),
                       (0.58, -0.55, 0.104),
                       (-0.31, -0.71, 0.106)]
WIDTH = 512
HEIGHT = 512
SCENE_PATH = "./assets/scene.json"
GEOMETRY_PATH = "./assets/teapot.json"


def update_size(new_width, new_height):
    global WIDTH, HEIGHT
    WIDTH = new_width
    HEIGHT = new_height


def update_scene_path(new_scene_path):
    global SCENE_PATH
    SCENE_PATH = new_scene_path
