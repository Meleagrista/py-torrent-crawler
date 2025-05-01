import asyncio
import libtorrent as lt

from rich.live import Live
from rich.progress import Progress, TextColumn, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.spinner import Spinner
from rich.text import Text
from torrentp import Downloader, TorrentDownloader, TorrentInfo

from src.core.cli import console


class DownloaderWrapper(Downloader):
    async def download(self):
        await self.get_size_info(self.status().total_wanted)

        with Progress(
                TextColumn("{task.fields[status]}"),
                SpinnerColumn(),
                BarColumn(complete_style="green"),
                TextColumn("{task.completed}%", style="progress.completed"),
                TimeElapsedColumn(),
                TextColumn("{task.fields[download]} Kb/s", style="dim"),
                TextColumn("{task.fields[peers]} peers", style='dim'),
                console=console,
                transient=True,
        ) as progress:
            fields = {'percentage': 0, 'status': 'Starting', 'peers': 0, 'download': 0, 'upload': 0}
            task = progress.add_task("Downloading movie", total=100, **fields)

            while not self._status.is_seeding:
                if not self._paused:
                    fields = self._get_status_progress(self.status())
                    progress.update(task, completed=fields['percentage'], **fields)
                await asyncio.sleep(1)

        if self._stop_after_download:
            self.stop()
        else:
            with Live(console=console, transient=False) as live:
                live.update(Text(f"Downloaded successfully!", style='green'))
                await asyncio.sleep(2)

    def _get_status_progress(self, s):
        fields = {
            'percentage': round(s.progress * 100),
            'status': str(s.state).capitalize() if s.num_peers > 0 else 'Seeding',
            'peers': s.num_peers,
            'download': round(s.download_rate / 1000, 2),
            "upload": round(s.upload_rate / 1000, 2)
        }

        return fields

    async def get_size_info(self, byte_length):
        with Live(console=console, transient=True) as live:
            live.update(Spinner(name='dots', text="Getting file info...", style='green'))
            await asyncio.sleep(2)

            if not self._is_magnet:
                _file_size = byte_length / 1000
                _size_info = 'Size: %.2f ' % _file_size
                _size_info += 'MB' if _file_size > 1000 else 'KB'
                live.update(Text(f"The file has a size of {_size_info}", style='green'))
                await asyncio.sleep(2)

            if self.status().name:
                live.update(Text(f"Saving as '{self.status().name}'...", style='green'))
                await asyncio.sleep(2)

    # def pause(self):
    #     console.print("[yellow]Pausing download..[/yellow]")
    #     self.pause()
    #     console.print("[yellow]Download paused successfully.[/yellow]")

    # def resume(self):
    #     console.print("[yellow]Resuming download..[/yellow]")
    #     self.resume()
    #     console.print("[yellow]Download resumed successfully.[/yellow]")

    # def stop(self):
    #     console.print("[red]Stopping download..[/red]")
    #     self.stop()
    #     console.print("[red]Download stopped successfully.[/red]")

class TorrentDownloaderWrapper(TorrentDownloader):

    async def start_download(self, download_speed=0, upload_speed=0):
        if self._file_path.startswith('magnet:'):
            self._add_torrent_params = self._lt.parse_magnet_uri(self._file_path)
            self._add_torrent_params.save_path = self._save_path
            self._downloader = DownloaderWrapper(
                session=self._session(), torrent_info=self._add_torrent_params,
                save_path=self._save_path, libtorrent=lt, is_magnet=True, stop_after_download=self._stop_after_download
            )

        else:
            self._torrent_info = TorrentInfo(self._file_path, self._lt)
            self._downloader = DownloaderWrapper(
                session=self._session(), torrent_info=self._torrent_info(),
                save_path=self._save_path, libtorrent=None, is_magnet=False, stop_after_download=self._stop_after_download
            )

        self._session.set_download_limit(download_speed)
        self._session.set_upload_limit(upload_speed)

        self._file = self._downloader
        await self._file.download()