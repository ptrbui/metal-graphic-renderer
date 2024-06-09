import time
import logging

import pipeline_config
from core.core import render_sequential, render_parallel, weighted_averaging, weighted_averaging_metal, images_to_numpy

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def main():
    #
    logging.info("render_sequential started")
    start_time = time.time()
    images_sequential = render_sequential(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    logging.info("render_sequential finished")
    logging.info('time to render sequential images: {}'.format(end_time - start_time))
    images_sequential_np = images_to_numpy(images_sequential)

    #
    logging.info("render_parallel started")
    start_time = time.time()
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    logging.info("render_parallel finished")
    logging.info('time to render parallel images: {}'.format(end_time - start_time))
    images_parallel_np = images_to_numpy(images_parallel)

    #
    logging.info("weighted_averaging started")
    start = time.time()
    output = weighted_averaging(images_sequential_np)
    end = time.time()
    logging.info("weighted_averaging finished")
    logging.info("time of weighted_averaging: {}".format(end - start))
    output.show()
    output.save('./output/output.jpg')

    #
    logging.info("weighted_averaging_metal started")
    start = time.time()
    output_metal = weighted_averaging_metal(images_parallel_np)
    end = time.time()
    logging.info("weighted_averaging_metal finished")
    logging.info("time of weighted_averaging_metal: {}".format(end - start))
    output_metal.show()
    output_metal.save('./output/output_metal.jpg')


if __name__ == '__main__':
    main()
