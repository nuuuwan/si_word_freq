import os
import re
from functools import cached_property

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.font_manager import FontProperties
from utils import Log

from utils_future import Wikipedia

log = Log('LetterFrequency')

# fonts
FONT_PATH = os.path.join('fonts', 'Nirmala.ttf')
FONT = FontProperties(fname=FONT_PATH)
plt.rcParams['font.family'] = FONT.get_name()


class LetterFrequency:
    def __init__(self, lang: str, n_pages: int):
        self.lang = lang
        self.n_pages = n_pages

    @cached_property
    def wikipedia(self) -> Wikipedia:
        return Wikipedia(self.lang)

    @cached_property
    def content(self) -> str:
        return self.wikipedia.get_page_content(self.n_pages)

    @cached_property
    def words(self) -> list[str]:
        return self.content.split(' ')

    @cached_property
    def n_words(self) -> int:
        return len(self.words)

    @cached_property
    def chars(self) -> list[str]:
        chars = []
        for word in self.words:
            for c in word:
                if self.is_si(c):
                    chars.append(c)
        return chars

    @cached_property
    def n_chars(self) -> int:
        return len(self.chars)

    @staticmethod
    def is_si(char) -> bool:
        return re.match(r'[\u0D80-\u0DFF]', char)

    @cached_property
    def c_to_n(self) -> dict[str, int]:
        c_to_n = {}
        for c in self.chars:
            c_to_n[c] = c_to_n.get(c, 0) + 1
        c_to_n = dict(
            sorted(c_to_n.items(), key=lambda x: x[1], reverse=True)
        )
        return c_to_n

    @cached_property
    def title(self):
        return f"Letter frequency analysis for {self.lang}"

    @cached_property
    def subtitle(self):
        return (
            f'Based on {self.n_chars:,} chars ({self.n_words:,} words)'
            + f' from {self.n_pages:,} random {self.wikipedia} articles'
        )

    def analyze(self):
        # pre-cache
        self.c_to_n
        n_total = self.n_chars

        log.debug('-' * 32)

        log.info(self.title)

        log.info(self.subtitle)
        log.debug('-' * 32)

        for i, (c, n) in enumerate(list(self.c_to_n.items())):
            p = n / n_total
            log.info(
                f'{i+1})'.rjust(6) + f"{c}".rjust(6) + f'{p:.2%}'.rjust(12)
            )

        log.debug('-' * 32)

    def draw_chart(
        self,
    ):
        c_and_n_display = list(self.c_to_n.items())
        n_total = self.n_chars
        n = len(c_and_n_display)

        # draw
        n_row = 2
        width = 12
        height = width * 9 / 16
        fig, axs = plt.subplots(n_row, 1, figsize=(width, height))
        fig.suptitle(
            self.title,
            fontsize=24,
        )
        plt.figtext(
            0.5,
            0.01,
            self.subtitle,
            fontsize=12,
            ha='center',
        )

        items_per_row = n // n_row
        for i, ax in enumerate(axs):
            c_and_n_display_for_row = c_and_n_display[
                i * items_per_row: (i + 1) * items_per_row
            ]
            x = [c for c, _ in c_and_n_display_for_row]
            y = [n for _, n in c_and_n_display_for_row]

            ax.bar(
                x,
                y,
            )
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(n_total))

        # save
        os.makedirs('charts', exist_ok=True)
        chart_path = os.path.join(
            'charts',
            f'letter_frequency-{self.lang}-{self.n_pages}.png',
        )

        plt.savefig(chart_path, dpi=300)
        log.info(f'Wrote {chart_path}')
