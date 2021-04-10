# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fantia.jp/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache
import collections
import itertools
import json


class FantiaExtractor(Extractor):
    """Base class for fantia extractors"""
    category = "fantia"
    root = "https://fantia.jp"
    directory_fmt = ("{category}", "{fanclub_id}")
    filename_fmt = "{post_id}_{file_id}.{extension}"
    archive_fmt = "{post_id}_{file_id}"
    _warning = True

    def items(self):
        yield Message.Version, 1

        if self._warning:
            if "_session_id" not in self.session.cookies:
                self.log.warning("no '_session_id' cookie set")
            FantiaExtractor._warning = False

        for url, data in self.posts():
            if data["content_filename"]:
                data["filename"] = data["content_filename"]
                if "." in data["filename"]:
                    data["extension"] = data["filename"][data["filename"].rfind(".")+1:]
                else:
                    data["extension"] = text.ext_from_url(url)
            else:
                data = text.nameext_from_url(url, data)
            data["file_url"] = url

            yield Message.Directory, data
            yield Message.Url, url, data

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, base_url):
        headers = {"Referer": self.root}
        page = 1
        posts_found = True

        while posts_found:
            url = base_url+str(page)
            url = text.ensure_http_scheme(url)
            gallery_page_html = self.request(url, headers=headers).text
            posts_found = False
            for post_id in text.extract_iter(gallery_page_html, 'class="link-block" href="/posts/', '"'):
                posts_found = True
                for url, data in self._get_post_data_and_urls(post_id):
                    yield url, data

            page += 1

    def _get_post_data_and_urls(self, post_id):
        """Fetch and process post data"""
        headers = {"Referer": self.root}
        url = self.root+"/api/v1/posts/"+post_id
        resp = self.request(url, headers=headers).json()["post"]
        post = {
            "post_id": resp["id"],
            "post_url": self.root + "/posts/" + str(resp["id"]),
            "post_title": resp["title"],
            "comment": resp["comment"],
            "rating": resp["rating"],
            "posted_at": resp["posted_at"],
            "fanclub_id": resp["fanclub"]["id"],
            "fanclub_user_id": resp["fanclub"]["user"]["id"],
            "fanclub_user_name": resp["fanclub"]["user"]["name"],
            "fanclub_name": resp["fanclub"]["name"],
            "fanclub_url": self.root + "/fanclubs/" + str(resp["fanclub"]["id"]),
            "tags": resp["tags"]
        }

        if "thumb" in resp and resp["thumb"] and "original" in resp["thumb"]:
            post["content_filename"] = ""
            post["content_category"] = "thumb"
            post["file_id"] = "thumb"
            yield resp["thumb"]["original"], post

        for content in resp["post_contents"]:
            post["content_category"] = content["category"]
            post["content_title"] = content["title"]
            post["content_filename"] = content.get("filename", "")
            post["content_id"] = content["id"]
            if "post_content_photos" in content:
                for photo in content["post_content_photos"]:
                    post["file_id"] = photo["id"]
                    yield photo["url"]["original"], post
            if "download_uri" in content:
                post["file_id"] = content["id"]
                yield self.root+"/"+content["download_uri"], post

class FantiaCreatorExtractor(FantiaExtractor):
    """Extractor for a creator's works"""
    subcategory = "creator"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/fanclubs/([^/?#]+)"
    test = (
        ("https://fantia.jp/fanclubs/6939", {
            "range": "1-25",
            "count": ">= 25",
            "keyword": {
                "fanclub_user_id" : 52152,
                "tags"            : list,
                "title"           : str,
            },
        }),
    )

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.creator_id = match.group(1)

    def posts(self):
        base_url = self.root+"/fanclubs/"+self.creator_id+"/posts?page="

        return self._pagination(base_url)

class FantiaPostExtractor(FantiaExtractor):
    """Extractor for media from a single post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/posts/([^/?#]+)"
    test = (
        ("https://fantia.jp/posts/508363", {
            "count": 6,
            "keyword": {
                "post_title": "zunda逆バニーでおしりｺｯｼｮﾘ",
                "tags": list,
                "rating": "adult",
                "post_id": 508363
            },
        }),
    )

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return self._get_post_data_and_urls(self.post_id)
