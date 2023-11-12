from time import sleep


class TimeHandler:
    def __init__(self, time: int) -> None:
        self.time = time
    

    def timeHand(self):
        if self.time is not None:
            while True:
                sleep(60)
                self.time -= 1
                if self.time == 0:
                    break