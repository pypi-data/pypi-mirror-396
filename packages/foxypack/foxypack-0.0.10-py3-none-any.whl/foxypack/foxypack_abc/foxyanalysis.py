from abc import ABC, abstractmethod

from foxypack.exceptions import DenialAnalyticsException
from foxypack.foxypack_abc.answers import AnswersAnalysis


class FoxyAnalysis(ABC):
    @abstractmethod
    def get_analysis(self, url: str) -> AnswersAnalysis:
        raise DenialAnalyticsException(url)
