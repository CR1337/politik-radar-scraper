from scrapers.scraper import Scraper
from typing import Dict
from scrapers.hib_scraper import HibScraper
from scrapers.hib_rss_scraper import HibRssScraper
from scrapers.nkr_scraper import NkrScraper
from scrapers.bfdi_scraper import BfdiScraper
from scrapers.bfdi_rss_scraper import BfdiRssScraper
from scrapers.bva_scraper import BvaScraper
from scrapers.bva_rss_scraper import BvaRssScraper
from scrapers.dsc_scraper import DscScraper
from scrapers.bsi_scraper import BsiScraper
from scrapers.bsi_rss_scraper import BsiRssScraper
from scrapers.bna_scraper import BnaScraper
from scrapers.diw_scraper import DiwScraper
from scrapers.diw_rss_scraper import DiwRssScraper
from scrapers.bmds_scraper import BmdsScraper
from scrapers.bmi_scraper import BmiScraper
from scrapers.bmi_rss_scraper import BmiRssScraper
from scrapers.bmwe_scraper import BmweScraper
from scrapers.bmwe_rss_scraper import BmweRssScraper
from scrapers.bmas_scraper import BmasScraper
from scrapers.bmas_rss_scraper import BmasRssScraper
from scrapers.breg_scraper import BregScraper
from scrapers.breg_rss_scraper import BregRssScraper
from scrapers.bmf_scraper import BmfScraper
from scrapers.bmf_rss_scraper import BmfRssScraper
from scrapers.bmbfsfj_scraper import BmbfsfjScraper
from scrapers.bmbfsfj_rss_scraper import BmbfsfjRssScraper
from scrapers.bmjv_scraper import BmjvScraper
from scrapers.bmjv_rss_scraper import BmjvRssScraper
from scrapers.bmftr_scraper import BmftrScraper
from scrapers.bmftr_rss_scraper import BmftrRssScraper
from scrapers.bmv_scraper import BmvScraper
from scrapers.bmukn_scraper import BmuknScraper
from scrapers.bmukn_rss_scraper import BmuknRssScraper
from scrapers.google_scraper import GoogleScraper
from scrapers.bmvg_scraper import BmvgScraper
from scrapers.bmg_scraper import BmgScraper
from scrapers.bmleh_scraper import BmlehScraper
from scrapers.bmz_scraper import BmzScraper
from scrapers.bmwsb_scraper import BmwsbScraper
from scrapers.aa_scraper import AaScraper
from scrapers.netzpolitik_rss_scraper import NetzpolitikRssScraper
from scrapers.heise_rss_scraper import HeiseRssScraper
from scrapers.eu_parlament_rss_scraper import EuParlamentRssScraper
from scrapers.data_europa_scraper import DataEuropaScraper
from scrapers.eu_digital_strategy_scraper import EuDigitalStrategy
from scrapers.eu_kommission_scraper import EuKommissionScraper
from scrapers.tagesspiegel_background_scraper import TagesspiegelBackgroundScraper



ALL_SCRAPERS: Dict[str, Scraper] = {
    "Heute im Bundestag": HibRssScraper(),
    "Normenkontrollrat": NkrScraper(),
    "BfDI": BfdiRssScraper(),
    "BVA": BvaRssScraper(),
    "DSC": DscScraper(),
    "BSI": BsiRssScraper(),
    "BNA": BnaScraper(),
    "DIW": DiwRssScraper(),
    "BMDS": BmdsScraper(),
    "BMI": BmiScraper(),
    "BMWE": BmweRssScraper(),
    "BMAS": BmasRssScraper(),
    "BREG": BregRssScraper(),
    "BMF": BmfRssScraper(),
    "BMBFSFJ": BmbfsfjRssScraper(),
    "BMJV": BmjvRssScraper(),
    "BMFTR": BmftrRssScraper(),
    "BMV": BmvScraper(),
    "BMUKN": BmuknRssScraper(),
    "Google News": GoogleScraper(),
    "BMVG": BmvgScraper(),
    "BMG": BmgScraper(),
    "BMLEH": BmlehScraper(),
    "BMZ": BmzScraper(),
    "BMWSB": BmwsbScraper(),
    "AA": AaScraper(),
    "Netzpolitik": NetzpolitikRssScraper(),
    "Heise": HeiseRssScraper(),
    "EU Parlament": EuParlamentRssScraper(),
    "Data.Europa" : DataEuropaScraper(),
    "EU Digital Strategy":EuDigitalStrategy(),
    "EU Kommission":EuKommissionScraper(),
    "Tagesspiegel Background":TagesspiegelBackgroundScraper(),
}

BUNDESMINISTERIEN = [
    "BMDS",
    "BMI",
    "BMWE",
    "BMAS",
    "BMF",
    "BMBFSFJ",
    "BMJV",
    "BMFTR",
    "BMV",
    "BMUKN",
    "BMVG",
    "BMG",
    "BMLEH",
    "BMZ",
    "BMWSB",
    "AA",
    "BREG",
]

PRESSEORGANE = [
    "Google News",
    "Netzpolitik",
    "Heise",
    "Tagesspiegel Background",
]

SONSTIGE_INSTUTIONEN = [
    "Normenkontrollrat",
    "BVA",
    "DSC",
    "BSI",
    "BNA",
    "DIW",
]

BUNDESTAG= [
    "Heute im Bundestag",
]

EUROPA_INTERNATIONAL = [
    "EU Parlament",
    "Data.Europa",
    "EU Digital Strategy",
    "EU Kommission",
]