from distutils.core import setup

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
    author='Kyuunex',
    author_email='kyuunex@protonmail.ch',
    url='https://github.com/Kyuunex/Momiji',
    install_requires=[
        'discord.py[voice]',
        'mutagen',
        'psutil',
        'youtube_dl',
        'aiosqlite',
        'feedparser',
        'python-minesweeper',
        'python-dateutil',
        'appdirs',
        'colorama',
        'aiohttp'
    ],
)
