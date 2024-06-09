import sys
import pipeline_config
from core.core import render_parallel, weighted_averaging_metal, images_to_numpy


def main():
    width_arg = int(sys.argv[1])
    height_arg = int(sys.argv[2])
    pipeline_config.update_size(width_arg, height_arg)
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, width_arg, height_arg)
    images_parallel_np = images_to_numpy(images_parallel)
    output_metal = weighted_averaging_metal(images_parallel_np)
    output_metal.show()


if __name__ == '__main__':
    main()
