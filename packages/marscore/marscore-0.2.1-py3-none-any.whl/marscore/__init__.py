# marscore/__init__.py
from .downloader.downloader import MultiThreadDownloader
from .recap.downloader import MultiParquetDownloader

class UnifiedDownloader:
    def __call__(self, urls, *args, **kwargs):
        return MultiThreadDownloader().run(urls, *args, **kwargs)

    def recap(self, urls, *args, **kwargs):
        return MultiParquetDownloader().run(urls, *args, **kwargs)



# 创建统一下载器实例
downloader = UnifiedDownloader()

__all__ = ['MultiThreadDownloader', 'MultiParquetDownloader', 'downloader', 'UnifiedDownloader']