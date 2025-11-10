from dataclasses import dataclass


MAIN_URL = "https://min-repo.com/tag/"
HALLS_YAML = "scraper/halls.yaml"
OUTPUT_CSV = "data/csv/halls.csv"
LOG_PATH = "data/log/minrepo.log"
DB_PATH = "data/db/minrepo_02.db"


@dataclass
class HallInfo:
    slug: str
    period: int
