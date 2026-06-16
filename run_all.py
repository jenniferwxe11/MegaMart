from data_generation.generation_runner import run_generation
from dirty_data_generation.run_dirty_generation import run_dirty_generation
from dirty_data_profiling.run_profiling import run_profiling

if __name__ == "__main__":
    run_generation()
    run_dirty_generation()
    run_profiling()
