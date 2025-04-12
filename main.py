# main.py
from multiprocessing import Process
from threading import Thread
from stats_manager import get_shared_stats
from yolo_detector import run_detection
from dash_app import run_dash

if __name__ == "__main__":
    shared_data = get_shared_stats()

    p1 = Process(target=run_detection, args=(shared_data,))
    t2 = Thread(target=run_dash, args=(shared_data,))

    p1.start()
    t2.start()

    p1.join()
    t2.join()
