import logging
from pathlib import Path
from datetime import datetime

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# console = logging.StreamHandler()
# logger.addHandler(console)

def saveToFile(path: str, filename: str, text: str, overwrite: bool = False):
    basePath = Path(path)
    if not basePath.is_dir():
        logger.error(
            f"{basePath} is not a directory, or it doesn't exist. File save aborted.")
        return
    fullPath = basePath / filename
    if not overwrite and fullPath.exists():
        logger.error(
            f"{fullPath} exists, will not overwrite. File save aborted")
        return
    try:
        with open(fullPath, 'wt') as file:
            file.write(text)
    except Exception:
        logger.exception(f"Error trying to save a file with path: {fullPath}")