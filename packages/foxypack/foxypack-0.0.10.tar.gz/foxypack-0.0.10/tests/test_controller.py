from datetime import date

import pytest

from foxypack import FoxyPack, InternalCollectionException, DenialAnalyticsException
from foxypack.foxypack_abc.answers import AnswersSocialContent, AnswersSocialContainer
from tests.foxypack_abc.test_foxyanalysis import FakeAnalysis
from tests.foxypack_abc.test_foxystat import FakeStat


def test_foxypack_with_analysis():
    """Test case verifies adding FoxyAnalysis analyzer to FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis())

    assert len(foxypack._queue_foxy_analysis) == 1
    assert isinstance(foxypack._queue_foxy_analysis[0], FakeAnalysis)
    assert len(foxypack._queue_foxy_stat) == 0


def test_foxypack_with_stat():
    """Test case verifies adding FoxyStat statistics to FoxyPack"""
    foxypack = FoxyPack().with_foxy_stat(FakeStat())

    assert len(foxypack._queue_foxy_stat) == 1
    assert isinstance(foxypack._queue_foxy_stat[0], FakeStat)
    assert len(foxypack._queue_foxy_analysis) == 0


def test_foxypack_with_both():
    """Test case verifies adding both analyzer and statistics to FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())

    assert len(foxypack._queue_foxy_analysis) == 1
    assert len(foxypack._queue_foxy_stat) == 1
    assert isinstance(foxypack._queue_foxy_analysis[0], FakeAnalysis)
    assert isinstance(foxypack._queue_foxy_stat[0], FakeStat)


def test_foxypack_chain_multiple():
    """Test case verifies chaining addition of multiple analyzers"""
    foxypack = (
        FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_analysis(FakeAnalysis())
    )

    assert len(foxypack._queue_foxy_analysis) == 2
    assert len(foxypack._queue_foxy_stat) == 0


def test_foxypack_get_analysis_channel():
    """Test case verifies getting analysis for a channel through FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis())
    analysis = foxypack.get_analysis("https://fakesocialmedia.com/qsgqsdrr")

    assert analysis is not None
    assert analysis.url == "https://fakesocialmedia.com/qsgqsdrr"
    assert analysis.social_platform == "FakeSocialMedia"
    assert analysis.type_content == "channel"


def test_foxypack_get_analysis_video():
    """Test case verifies getting analysis for video content through FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis())
    analysis = foxypack.get_analysis(
        "https://fakesocialmedia.com/qsgqsdr?content_id=video_fdasfdgfs"
    )

    assert analysis is not None
    assert (
        analysis.url == "https://fakesocialmedia.com/qsgqsdr?content_id=video_fdasfdgfs"
    )
    assert analysis.social_platform == "FakeSocialMedia"
    assert analysis.type_content == "video"


def test_foxypack_get_analysis_invalid_url():
    """Test case verifies handling of invalid URL through FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis())
    analysis = foxypack.get_analysis(
        "https://invalidmedia.com/qsgqsdr?content_id=video_fdasfdgfs"
    )

    assert analysis is None


def test_foxypack_get_analysis_no_analyzers():
    """Test case verifies behavior of FoxyPack without analyzers"""
    foxypack = FoxyPack()
    analysis = foxypack.get_analysis("https://fakesocialmedia.com/qsgqsdrr")

    assert analysis is None


def test_foxypack_get_analysis_multiple_analyzers_first_success():
    """Test case verifies analyzer chain operation where the first one fails and the second succeeds"""

    class FailingFakeAnalysis(FakeAnalysis):
        def get_analysis(self, url: str):
            raise DenialAnalyticsException(url)

    foxypack = (
        FoxyPack()
        .with_foxy_analysis(FailingFakeAnalysis())
        .with_foxy_analysis(FakeAnalysis())
    )
    analysis = foxypack.get_analysis("https://fakesocialmedia.com/qsgqsdrr")

    assert analysis is not None
    assert analysis.url == "https://fakesocialmedia.com/qsgqsdrr"
    assert analysis.social_platform == "FakeSocialMedia"
    assert analysis.type_content == "channel"


def test_foxypack_get_analysis_multiple_analyzers_all_fail():
    """Test case verifies analyzer chain operation where all analyzers fail"""

    class FailingFakeAnalysis(FakeAnalysis):
        def get_analysis(self, url: str):
            raise DenialAnalyticsException(url)

    foxypack = (
        FoxyPack()
        .with_foxy_analysis(FailingFakeAnalysis())
        .with_foxy_analysis(FailingFakeAnalysis())
    )
    analysis = foxypack.get_analysis("https://fakesocialmedia.com/qsgqsdrr")

    assert analysis is None


def test_foxypack_get_statistics_full_flow():
    """Test case verifies the full workflow of FoxyPack: analysis + statistics for channel"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = foxypack.get_statistics("https://fakesocialmedia.com/qsgqsdrr")

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContainer)
    assert statistics.system_id == "CH_001"
    assert statistics.title == "Tech Reviews Channel"
    assert statistics.subscribers == 15400
    assert statistics.creation_date == date(2020, 3, 15)


def test_foxypack_get_statistics_video_content():
    """Test case verifies the full workflow of FoxyPack: analysis + statistics for video"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = foxypack.get_statistics(
        "https://fakesocialmedia.com/qsgqsdr?content_id=video_fdasfdgfs"
    )

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContent)
    assert statistics.system_id == "VID_001"
    assert statistics.title == "New Smartphone Review 2024"
    assert statistics.views == 125000
    assert statistics.publish_date == date(2024, 1, 15)


def test_foxypack_get_statistics_no_analysis():
    """Test case verifies getting statistics without analyzers in FoxyPack"""
    foxypack = FoxyPack().with_foxy_stat(FakeStat())
    statistics = foxypack.get_statistics("https://fakesocialmedia.com/qsgqsdrr")

    assert statistics is None


def test_foxypack_get_statistics_no_stats():
    """Test case verifies getting statistics without statistical handlers in FoxyPack"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis())
    statistics = foxypack.get_statistics("https://fakesocialmedia.com/qsgqsdrr")

    assert statistics is None


def test_foxypack_get_statistics_invalid_url():
    """Test case verifies handling of invalid URL when getting statistics"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = foxypack.get_statistics("https://invalidmedia.com/qsgqsdrr")

    assert statistics is None


def test_foxypack_get_statistics_multiple_stats_first_success():
    """Test case verifies the operation of the statistical handler chain in FoxyPack"""

    class FailingFakeStat(FakeStat):
        def get_statistics(self, answers_analysis):
            raise InternalCollectionException()

    foxypack = (
        FoxyPack()
        .with_foxy_analysis(FakeAnalysis())
        .with_foxy_stat(FailingFakeStat())
        .with_foxy_stat(FakeStat())
    )
    statistics = foxypack.get_statistics("https://fakesocialmedia.com/qsgqsdrr")

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContainer)
    assert statistics.system_id == "CH_001"


def test_foxypack_get_statistics_multiple_stats_all_fail():
    """Test case verifies FoxyPack operation when all statistical handlers fail"""

    class FailingFakeStat(FakeStat):
        def get_statistics(self, answers_analysis):
            raise InternalCollectionException()

    foxypack = (
        FoxyPack()
        .with_foxy_analysis(FakeAnalysis())
        .with_foxy_stat(FailingFakeStat())
        .with_foxy_stat(FailingFakeStat())
    )
    statistics = foxypack.get_statistics("https://fakesocialmedia.com/qsgqsdrr")

    assert statistics is None


@pytest.mark.asyncio
async def test_foxypack_get_statistics_async_full_flow():
    """Test case verifies asynchronous full workflow of FoxyPack for channel"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = await foxypack.get_statistics_async(
        "https://fakesocialmedia.com/qsgqsdrr"
    )

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContainer)
    assert statistics.system_id == "CH_001"
    assert statistics.title == "Tech Reviews Channel"
    assert statistics.subscribers == 15400
    assert statistics.creation_date == date(2020, 3, 15)


@pytest.mark.asyncio
async def test_foxypack_get_statistics_async_video_content():
    """Test case verifies asynchronous full workflow of FoxyPack for video"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = await foxypack.get_statistics_async(
        "https://fakesocialmedia.com/qsgqsdr?content_id=video_fdasfdgfs"
    )

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContent)
    assert statistics.system_id == "VID_001"
    assert statistics.title == "New Smartphone Review 2024"
    assert statistics.views == 125000
    assert statistics.publish_date == date(2024, 1, 15)


@pytest.mark.asyncio
async def test_foxypack_get_statistics_async_no_analysis():
    """Test case verifies asynchronous statistics retrieval without analyzers"""
    foxypack = FoxyPack().with_foxy_stat(FakeStat())
    statistics = await foxypack.get_statistics_async(
        "https://fakesocialmedia.com/qsgqsdrr"
    )

    assert statistics is None


@pytest.mark.asyncio
async def test_foxypack_get_statistics_async_invalid_url():
    """Test case verifies asynchronous handling of invalid URL"""
    foxypack = FoxyPack().with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())
    statistics = await foxypack.get_statistics_async(
        "https://invalidmedia.com/qsgqsdrr"
    )

    assert statistics is None


@pytest.mark.asyncio
async def test_foxypack_get_statistics_async_multiple_stats():
    """Test case verifies asynchronous operation of statistical handler chain"""

    class FailingFakeStat(FakeStat):
        async def get_statistics_async(self, answers_analysis):
            raise InternalCollectionException()

    foxypack = (
        FoxyPack()
        .with_foxy_analysis(FakeAnalysis())
        .with_foxy_stat(FailingFakeStat())
        .with_foxy_stat(FakeStat())
    )
    statistics = await foxypack.get_statistics_async(
        "https://fakesocialmedia.com/qsgqsdrr"
    )

    assert statistics is not None
    assert isinstance(statistics, AnswersSocialContainer)
    assert statistics.system_id == "CH_001"


def test_foxypack_empty_initialization():
    """Test case verifies empty FoxyPack initialization"""
    foxypack = FoxyPack()

    assert foxypack._queue_foxy_analysis == []
    assert foxypack._queue_foxy_stat == []


def test_foxypack_with_initial_queues():
    """Test case verifies FoxyPack initialization with preset queues"""
    initial_analysis = [FakeAnalysis(), FakeAnalysis()]
    initial_stats = [FakeStat()]

    foxypack = FoxyPack(
        queue_foxy_analysis=initial_analysis, queue_foxy_stat=initial_stats
    )

    assert len(foxypack._queue_foxy_analysis) == 2
    assert len(foxypack._queue_foxy_stat) == 1


def test_foxypack_with_initial_queues_and_adding_more():
    """Test case verifies adding new handlers to a preset FoxyPack"""
    initial_analysis = [FakeAnalysis()]
    initial_stats = [FakeStat()]

    foxypack = FoxyPack(
        queue_foxy_analysis=initial_analysis, queue_foxy_stat=initial_stats
    )
    foxypack.with_foxy_analysis(FakeAnalysis()).with_foxy_stat(FakeStat())

    assert len(foxypack._queue_foxy_analysis) == 2
    assert len(foxypack._queue_foxy_stat) == 2
