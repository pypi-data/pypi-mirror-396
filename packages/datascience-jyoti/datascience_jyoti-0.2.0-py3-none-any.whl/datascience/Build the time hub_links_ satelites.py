import datetime
import time
import threading

class TimeHub:
    def __init__(self):
        self.time_links = []

    def add_time_link(self, link):
        self.time_links.append(link)

    def distribute_time(self):
        current_time = datetime.datetime.now(datetime.UTC)  
        for link in self.time_links:
            link.receive_time(current_time)


class TimeLink:
    def __init__(self, satellite):
        self.satellite = satellite

    def receive_time(self, current_time):
        self.satellite.update_time(current_time)


class Satellite:
    def __init__(self, name):
        self.name = name
        self.current_time = None

    def update_time(self, current_time):
        self.current_time = current_time

    def get_time(self):
        return self.current_time


def main():
    time_hub = TimeHub()

    satellite1 = Satellite("Satellite_1")
    satellite2 = Satellite("Satellite_2")

    link1 = TimeLink(satellite1)
    link2 = TimeLink(satellite2)

    time_hub.add_time_link(link1)
    time_hub.add_time_link(link2)

    # Thread to sync time every second
    def sync_time():
        while True:
            time_hub.distribute_time()
            time.sleep(1)

    sync_thread = threading.Thread(target=sync_time)
    sync_thread.daemon = True
    sync_thread.start()

    # Let it sync for 5 seconds
    time.sleep(5)

    print(f"{satellite1.name} Time: {satellite1.get_time()}")
    print(f"{satellite2.name} Time: {satellite2.get_time()}")


if __name__ == "__main__":
    main()
