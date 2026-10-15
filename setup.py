from setuptools import setup

from momiji.manifest import VERSION

setup(
    name='momiji',
    packages=[
        'momiji',
        'momiji.apiwrappers',
        'momiji.cogs',
        'momiji.embeds',
        'momiji.modules',
        'momiji.reusables'
    ],
    version=VERSION,
    description='The only Discord bot you\'ll ever need',
    author='qnx',
    author_email='me@qnx.sh',
    url='https://github.com/qnxt/Momiji',
    install_requires=[
        'discord.py[voice]==2.7.1',
        'mutagen',
        'psutil',
        'yt-dlp',
        'aiosqlite',
        'feedparser',
        'python-minesweeper',
        'python-dateutil',
        'appdirs',
        'colorama',
        'aiohttp',
    ],
)
