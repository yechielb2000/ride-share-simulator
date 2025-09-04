from shared.config.config import config
from shared.files import load_models_from_json
from shared.logger import logger
from shared.models import Driver
from shared.redis_sdk import redis_client


def main():
    logger.info("Loading drivers")
    for driver in load_models_from_json(config.drivers_loader.json_file, "drivers", Driver):
        redis_client.driver.add(driver)
        logger.info("Driver added to redis index", driver=driver.model_dump_json())
    logger.info("Finished loading drivers")


if __name__ == "__main__":
    main()
