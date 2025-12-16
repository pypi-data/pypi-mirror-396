# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Metadata-aware search that indexes `{title}`, `{subtitle}`, and `{keywords}` directives from ChordPro files
- Optional "Include lyric search" toggle so large catalogs can disable lyric matching for faster filtering
- Documentation updates covering the new search capabilities and ChordPro metadata best practices

## [1.0.0] - 2025-01-XX

### Added
- Initial release of genlist-butler
- HTML catalog generation from music notation files
- Support for ChordPro (.chopro, .cho), PDF, MuseScore (.mscz), and URL files
- Git-based version tracking to identify newest file versions
- Three filtering modes: none, hidden, timestamp
- Interactive HTML with search and filter capabilities
- Easy song marking with `.easy` files
- File hiding with `.hide` files
- Optional PDF generation from ChordPro files
- Command-line interface with multiple options
- Fast batch git timestamp fetching (89x performance improvement)

### Performance
- Optimized git timestamp operations using single batch command
- Typical runtime: ~0.7 seconds for large music libraries

[1.0.0]: https://github.com/TuesdayUkes/genlist-butler/releases/tag/v1.0.0
