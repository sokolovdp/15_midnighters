import requests
from datetime import datetime
import pytz
import ast
import logging

user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                            "Chrome/59.0.3071.104 Safari/537.36"}
MAX_RESPONSE_TIMEOUT = 7
devman_api = "https://devman.org/api/challenges/solution_attempts/"
SECS_IN_HOUR = 3600
LATE_HOUR = 4


def get_response_from_devman_api(page=1) -> "str":
    params = dict(page=page)
    try:
        response = requests.get(devman_api, params, headers=user_agent, timeout=MAX_RESPONSE_TIMEOUT)
    except requests.exceptions.Timeout:
        logger.error("devman api response timeout")
    else:
        if response.ok:
            return response.text.replace('null', '0.0')
        else:
            logger.error("response error=", response.status_code)


def load_amount_of_records_pages() -> "int":
    page = get_response_from_devman_api()
    if page:
        page_info = ast.literal_eval(page)  # convert string to dict
        return page_info['number_of_pages']


def load_all_records(pages_amount: "int") -> "list":
    all_records = list()
    for n in range(pages_amount):
        page = get_response_from_devman_api(page=n + 1)
        if page:
            page_info = ast.literal_eval(page)
            for record in page_info['records']:
                all_records.append(record)
        else:
            logger.error("received empty page")
            return list()
    return all_records


def get_midnighters(all_records: "list") -> "list":
    midnighters = list()
    for record in all_records:
        timezone = pytz.timezone(record['timezone'])
        timestamp = record['timestamp']
        time = pytz.utc.localize(datetime.utcfromtimestamp(timestamp)).astimezone(timezone)
        local_time = time.hour + (time.utcoffset().seconds // SECS_IN_HOUR)
        if 0 < local_time < LATE_HOUR:
            midnighters.append(record['username'])
    return midnighters


def main():
    pages_amount = load_amount_of_records_pages()
    all_records = [record for record in load_all_records(pages_amount) if record['timestamp'] != 0.0]
    if pages_amount and all_records:
        print("loaded {} valid records from {} pages".format(len(all_records), pages_amount))
        midnighters = get_midnighters(all_records)
        print("midnighthers are:", *set(midnighters), sep='\n   ')
    else:
        print('devman api is not available')


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logger.setLevel(logging.ERROR)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    main()
