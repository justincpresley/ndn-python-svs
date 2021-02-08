import sys
import time


def current_milli_time():
    return round(time.time() * 1000)

def main() -> int:
    curr_time = current_milli_time()
    print(curr_time)
    time.sleep(30)
    end_time = current_milli_time()
    print(end_time)

if __name__ == "__main__":
    sys.exit(main())
