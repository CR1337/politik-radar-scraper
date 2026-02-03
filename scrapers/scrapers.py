from scrapers.scraper import Scraper
from typing import Dict
from scrapers.hib_scraper import HibScraper
from scrapers.nkr_scraper import NkrScraper
from scrapers.bfdi_scraper import BfdiScraper
from scrapers.bva_scraper import BvaScraper
from scrapers.dsc_scraper import DscScraper
from scrapers.bsi_scraper import BsiScraper
from scrapers.bna_scraper import BnaScraper
from scrapers.diw_scraper import DiwScraper
from scrapers.bmds_scraper import BmdsScraper


ALL_SCRAPERS: Dict[str, Scraper] = {
    "Heute im Bundestag": HibScraper(),
    "Normenkontrollrat": NkrScraper(),
    "BfDI": BfdiScraper(),
    "BVA": BvaScraper(),
    "DSC": DscScraper(),
    "BSI": BsiScraper(),
    "BNA": BnaScraper(),
    "DIW": DiwScraper(),
    "BMDS": BmdsScraper()
}
