"""Extract series information from the IMDB web page."""

from __future__ import annotations

from contextlib import suppress
import csv
from importlib import metadata
from pathlib import Path
import re

import click
from rich.console import Console
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .unicodewriter import UnicodeWriter

EPISODE_HEADER = re.compile(r"Season (?P<season>\d+), Episode (?P<episode>\d+):")
CONSOLE = Console()


class IMDBEntry:
    """Handle IMDB episodes information for TV series."""

    line = 2
    TITLE_MATCH = re.compile(r"S(?P<season>\d+)\.\s*E(?P<episode>\d+) ∙ (?P<title>.+)")

    def __init__(self, season: int, href_text: str, href: str, desc: str):
        """Initialize class instance."""
        self.season = season
        _match = self.TITLE_MATCH.match(href_text)
        if _match is None:
            msg = "Season info not found."
            raise ValueError(msg)
        if int(_match.group("season")) != self.season:
            msg = "Current season does not fit html data."
            raise ValueError(msg)
        self.episode = int(_match.group("episode"))
        self.title = _match.group("title")
        self.url = href
        self.url = self.url[: self.url.rfind("?")]
        self.descr = desc

    def list(self) -> tuple:
        """Return information list."""
        IMDBEntry.line += 1
        return (
            None,
            self.season,
            self.episode,
            None,
            None,
            None,
            f'=HYPERLINK("{self.url}";"{self.title}")',
            self.descr,
            f"=WENN(ODER(ISTLEER(F{IMDBEntry.line});"
            f'ISTLEER(A{IMDBEntry.line}));"";'
            f"SVERWEIS(F{IMDBEntry.line};F$3:J$10000;5;0)/"
            f"SUMMENPRODUKT(((A$3:A$10000)>0)*((F$3:F$10000)="
            f"F{IMDBEntry.line})))",
        )

    def __lt__(self, other: object) -> bool:
        """Return if instance less than or equal other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode < other.episode

    def __le__(self, other: object) -> bool:
        """Return if instance less than other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode <= other.episode

    def __eq__(self, other: object) -> bool:
        """Return if instance is equal other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode == other.episode

    def __hash__(self) -> int:
        """Return hash value for class instance."""
        return hash(self.episode)

    def __ne__(self, other: object) -> bool:
        """Return if instance is not equal other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode != other.episode

    def __gt__(self, other: object) -> bool:
        """Return if instance is greater than other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode > other.episode

    def __ge__(self, other: object) -> bool:
        """Return if instance is greater or equal than other."""
        if not isinstance(other, IMDBEntry):
            raise TypeError
        return self.episode >= other.episode


class IMDBInfo:
    """Process html page from IMDB."""

    def __init__(self, url: str, title: str, language: str):
        """Initialize instance."""
        self.url = self.get_url(url)
        self.title = title
        self.language = language

        options = Options()
        options.add_argument("--headless")
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference(key="intl.accept_languages", value=self.language)
        firefox_profile.set_preference(key="javascript.enabled", value=True)
        options.profile = firefox_profile
        self.driver = webdriver.Firefox(options=options)

        self.series = " ".join(title)

        if len(self.series) == 0:
            self.series = self.get_series()

        self.driver.get(self.url)

    def __del__(self) -> None:
        """Cleuup."""
        self.driver.quit()

    def get_url(self, url: Path | str) -> str:
        """Return preprocessed URL."""
        path = Path(url)
        res = url
        if path.is_file():
            with path.open() as csvfile:
                inforeader = csv.reader(csvfile)
                res = next(inforeader)[0].split('"')[1]
        if not isinstance(res, str):
            raise TypeError
        while res.endswith("/"):
            res = res[:-1]
        if not res.endswith("/episodes"):
            res += "/episodes"
        return res

    def __call__(self) -> None:
        """Process data."""
        self.process_data()

    def process_data(self) -> None:
        """Generate the csv file."""
        wait = WebDriverWait(self.driver, 10)

        def extract_url(inp: str | None) -> str:
            if inp is None:
                raise ValueError
            res = re.match(r".+season\=(?P<season>(\d+|Unknown))\&?.+", inp)
            if res is None:
                msg = "No season information found."
                raise RuntimeError(msg)
            return res.groupdict()["season"]

        seasons = [
            int(href)
            for i in wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, '//div[contains(@class,"ipc-tabs--display-chip")]')
                )
            ).find_elements(
                By.XPATH, '//div[contains(@class,"ipc-tabs--display-chip")]//a'
            )
            if (href := extract_url(i.get_attribute("href"))) and href.isdigit()
        ]

        tbl = "".maketrans("/", "_")
        with Path(f"{self.series.strip().translate(tbl)}.csv").open("w") as filep:
            writer = UnicodeWriter(filep, delimiter=";", quoting=csv.QUOTE_MINIMAL)

            writer.writerow(
                [f'=HYPERLINK("{self.url.strip()[:-9]}";"{self.series.strip()}")']
            )
            writer.writerow(
                [
                    '=HYPERLINK("#Übersicht";"Datum")',
                    None,
                    None,
                    "Disk",
                    "Index",
                    "Diskset",
                    "IMDB URL",
                    None,
                    "=MITTELWERT(I3:I10000)",
                    "=SUMME(J3:J10000)",
                ]
            )

            for season in seasons:
                self.driver.get(f"{self.url}/?season={season}")
                wait = WebDriverWait(self.driver, 10)

                CONSOLE.print(f"Season {season}")

                elem = wait.until(
                    ec.element_to_be_clickable(
                        (
                            By.XPATH,
                            '//article[contains(@class,"episode-item-wrapper")]',
                        )
                    )
                )
                articles = elem.find_elements(
                    By.XPATH,
                    '//article[contains(@class,"episode-item-wrapper")]',
                )

                episodes = []

                for article in articles:
                    description_ = article.find_elements(
                        By.XPATH, './/div[@class="ipc-html-content-inner-div"]'
                    )
                    description = description_[0].text if description_ else ""
                    link = article.find_element(
                        By.XPATH, './/a[@class="ipc-title-link-wrapper"]'
                    )
                    href_ = link.get_attribute("href")
                    if not isinstance(href_, str):
                        raise TypeError
                    episodes.append(IMDBEntry(season, link.text, href_, description))

                episodes.sort()

                for i in episodes:
                    writer.writerow(
                        [j.strip() if isinstance(j, str) else j for j in i.list()]
                    )

    def get_series(self) -> str:
        """Get Series title."""
        url = self.url[:-9]
        driver = self.driver
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wrapper = wait.until(ec.presence_of_element_located((By.TAG_NAME, "h1")))
        res = wrapper.find_element(
            By.XPATH, '//h1[contains(@data-testid, "hero__pageTitle")]'
        ).text
        with suppress(Exception):
            res = wrapper.find_element(
                By.XPATH,
                '//div[contains(@data-testid, "hero-title-block__original-title")]',
            ).text.strip()
            res = res.removesuffix(" (original title)")
            res = res.removeprefix("Original title: ")
            res = res.removeprefix("Originaltitel: ")
        return res.strip()


@click.command()
@click.argument("url", type=str, nargs=1)
@click.argument("title", type=str, nargs=-1)
@click.option(
    "-l",
    "--language",
    type=str,
    default="en",
    help="Language to use for download, default: %(default)s",
)
@click.version_option(version=f"{metadata.version('imdb_extract')}")
def imdb_extract(url: str, title: str, language: str) -> None:
    """Extract IMDB information for TV series.

    Generates file <Title>.csv.  If existing CSV file is given as
    argument, URL is read from previously generated CSV file.

    URL: URL string / existing CSV file.

    TITLE: title string
    """
    prog = IMDBInfo(url, title, language)

    CONSOLE.print(f"URL   : {url}")
    CONSOLE.print(f"series: {title}")

    prog()

    raise SystemExit


if __name__ == "__main__":
    imdb_extract()
