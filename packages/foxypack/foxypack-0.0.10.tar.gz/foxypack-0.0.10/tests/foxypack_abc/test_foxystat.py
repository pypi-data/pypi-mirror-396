import random
from datetime import date, timedelta
from typing import Union

from foxypack import (
    FoxyStat,
    AnswersAnalysis,
    DenialAsynchronousServiceException,
    AnswersStatistics,
    DenialSynchronousServiceException,
)

from urllib.parse import urlparse, parse_qs

from foxypack.foxypack_abc.answers import AnswersSocialContent, AnswersSocialContainer


class FakeStat(FoxyStat):
    """Test implementation of FoxyStat to test functionality"""

    def __init__(self):
        self.fake_containers = {
            "qsgqsdrr": {
                "system_id": "CH_001",
                "title": "Tech Reviews Channel",
                "subscribers": 15400,
                "creation_date": date(2020, 3, 15),
            },
            "programming": {
                "system_id": "CH_002",
                "title": "Code Masters",
                "subscribers": 89200,
                "creation_date": date(2019, 7, 22),
            },
            "gaming": {
                "system_id": "CH_003",
                "title": "Game Zone",
                "subscribers": 231500,
                "creation_date": date(2021, 1, 10),
            },
        }

        self.fake_content = {
            "video_fdasfdgfs": {
                "system_id": "VID_001",
                "title": "New Smartphone Review 2024",
                "views": 125000,
                "publish_date": date(2024, 1, 15),
            },
            "image_abc123": {
                "system_id": "IMG_001",
                "title": "Sunset Landscape Photography",
                "views": 8700,
                "publish_date": date(2023, 12, 5),
            },
            "text_xyz789": {
                "system_id": "TXT_001",
                "title": "Machine Learning Trends",
                "views": 4300,
                "publish_date": date(2024, 2, 20),
            },
            "audio_sound123": {
                "system_id": "AUD_001",
                "title": "Morning Meditation",
                "views": 15600,
                "publish_date": date(2023, 11, 30),
            },
        }

        self.random_titles = [
            "Awesome Content",
            "Daily Update",
            "Special Edition",
            "Behind the Scenes",
            "Exclusive Interview",
            "Tutorial Guide",
            "News Update",
            "Community Spotlight",
            "Weekly Recap",
        ]

    @staticmethod
    def _extract_content_id(url: str) -> Union[str, None]:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "content_id" in query_params:
            return query_params["content_id"][0]
        path = parsed_url.path.strip("/")
        if path:
            return path
        return None

    def _generate_fake_container_data(self, channel_code: str) -> dict:
        if channel_code in self.fake_containers:
            return self.fake_containers[channel_code]
        return {
            "system_id": f"CH_{random.randint(100, 999):03d}",
            "title": random.choice(self.random_titles),
            "subscribers": random.randint(100, 1000000),
            "creation_date": date.today() - timedelta(days=random.randint(30, 365 * 3)),
        }

    def _generate_fake_content_data(self, content_id: str) -> dict:
        for key, data in self.fake_content.items():
            if content_id.startswith(key.split("_")[0]):
                return data
        if content_id.startswith("video_"):
            content_type = "video"
            base_views = random.randint(50000, 500000)
        else:
            content_type = "unknown"
            base_views = random.randint(100, 10000)
        return {
            "system_id": f"{content_type[:3].upper()}_{random.randint(100, 999):03d}",
            "title": f"{content_type.capitalize()} - {random.choice(self.random_titles)}",
            "views": base_views + random.randint(-base_views // 10, base_views // 10),
            "publish_date": date.today() - timedelta(days=random.randint(1, 90)),
        }

    def get_statistics(self, answers_analysis: AnswersAnalysis) -> AnswersStatistics:
        if not answers_analysis:
            raise DenialSynchronousServiceException(self.__class__)
        content_id = self._extract_content_id(answers_analysis.url)
        if answers_analysis.type_content in ["channel", "homepage"]:
            channel_code = content_id if content_id else "home"
            fake_data = self._generate_fake_container_data(channel_code)
            return AnswersSocialContainer(
                system_id=fake_data["system_id"],
                title=fake_data["title"],
                subscribers=fake_data["subscribers"],
                creation_date=fake_data["creation_date"],
                analysis_status=answers_analysis,
            )
        else:
            if not content_id:
                content_id = f"{answers_analysis.type_content}_generated_{random.randint(1000, 9999)}"
            fake_data = self._generate_fake_content_data(content_id)
            return AnswersSocialContent(
                system_id=fake_data["system_id"],
                title=fake_data["title"],
                views=fake_data["views"],
                publish_date=fake_data["publish_date"],
                analysis_status=answers_analysis,
            )

    async def get_statistics_async(
        self, answers_analysis: AnswersAnalysis
    ) -> AnswersStatistics:
        if not answers_analysis:
            raise DenialAsynchronousServiceException(self.__class__)
        import asyncio

        await asyncio.sleep(0.1)
        return self.get_statistics(answers_analysis)


def test_fake_stat_container_sync():
    fake_stat = FakeStat()
    analysis = AnswersAnalysis(
        url="https://fakesocialmedia.com/qsgqsdrr",
        social_platform="FakeSocialMedia",
        type_content="channel",
    )

    result = fake_stat.get_statistics(analysis)

    assert result.analysis_status.url == "https://fakesocialmedia.com/qsgqsdrr"
    assert result.analysis_status.social_platform == "FakeSocialMedia"
    assert result.analysis_status.type_content == "channel"
    assert isinstance(result, AnswersSocialContainer)
    assert result.system_id == "CH_001"
    assert result.title == "Tech Reviews Channel"
    assert result.subscribers == 15400
    assert result.creation_date == date(2020, 3, 15)
