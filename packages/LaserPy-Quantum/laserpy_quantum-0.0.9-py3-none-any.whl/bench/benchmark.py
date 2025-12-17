import timeit
import functools

def benchmark(number: int = 1, repeat: int = 5, beta= 0.9):
    """
    A decorator to benchmark the runtime of a function.

    Args:
        number (int): The number of times to execute the function in one trial.
        repeat (int): The number of times to repeat the timing trial.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # The function's name and its containing module/class
            func_name = func.__name__
            instance = args[0] if args else None

            print(f"\n--- Benchmarking '{func_name}' ---")
            print(f"Number of executions per trial: {number}")
            print(f"Number of trials (repeats): {repeat}")

            times = []
            time_moving_avg = 0
                        
            for _ in range(repeat):
                # Use timeit.default_timer for high-resolution timing
                timer = timeit.default_timer
                
                start = timer()
                for _ in range(number):
                    result = func(*args, **kwargs) # Execute the original function
                end = timer()

                total_time = (end - start)
                time_moving_avg = (1 - beta) * time_moving_avg + beta * total_time
                times.append(total_time)

            # Process the results
            if not times:
                print("Benchmarking failed or returned no data.")
                return result # Return the last result if successful

            # Convert results to milliseconds and calculate metrics
            times_ms = [t * 1000 / number for t in times]
            min_time_ms = min(times_ms)
            avg_time_ms = sum(times_ms) / len(times_ms)

            time_moving_avg_ms = time_moving_avg * 1000 / number

            print("--- Results (time per execution in milliseconds) ---")
            print(f"All trial times: {[f'{t:.6f}' for t in times_ms]} ms")
            print(f"Fastest time (min): {min_time_ms:.6f} ms")
            print(f"Average time: {avg_time_ms:.6f} ms")
            print(f"Moving Average time (min): {time_moving_avg_ms:.6f} ms")
            print(f"---------------------------------------------------\n")

            # Return the result of the function call
            return result
        return wrapper
    return decorator