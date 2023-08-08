import logging 

class HazelRecommendationEngine():

    def meta(self):
        self.VERSION = 0.1
        self.BUILD_TYPE = "ALPHA"

    def __init__(self) -> None:
        self.meta()
        logging.info("Hazel Recommendation Engine")
        