import logging
import time
import matplotlib.pyplot as plt
import pipeline_config
from main import render_sequential, render_parallel, weighted_averaging, weighted_averaging_metal, images_to_numpy

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

scene_paths = ["./assets/test_geom/scene1.json",
               "./assets/test_geom/scene2.json",
               "./assets/test_geom/scene3.json",
               "./assets/test_geom/scene4.json",
               "./assets/test_geom/scene5.json"]

def compute_difference_render(scene_path):
    pipeline_config.update_scene_path(scene_path)
    print("\nFOR SCENE PATH: " + scene_path)

    start_time = time.time()
    images_sequential = render_sequential(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    renderSequentialTime = time.time() - start_time
    logging.info("time to render sequential images: {}".format(renderSequentialTime))

    start_time = time.time()
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    renderParallelTime = time.time() - start_time
    logging.info("time to render parallel images:   {}".format(renderParallelTime))

    return renderSequentialTime, renderParallelTime

def compute_difference_avg(scene_path):
    pipeline_config.update_scene_path(scene_path)
    print("\nFOR SCENE PATH: " + scene_path)

    start_time = time.time()
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    images_parallel_np = images_to_numpy(images_parallel)

    start = time.time()
    weighted_averaging(images_parallel_np)
    weightedAvgTime = time.time() - start
    logging.info("time of weighted_averaging:       {}".format(weightedAvgTime))

    start = time.time()
    weighted_averaging_metal(images_parallel_np)
    metalAvgTime = time.time() - start
    logging.info("time of weighted_averaging_metal: {}".format(metalAvgTime))

    return weightedAvgTime, metalAvgTime

def plot_render_difference():
    timeDict = {}
    totalSequentialTime = 0
    totalParallelTime = 0

    for scene_path in scene_paths:
        times = compute_difference_render(scene_path)
        totalSequentialTime += times[0]
        totalParallelTime += times[1]
        timeDict[scene_path] = times

    renderingPerformanceChange = 100 * (totalParallelTime - totalSequentialTime) / totalSequentialTime
    print("\nAverage Performance Increase by Percentage (%): ")
    print("From sequential rendering to parallel rendering   : {:.2f} (%)".format(renderingPerformanceChange))

    scenes = list(timeDict.keys())
    sequentialTimes = [timeDict[scene][0] for scene in scenes]
    parallelTimes = [timeDict[scene][1] for scene in scenes]

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(scene_paths)+1), sequentialTimes, label='Sequential Rendering', marker='o')
    plt.plot(range(1, len(scene_paths)+1), parallelTimes, label='Parallel Rendering', marker='o')
    plt.xlabel('Scene')
    plt.ylabel('Time (seconds)')
    plt.title('Rendering Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/render_difference_multiple_teapots.png')

def plot_weighted_averaging_difference():
    timeDict = {}
    totalWeightAvgTime = 0
    totalWeightAvgTime_metal = 0

    for scene_path in scene_paths:
        times = compute_difference_avg(scene_path)
        totalWeightAvgTime += times[0]
        totalWeightAvgTime_metal += times[1]
        timeDict[scene_path] = times

    weightedAvgPerformanceChange = 100 * (totalWeightAvgTime_metal - totalWeightAvgTime) / totalWeightAvgTime
    print("\nAverage Performance Increase by Percentage (%): ")
    print("From CPU averaging to Metal averaging   : {:.2f} (%)".format(weightedAvgPerformanceChange))

    scenes = list(timeDict.keys())
    weightedAvgTimes = [timeDict[scene][0] for scene in scenes]
    metalAvgTimes = [timeDict[scene][1] for scene in scenes]

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(scene_paths)+1), weightedAvgTimes, label='Weighted Averaging CPU', marker='o')
    plt.plot(range(1, len(scene_paths)+1), metalAvgTimes, label='Weighted Averaging Metal', marker='o')
    plt.xlabel('Scene')
    plt.ylabel('Time (seconds)')
    plt.title('Weighted Averaging Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/weighted_averaging_difference_multiple_teapots.png')

if __name__ == '__main__':
    plot_render_difference()
    plot_weighted_averaging_difference()
