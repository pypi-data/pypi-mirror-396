# foxypack

### Foxy interface library, entity balancing core, and shared parser

### Basic usage

#### Add a module to the FoxyPack controller for analyzing a set of social media links and getting analytics by link

~~~python

from foxypack import FoxyPack
from foxypack_youtube_pytubefix import FoxyYouTubeAnalysis

parser = FoxyPack().with_foxy_analysis(FoxyYouTubeAnalysis())

parser.get_analysis("https://youtu.be/-3eMzaP9XOM")

~~~

#### Add a module to the FoxyPack controller to collect statistics on a set of social media links and getting analytics by link and getting statistics by link by link

~~~python

from foxypack import FoxyPack
from foxypack_youtube_pytubefix import FoxyYouTubeStat

parser = FoxyPack().with_foxy_stat(
    FoxyYouTubeStat()
)

parser.get_statistics("https://youtu.be/-3eMzaP9XOM")

~~~