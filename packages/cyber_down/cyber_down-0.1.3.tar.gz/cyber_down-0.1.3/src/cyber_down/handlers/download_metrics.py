import time


# Display download speed
def _download_speed(downloaded, time_started, bar):
    """ Display download speed """

    time_elapsed = time.time() - time_started
    _speed = downloaded / time_elapsed
    b = 1024

    _SPEED = _speed / b
    bar.text(f"[{_SPEED:.2f} mbps]")
