import json
import random
import time
from dataclasses import dataclass

import httpx


class TooManyRequests(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Too many requests, consider using a proxy or increasing the delay between requests."


@dataclass
class _APIBase:
    source_lang: str = "auto"
    target_lang: str = "en"
    proxies: dict | None = None

    def translate(self):
        raise NotImplementedError("Do not use _APIBase directly")

    def handle_response(self, resp: int) -> str:
        if resp.status_code == 429:
            raise TooManyRequests()
        if resp.status_code != 200:
            raise Exception(f"Error: {resp.status_code}")
        return resp.text


class DeepLAPI(
    _APIBase
):  # FIXME: Rate limit too low, maybe use the official API instead?
    API = "deepl"
    API_URL = "https://www2.deepl.com/jsonrpc"
    HEADERS = {  # Mimic DeepL iOS App
        "Content-Type": "application/json",
        "Accept": "*/*",
        "x-app-os-name": "iOS",
        "x-app-os-version": "16.3.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "x-app-device": "iPhone13,2",
        "User-Agent": "DeepL-iOS/2.9.1 iOS 16.3.0 (iPhone13,2)",
        "x-app-build": "510265",
        "x-app-version": "2.9.1",
        "Connection": "keep-alive",
    }

    def __get_i_count(self, text: str) -> int:
        return text.count("i")

    def __get_random_number(self) -> int:
        random.seed(time.time())
        num = random.randint(8300000, 8399998)
        return num * 1000

    def __get_timestamp(self, i_count: int) -> int:
        ts = int(time.time() * 1000)
        if i_count == 0:
            return ts
        i_count += 1
        return ts - ts % i_count + i_count

    def __get_post_data(self, text: str) -> str:
        i_count = self.__get_i_count(text)
        id = self.__get_random_number()
        post_data = {
            "jsonrpc": "2.0",
            "method": "LMT_handle_texts",
            "id": id,
            "params": {
                "texts": [{"text": text, "requestAlternatives": 0}],
                "splitting": "newlines",
                "lang": {
                    "source_lang_user_selected": self.source_lang,
                    "target_lang": self.target_lang,
                },
                "timestamp": self.__get_timestamp(i_count),
                "commonJobParams": {
                    "wasSpoken": False,
                    "transcribe_as": "",
                },
            },
        }
        post_data_str = json.dumps(post_data, ensure_ascii=False)
        if (id + 5) % 29 == 0 or (id + 3) % 13 == 0:
            post_data_str = post_data_str.replace('"method":"', '"method" : "', -1)
        else:
            post_data_str = post_data_str.replace('"method":"', '"method": "', -1)
        return post_data_str

    def translate(self, text: str) -> str:
        post_data_str = self.__get_post_data(text)
        with httpx.Client(proxies=self.proxies) as client:
            resp = client.post(
                url=self.API_URL, data=post_data_str, headers=self.HEADERS
            )
            resp_text = self.handle_response(resp)
            resp_json = json.loads(resp_text)
            return resp_json["result"]["texts"][0]["text"]


class GoogleTranslateAPI(_APIBase):
    # FIXME: Use /m endpoint instead, this one only translates the first sentence
    API = "google"
    BASE_URL = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "dt": "t",
        "ie": "UTF-8",
        "oe": "UTF-8",
    }

    def translate(self, text: str) -> str:
        with httpx.Client(proxies=self.proxies) as client:
            resp = client.get(
                url=self.BASE_URL,
                params={
                    "q": text,
                    "sl": self.source_lang,
                    "tl": self.target_lang,
                    **self.params,
                },
            )
            resp_text = self.handle_response(resp)
            resp_json = json.loads(resp_text)
            return resp_json[0][0][0]


def Translator(
    api: str = "deepl",
    source_lang: str = "auto",
    target_lang: str = "en",
    proxies: dict | None = None,
) -> DeepLAPI | GoogleTranslateAPI:
    api = api.lower()
    if api == "deepl":
        return DeepLAPI(source_lang, target_lang, proxies)
    elif api == "google":
        return GoogleTranslateAPI(source_lang, target_lang, proxies)
    else:
        raise ValueError("Invalid API, please choose either 'deepl' or 'google'")
