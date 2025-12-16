## [1.1.0] - 2025-12-04
### Added
- CHANGELOG.md for better logging profile on each update.
- New feature: QR Code Generator. Use the `{qrcode}` command followed by any text 
or URL to instantly generate and display a QR code in the terminal.
- Added the `qrcode` package as a dependency.

## [1.1.0.1] - 2025-12-4
### Fixes
- README.md for better user experience.

## [1.1.0.2] - 2025-12-5
### Fixes
- Memory optimization for devices with lower memory.
- Fixed setup.py by adding packages 
- ```bash
  extras_require={
        'transcribe': [
            'openai-whisper',
            'numpy'
        ],
        'media': ['pygame']
    },``` 
in extra, so the user will download it as per his recommendation.

## [1.2.0.2] - 2025-12-5
### Fixes
- Major CLI update. Now the user will not
see logging information at every search or at the start of the program.

## [1.3.0.2] - 2025-12-10
### Fixes
- Optimize config.json for better script performance.

## [1.4.2.2] - 2025-12-11
### Added
- New Search filters for specific searches. For example.
- ```bash
  Search Filters: {wiki}, {code}, {news}, {youtube} (e.g., {code} python sort list)```

## [1.4.2.3] - 2025-12-11
### Fixes
- Fixed the display of the version in the banner.
