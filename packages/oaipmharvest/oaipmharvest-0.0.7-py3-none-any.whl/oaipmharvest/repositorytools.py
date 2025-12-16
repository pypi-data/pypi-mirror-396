# from oaipmharvest.commons import get_logger, iter_sets
# from oaipmharvest.settings import get_args, get_settings
import models

REPO_FILE_NAME = ".oaipmharvest_repo.db"


class RepositoryManager:
    def __init__(self, folder):
        self.db = models.database
        self.db.init(folder / REPO_FILE_NAME)
        self.db.connect()
        self.init_db()

    def init_db(self):
        with self.db as db:
            db.create_tables([models.ResumptionToken, models.HarvestRun])
