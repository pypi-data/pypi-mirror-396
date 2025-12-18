import json
import random

from loguru import logger
from pushikoo_interface import Detail, Getter

from pushikoo_getter_skland.config import SklandAdapterConfig, SklandInstanceConfig

from hypergryph_api import HypergryphAPI
from skland_api import SklandAPI, SklandAPIExpection


class SklandGetter(Getter[SklandAdapterConfig, SklandInstanceConfig]):
    """Skland (森空岛) getter for Pushikoo."""

    def __init__(self) -> None:
        self.api: SklandAPI | None = None
        self._init_api()
        logger.debug(f"{self.adapter_name}.{self.identifier} initialized")

    def _init_api(self) -> None:
        """Initialize or reinitialize the Skland API."""
        self.api = SklandAPI(
            HypergryphAPI(
                phone=self.instance_config.phone,
                password=self.instance_config.password,
            )
        )

    def timeline(self) -> list[str]:
        """Return list of article IDs from feed."""
        page_size = random.randrange(
            self.config.page_size_min,
            self.config.page_size_max,
        )
        logger.debug(f"page_size={page_size}")

        try:
            feed_list_response = self.api.web_v1_feed_list(pageSize=page_size)
        except (AttributeError, SklandAPIExpection) as e:
            logger.debug(f"Initing or Re-initing Skland API: {e}")
            self._init_api()
            try:
                feed_list_response = self.api.web_v1_feed_list(pageSize=page_size)
            except SklandAPIExpection:
                return []

        feed_list = feed_list_response["list"]
        return [article["item"]["id"] for article in feed_list]

    def detail(self, identifier: str) -> Detail:
        """Get detail of a single article."""
        detail_response = self.api.api_v1_item_list([identifier])["list"][0]
        article = self._parse_article(detail_response)

        return Detail(
            ts=article["publishedAtTs"],
            content=article["content"],
            title=article["title"],
            author_id=article["userId"],
            author_name=article["user_name"],
            url=article["url"],
            image=article["pics"],
            extra_detail=[article["ip"]] if article["ip"] else [],
        )

    def _parse_article(self, detail: dict) -> dict:
        """Parse article detail from API response."""
        item = detail["item"]
        user = detail["user"]
        content = ""

        # Parse format JSON to extract text content
        format_ = json.loads(item["format"])
        format_data = format_["data"]

        for slice_ in format_data:
            slice_type = slice_["type"]

            if slice_type == "paragraph":
                for slice_content in slice_.get("contents", []):
                    content_type = slice_content["type"]

                    if content_type == "text":
                        content_id = slice_content["contentId"]
                        text = next(
                            (
                                s["c"]
                                for s in item["textSlice"]
                                if s["id"] == content_id
                            ),
                            "",
                        )
                        content += text
                    elif content_type == "at":
                        content_id = slice_content["contentId"]
                        at_text = next(
                            (
                                f"@{s['c']}"
                                for s in item["atSlice"]
                                if s["id"] == content_id
                            ),
                            "",
                        )
                        content += at_text
                    elif content_type == "link":
                        content_id = slice_content["contentId"]
                        link_id = slice_content["linkId"]
                        link = next(
                            (s["c"] for s in item["linkSlice"] if s["id"] == link_id),
                            "",
                        )
                        text = next(
                            (
                                s["c"]
                                for s in item["textSlice"]
                                if s["id"] == content_id
                            ),
                            "",
                        )
                        content += f"{text}（{link}）"
                content += "\n"
            elif slice_type == "b_video":
                bv_id = slice_["bvId"]
                bv = next(
                    (s["c"] for s in item["bvSlice"] if s["id"] == bv_id),
                    "",
                )
                content += f"https://www.bilibili.com/video/{bv}\n"

        # Get image URLs (excluding gifs)
        pics = [
            pic["url"]
            for pic in item.get("imageListSlice", [])
            if pic.get("format") != "gif"
        ]

        return {
            "user_name": user["nickname"],
            "title": item["title"],
            "ip": item.get("latestIpLocation", ""),
            "publishedAtTs": item["publishedAtTs"],
            "latestEditAtTs": item.get("latestEditAtTs"),
            "id": item["id"],
            "userId": item["userId"],
            "pics": pics,
            "url": f"https://www.skland.com/article?id={item['id']}",
            "content": content.strip(),
        }
