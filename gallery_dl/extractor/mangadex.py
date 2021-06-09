# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangadex.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import memcache
from collections import defaultdict


class MangadexExtractor(Extractor):
    """Base class for mangadex extractors"""
    category = "mangadex"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    archive_fmt = "{chapter_id}_{page}"
    root = "https://mangadex.org"

    # mangadex-to-iso639-1 codes
    iso639_map = {
        "br": "pt",
        "ct": "ca",
        "gb": "en",
        "vn": "vi",
    }

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = MangadexAPI(self)
        self.uuid = match.group(1)

    def items(self):
        for chapter in self.chapters():

            relationships = defaultdict(list)
            for item in chapter["relationships"]:
                relationships[item["type"]].append(item["id"])
            manga = self.api.manga(relationships["manga"][0])
            for item in manga["relationships"]:
                relationships[item["type"]].append(item["id"])

            cattributes = chapter["data"]["attributes"]
            mattributes = manga["data"]["attributes"]
            lang = cattributes["translatedLanguage"].partition("-")[0]

            if cattributes["chapter"]:
                chnum, sep, minor = cattributes["chapter"].partition(".")
            else:
                chnum, sep, minor = 0, "", ""

            data = {
                "manga"   : mattributes["title"]["en"],
                "manga_id": manga["data"]["id"],
                "title"   : cattributes["title"],
                "volume"  : text.parse_int(cattributes["volume"]),
                "chapter" : text.parse_int(chnum),
                "chapter_minor": sep + minor,
                "chapter_id": chapter["data"]["id"],
                "date"    : text.parse_datetime(cattributes["publishAt"]),
                "lang"    : lang,
                "language": util.code_to_language(lang),
                "count"   : len(cattributes["data"]),
            }

            if self.config("metadata"):
                data["artist"] = [
                    self.api.author(uuid)["data"]["attributes"]["name"]
                    for uuid in relationships["artist"]]
                data["author"] = [
                    self.api.author(uuid)["data"]["attributes"]["name"]
                    for uuid in relationships["author"]]
                data["group"] = [
                    self.api.group(uuid)["data"]["attributes"]["name"]
                    for uuid in relationships["scanlation_group"]]

            base = "{}/data/{}/".format(
                self.api.athome_server(chapter["data"]["id"])["baseUrl"],
                cattributes["hash"])

            yield Message.Directory, data
            for data["page"], page in enumerate(cattributes["data"], 1):
                text.nameext_from_url(page, data)
                yield Message.Url, base + page, data


class MangadexChapterExtractor(MangadexExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    subcategory = "chapter"
    pattern = (r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)"
               r"/chapter/([0-9a-f-]+)")
    test = (
        ("https://mangadex.org/chapter/f946ac53-0b71-4b5d-aeb2-7931b13c4aaa", {
            "keyword": "f6c2b908df06eb834d56193dfe1fa1f7c2c4dccd",
            #  "content": "50383a4c15124682057b197d40261641a98db514",
        }),
        # oneshot
        ("https://mangadex.org/chapter/61a88817-9c29-4281-bdf1-77b3c1be9831", {
            "options": (("metadata", True),),
            "count": 64,
            "keyword": "6abcbe1e24eeb1049dc931958853cd767ee483fb",
        }),
        # MANGA Plus (#1154)
        ("https://mangadex.org/chapter/8d50ed68-8298-4ac9-b63d-cb2aea143dd0", {
            "exception": exception.StopExtraction,
        }),
    )

    def chapters(self):
        return (self.api.chapter(self.uuid),)


class MangadexMangaExtractor(MangadexExtractor):
    """Extractor for manga from mangadex.org"""
    subcategory = "manga"
    pattern = (r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)"
               r"/(?:title|manga)/([0-9a-f-]+)")
    test = (
        ("https://mangadex.org/title/f90c4398-8aad-4f51-8a1f-024ca09fdcbc", {
            "keyword": {
                "manga"   : "Souten no Koumori",
                "manga_id": "f90c4398-8aad-4f51-8a1f-024ca09fdcbc",
                "title"   : "re:One[Ss]hot",
                "volume"  : 0,
                "chapter" : 0,
                "chapter_minor": "",
                "chapter_id": str,
                "date"    : "type:datetime",
                "lang"    : str,
                "language": str,
            },
        }),
        ("https://mangadex.cc/manga/d0c88e3b-ea64-4e07-9841-c1d2ac982f4a/"),
        ("https://mangadex.org/title/7c1e2742-a086-4fd3-a3be-701fd6cf0be9", {
            "count": 16,
        }),
    )

    def chapters(self):
        return self.api.manga_feed(self.uuid)


class MangadexAPI():
    """Interface for the MangaDex API v5"""

    def __init__(self, extr):
        self.extractor = extr
        server = extr.config("api-server")
        self.root = ("https://api.mangadex.org" if server is None
                     else text.ensure_http_scheme(server).rstrip("/"))

    def athome_server(self, uuid):
        return self._call("/at-home/server/" + uuid)

    @memcache(keyarg=1)
    def author(self, uuid):
        return self._call("/author/" + uuid)

    def chapter(self, uuid):
        return self._call("/chapter/" + uuid)

    @memcache(keyarg=1)
    def group(self, uuid):
        return self._call("/group/" + uuid)

    @memcache(keyarg=1)
    def manga(self, uuid):
        return self._call("/manga/" + uuid)

    def manga_feed(self, uuid):
        config = self.extractor.config
        order = "desc" if config("chapter-reverse") else "asc"
        params = {
            "order[volume]"       : order,
            "order[chapter]"      : order,
            "translatedLanguage[]": config("lang"),
        }
        return self._pagination("/manga/" + uuid + "/feed", params)

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(url, params=params, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                until = response.headers.get("X-RateLimit-Retry-After")
                self.extractor.wait(until=until)
                continue

            msg = ", ".join('{title}: {detail}'.format_map(error)
                            for error in response.json()["errors"])
            raise exception.StopExtraction(
                "%s %s (%s)", response.status_code, response.reason, msg)

    def _pagination(self, endpoint, params=None):
        if params is None:
            params = {}
        params["offset"] = 0

        while True:
            data = self._call(endpoint, params)
            yield from data["results"]

            params["offset"] = data["offset"] + data["limit"]
            if params["offset"] >= data["total"]:
                return
