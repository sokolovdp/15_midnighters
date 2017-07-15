from datetime import datetime
import pytz
import logging
import requests

USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                            "Chrome/59.0.3071.104 Safari/537.36"}
DEVMAN_API_URL = "https://devman.org/api/challenges/solution_attempts/"
MAX_TIMEOUT = 5
SECS_IN_HOUR = 3600
LATE_HOUR = 4


def get_response_from_devman_api(page=1) -> "dict":
    try:
        response = requests.get(DEVMAN_API_URL, params=dict(page=page), headers=USER_AGENT, timeout=MAX_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as rer:
        logger.error("devman api error, exception={}".format(rer))
    else:
        return response.json()


def load_all_records() -> "list":
    all_records = list()
    page = get_response_from_devman_api(page=1)
    pages_amount = page['number_of_pages']
    all_records.extend(page['records'])
    for n in range(1, pages_amount):
        page = get_response_from_devman_api(page=n + 1)
        all_records.extend(page['records'])
    return all_records


def find_midnighters(all_records: "list") -> "list":
    midnighters = list()
    for record in all_records:
        timezone = pytz.timezone(record['timezone'])
        timestamp = record['timestamp']
        time = pytz.utc.localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone)
        local_user_time = time.hour + (time.utcoffset().seconds // SECS_IN_HOUR)
        if local_user_time < LATE_HOUR:
            midnighters.append(record['username'])
    return midnighters


def main():
    all_records = [record for record in load_all_records() if record['timestamp']]
    if all_records:
        print("loaded {} valid records".format(len(all_records)))
        midnighters = find_midnighters(all_records)
        print("midnighthers are:", *set(midnighters), sep='\n   ')


def create_logger() -> "class 'logging.RootLogger'":
    new_logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(name)-4s %(levelname)-5s %(message)s')
    new_logger.setLevel(logging.ERROR)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    new_logger.addHandler(ch)
    return new_logger


if __name__ == '__main__':
    logger = create_logger()
    main()
