# GenList Butler

[![Tests](https://github.com/TuesdayUkes/genlist-butler/actions/workflows/test.yml/badge.svg)](https://github.com/TuesdayUkes/genlist-butler/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/genlist-butler.svg)](https://badge.fury.io/py/genlist-butler)
[![Python versions](https://img.shields.io/pypi/pyversions/genlist-butler.svg)](https://pypi.org/project/genlist-butler/)

A command-line tool for generating HTML music archives from ChordPro files, PDFs, and other music notation files. Originally created for the Tuesday Ukulele Group, this tool scans a directory tree of music files and generates a searchable, filterable HTML catalog.

## Features

- 📁 **Smart File Discovery**: Automatically finds ChordPro (.chopro, .cho), PDF, MuseScore, and other music files
- 🔍 **Version Control Integration**: Uses git timestamps to identify the newest version of duplicate files
- 🎯 **Filtering Options**: Hide older versions, mark easy songs, exclude specific files
- 📄 **PDF Generation**: Optional automatic PDF generation from ChordPro files
- 🌐 **Interactive HTML**: Generates searchable, filterable HTML catalogs with modern UI
- 🧠 **Metadata-Aware Search**: Parses `{title:}`, `{subtitle:}`, `{keywords:}` (and optional lyrics) so the catalog can be filtered beyond filenames
- 🎨 **Beautiful Styling**: Includes Tuesday Ukes' professional HTML template - no configuration needed!
- ⚡ **Fast**: Optimized git operations for quick catalog generation

## Requirements

- Python 3.9 or later
- Git (for version tracking features)

## Installation

Install using pipx (recommended):

```bash
pipx install genlist-butler
```

Or using pip:

```bash
pip install genlist-butler
```

## Usage

Basic usage:

```bash
genlist <music_folder> <output_file>
```

### Examples

Generate a catalog with default settings (newest versions only):

```bash
genlist ./music index.html
```

Show all file versions:

```bash
genlist ./music index.html --filter none
```

Hide only files marked with `.hide` extension:

```bash
genlist ./music index.html --filter hidden
```

Generate PDFs from ChordPro files before cataloging:

```bash
genlist ./music index.html --genPDF
```

### Options

- `musicFolder` - Path to the directory containing music files
- `outputFile` - Path where the HTML catalog will be written
- `--filter [none|hidden|timestamp]` - Filtering method (default: timestamp)
  - `none`: Show all files
  - `hidden`: Hide files with `.hide` extension
  - `timestamp`: Show only newest versions based on git history
- `--intro / --no-intro` - Include/exclude introduction section (default: include)
- `--genPDF / --no-genPDF` - Generate PDFs from ChordPro files (default: no)
- `--forcePDF / --no-forcePDF` - Regenerate all PDFs even if they exist (default: no)

### File Markers

GenList Butler uses special marker files:

- **`.hide` files**: Create a file with `.hide` extension (e.g., `song.hide`) to hide all files with the same base name from the catalog
- **`.easy` files**: Create a file with `.easy` extension (e.g., `song.easy`) to mark all files with the same base name as "easy songs" for filtering

### Search Metadata & Lyrics

The search bar now understands more than filenames:

- `{title: ...}` / `{t: ...}` and `{subtitle: ...}` / `{st: ...}` directives are indexed automatically.
- `{keywords: folk; jam; singalong}` directives (or `# keywords:` inline comments) let you define search tags without changing filenames.
- Full lyric text from `.chopro` files is indexed as well, and users can disable lyric-matching with the **Include lyric search** checkbox if they want faster filtering.

Add metadata directly in your ChordPro charts:

```chordpro
{title: Wagon Wheel}
{subtitle: Old Crow Medicine Show}
{keywords: campfire; beginner; singalong}

[G]Heading down south to the [D]land of the pines...
```

Those keywords/subtitles become instantly searchable in the generated HTML.

### Custom HTML Styling

GenList-Butler includes a beautiful, professional HTML template out of the box (Tuesday Ukes' styling). However, you can customize it:

1. Create your own `HTMLheader.txt` file in your working directory
2. Run genlist from that directory
3. Your custom header will be used instead of the default

The generated HTML will use your custom styling while maintaining all the interactive search/filter functionality.

## Requirements

- Python 3.9+
- Git (for timestamp-based filtering)
- ChordPro (optional, for PDF generation)

## How It Works

1. **Scans** the music folder recursively for supported file types
2. **Groups** files by song title (normalized, ignoring articles)
3. **Filters** based on the selected method:
   - Uses git history to find the newest version of each file
   - Respects `.hide` marker files
   - Processes `.easy` marker files for special highlighting
4. **Generates** an interactive HTML page with:
   - Searchable song list
   - Download links for all file formats
   - Optional filtering for easy songs
   - Toggle for showing all versions

## Development

To contribute or modify:

```bash
# Clone the repository
git clone https://github.com/TuesdayUkes/genlist-butler.git
cd genlist-butler

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see LICENSE file for details

## Credits

Created for the Tuesday Ukulele Group (https://tuesdayukes.org/)

Maintained by the TUG community.
