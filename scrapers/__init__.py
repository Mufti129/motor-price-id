from scrapers.olx_scraper import OLXMotorScraper
try:
    from scrapers.stealth_scraper import StealthMarketplaceScraper
except ImportError:
    StealthMarketplaceScraper = None
