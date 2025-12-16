import inspect
import logging

def _get_caller_name(levels: int = 3) -> str:
    frame = inspect.currentframe()
    try:
        if frame is None:
            raise RuntimeError("No current frame available")

        cur = frame
        for _ in range(levels):
            nxt = cur.f_back
            if nxt is None:
                raise RuntimeError(f"Call stack shorter than {levels} frames")
            cur = nxt

        return cur.f_code.co_name
    finally:
        del frame


def get_spark():
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    logging.info(f"Found the spark session : {spark}")
    if spark is None:
        raise Exception("Spark session does not exists.")
    return spark
