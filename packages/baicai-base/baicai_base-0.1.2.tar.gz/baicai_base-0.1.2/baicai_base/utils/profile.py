"""
This script is used to profile the code.
"""

import cProfile
import csv
import pstats
import time


def profile_code():
    start_time = time.time()
    ####### code here #######

    ####### code here #######
    end_time = time.time()
    print(f"Time taken to import: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    profile_code()
    profiler.disable()

    # Output profiling results to a CSV file
    with open("profiling_results.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header
        csv_writer.writerow(["ncalls", "tottime", "percall", "cumtime", "filename:lineno(function)"])

        # Create a Stats object and sort by cumulative time
        stats = pstats.Stats(profiler).sort_stats("cumtime")

        # Write each line of the profiling results to the CSV
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            # func is a tuple (filename, lineno, function_name)
            filename, lineno, function_name = func
            # Write to CSV
            csv_writer.writerow([cc, nc, tt, ct, f"{filename}:{lineno}({function_name})"])
