import logging
import time
import matplotlib.pyplot as plt
import pipeline_config
from core.core import render_sequential, render_parallel, weighted_averaging, weighted_averaging_metal, images_to_numpy

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# List of dimensions we want to use
dimList = [[64, 64], [128, 128], [256, 256], [512, 512], [1024, 1024]]


def compute_difference_render():
    print(" ")
    print("FOR DIMENSIONS " + str(pipeline_config.HEIGHT) + " x " + str(pipeline_config.WIDTH) + ":")

    # RENDER SEQUENTIALLY w/ inputs
    start_time = time.time()
    images_sequential = render_sequential(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    renderSequentialTime = end_time - start_time
    logging.info("time to render sequential images: {}".format(renderSequentialTime))
    images_sequential_np = images_to_numpy(images_sequential)

    # RENDER PARALLEL w/ inputs
    start_time = time.time()
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    renderParallelTime = end_time - start_time
    logging.info("time to render parallel images:   {}".format(renderParallelTime))
    images_parallel_np = images_to_numpy(images_parallel)

    # output a list of length 2
    return [renderSequentialTime, renderParallelTime]


def compute_difference_avg():
    print(" ")
    print("FOR DIMENSIONS " + str(pipeline_config.HEIGHT) + " x " + str(pipeline_config.WIDTH) + ":")

    # RENDER PARALLEL w/ inputs
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    images_parallel_np = images_to_numpy(images_parallel)

    # WEIGHTED AVERAGING w/ inputs
    start = time.time()
    output = weighted_averaging(images_parallel_np)
    end = time.time()
    weightedAvgTime = end - start
    logging.info("time of weighted_averaging:       {}".format(weightedAvgTime))

    # WEIGHTED AVERAGING (METAL) w/ inputs
    start = time.time()
    output_metal = weighted_averaging_metal(images_parallel_np)
    end = time.time()
    metalAvgTime = end - start
    logging.info("time of weighted_averaging_metal: {}".format(metalAvgTime))

    # output a list of length 2
    return [weightedAvgTime, metalAvgTime]


def compute_difference_total():
    print(" ")
    print("FOR DIMENSIONS " + str(pipeline_config.HEIGHT) + " x " + str(pipeline_config.WIDTH) + ":")

    # RENDER SEQUENTIALLY w/ inputs
    start_time = time.time()
    images_sequential = render_sequential(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    renderSequentialTime = end_time - start_time
    images_sequential_np = images_to_numpy(images_sequential)

    # RENDER PARALLEL w/ inputs
    start_time = time.time()
    images_parallel = render_parallel(pipeline_config.SCENE_PATH, pipeline_config.WIDTH, pipeline_config.HEIGHT)
    end_time = time.time()
    renderParallelTime = end_time - start_time
    images_parallel_np = images_to_numpy(images_parallel)

    # WEIGHTED AVERAGING w/ inputs
    start = time.time()
    output = weighted_averaging(images_sequential_np)
    end = time.time()
    weightedAvgTime = end - start
    # output.show()
    # output.save('./output/output.jpg')

    # WEIGHTED AVERAGING (METAL w/ inputs
    start = time.time()
    output_metal = weighted_averaging_metal(images_parallel_np)
    end = time.time()
    metalAvgTime = end - start
    output_metal.show()
    # output_metal.save('./output/output_metal.jpg')

    standardProcessingTime = renderSequentialTime + weightedAvgTime
    optimizedProcessingTime = renderParallelTime + metalAvgTime

    logging.info("Total time to render using standard rendering and averaging:       {}".format(standardProcessingTime))
    logging.info(
        "Total time to render using parallel rendering and metal averaging: {}".format(optimizedProcessingTime))

    # output a list of length 2
    return [standardProcessingTime, optimizedProcessingTime]


def plot_render_difference():
    # initialize a dictionary that maps sets of dimensions to their time results
    timeDict = {}
    # keep track of total time so that we can compute avg performance change
    totalSequentialTime = 0
    totalParallelTime = 0

    for dim in dimList:
        pipeline_config.update_size(dim[0], dim[1])
        newTimes = compute_difference_render()

        # for calculating average
        totalSequentialTime += newTimes[0]
        totalParallelTime += newTimes[1]

        # add to the dictionary
        timeDict[str(pipeline_config.WIDTH) + "x" + str(pipeline_config.HEIGHT)] = newTimes

    renderingPerformanceChange = 100 * (totalSequentialTime - totalParallelTime) / totalSequentialTime

    print(" ")
    print("Average Performance Increase by Percentage (%): ")
    print("From sequential rendering to parallel rendering   : " + str(renderingPerformanceChange) + " (%)")

    # PLOTTING
    resolutions = list(timeDict.keys())
    sequentialTimes = [timeDict[res][0] for res in resolutions]
    parallelTimes = [timeDict[res][1] for res in resolutions]
    plt.figure(figsize=(10, 5))
    plt.plot(resolutions, sequentialTimes, label='Sequential Rendering', marker='o')
    plt.plot(resolutions, parallelTimes, label='Parallel Rendering', marker='o')
    plt.xlabel('Image Resolution')
    plt.ylabel('Time (seconds)')
    plt.title('Rendering Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/render_difference.png')


def plot_weighted_averaging_difference():
    # initialize a dictionary that maps sets of dimensions to their time results
    timeDict = {}
    # keep track of total time so that we can compute avg performance change
    totalWeightAvgTime = 0
    totalWeightAvgTime_metal = 0

    for dim in dimList:
        pipeline_config.update_size(dim[0], dim[1])
        newTimes = compute_difference_avg()

        # for calculating average
        totalWeightAvgTime += newTimes[0]
        totalWeightAvgTime_metal += newTimes[1]

        # add to the dictionary
        timeDict[str(pipeline_config.WIDTH) + "x" + str(pipeline_config.HEIGHT)] = newTimes

    weightedAvgPerformanceChange = 100 * (totalWeightAvgTime - totalWeightAvgTime_metal) / totalWeightAvgTime

    print(" ")
    print("Average Performance Increase by Percentage (%): ")
    print("From weighted averaging after using Metal Compute : " + str(weightedAvgPerformanceChange) + " (%)")

    # PLOTTING
    resolutions = list(timeDict.keys())
    weightedAvgTimes = [timeDict[res][0] for res in resolutions]
    metalAvgTimes = [timeDict[res][1] for res in resolutions]
    plt.figure(figsize=(10, 5))
    plt.plot(resolutions, weightedAvgTimes, label='Weighted Averaging CPU', marker='o')
    plt.plot(resolutions, metalAvgTimes, label='Weighted Averaging Metal', marker='o')
    plt.xlabel('Image Resolution')
    plt.ylabel('Time (seconds)')
    plt.title('Weighted Averaging Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/weighted_averaging_difference.png')


def plot_total_difference():
    # initialize a dictionary that maps sets of dimensions to their time results
    timeDict = {}

    # keep track of total time so that we can compute avg performance change
    totalTimeStandard = 0
    totalTimeOptimized = 0

    for dim in dimList:
        pipeline_config.update_size(dim[0], dim[1])
        newTimes = compute_difference_total()

        # for calculating average
        totalTimeStandard += newTimes[0]
        totalTimeOptimized += newTimes[1]

        # add to the dictionary
        timeDict[str(pipeline_config.WIDTH) + "x" + str(pipeline_config.HEIGHT)] = newTimes

    performanceChange = 100 * (totalTimeStandard - totalTimeOptimized) / totalTimeStandard

    print(" ")
    print("Average Performance Increase by Percentage (%): ")
    print("From sequential rendering to parallel rendering   : " + str(performanceChange) + " (%)")

    # PLOTTING
    resolutions = list(timeDict.keys())

    unoptimizedTime = [timeDict[res][0] for res in resolutions]
    optimizedTime = [timeDict[res][1] for res in resolutions]
    timeDifference = [u - o for u, o in zip(unoptimizedTime, optimizedTime)]

    plt.figure(figsize=(10, 5))
    plt.plot(resolutions, timeDifference, color='red', label='Time Saved with Optimized Rendering', marker='o')
    plt.xlabel('Image Resolution')
    plt.ylabel('Time (seconds)')
    plt.title('Time savings as Image size increases')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/total_difference.png')


def main_test():
    plot_render_difference()
    plot_weighted_averaging_difference()
    plot_total_difference()


if __name__ == '__main__':
    main_test()
