from setuptools import setup, find_packages

setup(
    name='mr-searcher',  # Use a lowercase, hyphenated name for PyPI
    version='1.4.2.2',
    description='A non-hostile, terminal-based information retrieval utility using DuckDuckGo.',
    long_description=open('README.md', encoding='utf-8').read(),  # Assume you will create a README.md
    long_description_content_type='text/markdown',
    author='Om Shailesh Vetale',
    author_email='omvetale.legend@gmail.com',
    url='https://github.com/YourUsername/MrSearcher',  # Replace with your actual GitHub repo
    license='MIT',  # Assuming you will use the common MIT license
    packages=find_packages(),
    # Define the external Python dependencies
    install_requires=[
        'psutil',
        'pyfiglet',
        'colorama',
        'duckduckgo-search',  # The DDGS class is part of this package
        'autocorrect',  # Assuming 'spellchecker' is a typo and you meant 'autocorrect' or 'pyspellchecker'
        # Note: If 'spellchecker' refers to the 'pyspellchecker' package, use that name.
        # Check your actual package name. Let's assume 'pyspellchecker' is the correct one.
        'pyspellchecker',
        'numpy',
        'yt-dlp',
        'qrcode'
    ],
    extras_require={
        'transcribe': [
            'openai-whisper',
            'numpy'
        ],
        'media': ['pygame']
    },
    # Add external dependencies note for the user
    # Note: yt-dlp and ffmpeg must be installed manually by the user, as they are system binaries.
    keywords='cli search utility duckduckgo terminal',

    # Specify the entry point for the script
    entry_points={
        'console_scripts': [
            'mrsearcher=Mr_Searcher:cli_duck_search',  # <--- Crucial line!
        ],
    },
    # Ensure the script file is included, even if no packages are used
    py_modules=['Mr_Searcher'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)