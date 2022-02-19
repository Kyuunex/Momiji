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
        'discord.py[voice]==1.7.3',
        'mutagen',
        'psutil',
        'youtube_dl',
        'aiosqlite',
        'feedparser',
        'python-minesweeper',
        'python-dateutil',
        'appdirs',
        'colorama',
        'aiohttp',
        'aiocovidapi @ git+https://github.com/Kyuunex/aiocovidapi.git@0.1.0',
    ],
)
