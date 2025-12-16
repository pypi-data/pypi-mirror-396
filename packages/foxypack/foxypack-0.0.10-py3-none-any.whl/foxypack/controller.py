from typing_extensions import Self

from foxypack.exceptions import DenialAnalyticsException, InternalCollectionException
from foxypack.foxypack_abc.foxyanalysis import FoxyAnalysis
from foxypack.foxypack_abc.foxystat import FoxyStat
from foxypack.foxypack_abc.answers import AnswersAnalysis, AnswersStatistics


class FoxyPack:
    def __init__(
        self,
        queue_foxy_analysis: list[FoxyAnalysis] | None = None,
        queue_foxy_stat: list[FoxyStat] | None = None,
    ) -> None:
        self._queue_foxy_analysis = queue_foxy_analysis or []
        self._queue_foxy_stat = queue_foxy_stat or []

    def with_foxy_analysis(self, foxy_analysis: FoxyAnalysis) -> "Self":
        self._queue_foxy_analysis.append(foxy_analysis)
        return self

    def with_foxy_stat(self, foxy_stat: FoxyStat) -> "Self":
        self._queue_foxy_stat.append(foxy_stat)
        return self

    def get_analysis(self, url: str) -> AnswersAnalysis | None:
        for foxy_analysis in self._queue_foxy_analysis:
            try:
                result_analysis = foxy_analysis.get_analysis(url=url)
            except DenialAnalyticsException:
                continue
            return result_analysis
        return None

    def get_statistics(self, url: str) -> AnswersStatistics | None:
        answers_analysis = self.get_analysis(url)
        if answers_analysis is None:
            return None
        for foxy_stat in self._queue_foxy_stat:
            try:
                result_analysis = foxy_stat.get_statistics(
                    answers_analysis=answers_analysis
                )
                return result_analysis
            except InternalCollectionException:
                continue
        return None

    async def get_statistics_async(self, url: str) -> AnswersStatistics | None:
        answers_analysis = self.get_analysis(url)
        if answers_analysis is None:
            return None
        for foxy_stat in self._queue_foxy_stat:
            try:
                result_analysis = await foxy_stat.get_statistics_async(
                    answers_analysis=answers_analysis
                )
                return result_analysis
            except InternalCollectionException:
                continue
        return None
