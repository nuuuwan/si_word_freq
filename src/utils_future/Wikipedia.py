import os
from functools import cache, cached_property

import wikipedia
from utils import File, Log, Parallel

log = Log('Wikipedia')


class Wikipedia:
    def __init__(self, lang: str):
        self.lang = lang

    def __str__(self):
        return f"<Wikipedia {self.lang}>"

    @property
    def dir_pages_path(self) -> str:
        return os.path.join('data', self.lang, 'pages')

    @cached_property
    def n_pages(self) -> int:
        if not os.path.exists(self.dir_pages_path):
            return 0
        return len(os.listdir(self.dir_pages_path))

    @cached_property
    def page_content_list(self) -> list[str]:
        page_content_list = []
        for page_name in os.listdir(self.dir_pages_path):
            page_file = File(os.path.join(self.dir_pages_path, page_name))
            page_content_list.append(page_file.read())
        return page_content_list

    @staticmethod
    def download_random_page(dir_pages_path) -> str:
        title = wikipedia.random()
        try:
            page = wikipedia.page(title)
            page_file_path = os.path.join(dir_pages_path, f'{title}.txt')
            if os.path.exists(page_file_path):
                log.warning(f"Skipping {title}. Already downloaded.")
                return None

            page_content = page.content
            page_file = File(page_file_path)
            page_file.write(page_content)

            return page_file_path
        except Exception as e:
            log.error(f"Skipping {title}. Error: {e}")

        return None

    def download_pages(self, n: int):
        log.debug(f'download_pages({n=:,})')
        os.makedirs(self.dir_pages_path, exist_ok=True)
        wikipedia.set_lang(self.lang)

        workers = []
        for i in range(0, n):

            def worker(i=i, n=n):
                page_file_path = Wikipedia.download_random_page(
                    self.dir_pages_path
                )
                if page_file_path:
                    log.debug(f'{i+1}/{n}) {page_file_path}')

            workers.append(worker)

        Parallel.run(workers, max_threads=16)

    @cache
    def get_page_content(self, limit: int) -> str:
        log.debug(f'n_pages={self.n_pages}')
        if self.n_pages < limit:
            self.download_pages(limit - self.n_pages)
        return '\n\n'.join(self.page_content_list)
