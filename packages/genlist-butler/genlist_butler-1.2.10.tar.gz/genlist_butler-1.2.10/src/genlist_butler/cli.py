#! python
"""
GenList Butler - Music Catalog Generator

This module generates HTML catalogs from music notation files (ChordPro, PDF, MuseScore, etc.)
with git-based version tracking to show only the newest versions of each song.
"""

import subprocess
from first import first
from pathlib import Path
from posixpath import basename, splitext
import sys
import os
import argparse
import re
from datetime import datetime
from collections import defaultdict
from html import escape


# Default HTML header with Tuesday Ukes styling
DEFAULT_HTML_HEADER = """<!DOCTYPE html>
<html lang="en-US" class="no-js">
<head>
	<Title>Tuesday Ukes' archive of ukulele songs and chords</title>

	<meta name="description" content="Free downloads of ukulele tabs and chords for hundreds of songs, from Tin Pan Alley to today's most-popular hit tunes, from the Tuesday Uke Group.">

	<meta charset="utf-8">
	<link rel="canonical" href="https://tuesdayukes.org/ukulele-song-archive.html/">

	<meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="stylesheet" href="styles/main.css">
<style>
/* Modern body styling */
body.custom-background { 
  background: linear-gradient(135deg, var(--background) 0%, #edf2f7 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: var(--text-primary);
}

.desktop-only {
  display: none;
}

/* Container with max-width for better readability */
.site-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Modern heading styles */
h1 {
  color: var(--primary-color);
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
}

h2 {
  color: var(--secondary-color);
  font-size: 1.75rem;
  font-weight: 600;
  margin: 2rem 0 1rem 0;
  border-bottom: 2px solid var(--accent-color);
  padding-bottom: 0.5rem;
}

/* Search controls container */
.search-controls {
  background: var(--surface);
  padding: 2rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin: 2rem 0;
  border: 1px solid var(--border-light);
}

/* Modern search input */
#searchInput {
  width: 100%;
  max-width: 500px;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid var(--border-light);
  border-radius: var(--radius);
  transition: all 0.3s ease;
  background: white;
}

#searchInput:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(44, 82, 130, 0.1);
}

/* Modern checkbox styling */
.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 1rem;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

#easyFilter {
  width: 20px;
  height: 20px;
  accent-color: var(--accent-color);
  cursor: pointer;
}

/* Modern table styling */
#dataTable {
  width: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border-light);
  margin: 2rem 0;
}

/* Table header */
#dataTable thead {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}

#dataTable th {
  padding: 1rem;
  font-weight: 600;
  text-align: left;
  font-size: 16px;
  border: none;
}

/* Table rows */
#dataTable tbody tr {
  border-bottom: 1px solid var(--border-light);
  transition: background-color 0.2s ease;
}

#dataTable tbody tr:hover {
  background-color: #f8fafc;
}

/* Easy song highlighting */
#dataTable tbody tr.easy-song {
  background-color: rgba(246, 173, 85, 0.1);
  border-left: 4px solid var(--accent-color);
}

#dataTable tbody tr.easy-song:hover {
  background-color: rgba(246, 173, 85, 0.15);
}

/* Table cells */
#dataTable td {
  padding: 0.5rem;
  border: none;
  vertical-align: top;
  overflow-wrap:anywhere;
}

/* Row number styling - only when line numbers are enabled */
#dataTable.with-line-numbers td:first-child {
  font-weight: 600;
  color: var(--text-secondary);
  font-family: 'Monaco', 'Consolas', monospace;
  width: 80px;
  text-align: center;
  background: rgba(44, 82, 130, 0.05);
}

/* Song title styling */
#dataTable.with-line-numbers td:nth-child(2) {
  font-weight: 600;
  color: var(--text-primary);
  min-width: 0px;
}

#dataTable.no-line-numbers td:first-child {
  font-weight: 600;
  color: var(--text-primary);
  min-width: 0px;
}

/* Download links styling */
#dataTable td:last-child {
  min-width: 0px;
}

#dataTable a {
  display: inline-block;
  padding: 6px 12px;
  margin: 2px 4px 2px 0;
  background: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

#dataTable a:hover {
  background: var(--secondary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Special styling for PDF links */
#dataTable a[href$=".pdf"] {
  background: #dc2626;
}

#dataTable a[href$=".pdf"]:hover {
  background: #b91c1c;
}

/* External links (like Doctor Uke) */
#dataTable a[target="_blank"]:not([download]) {
  background: var(--accent-color);
  color: var(--text-primary);
}

#dataTable a[target="_blank"]:not([download]):hover {
  background: #ed8936;
}

/* Responsive design */
@media (max-width: 768px) {
  .site-inner {
    padding: 1rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .search-controls {
    padding: 1.5rem;
  }
  
  #searchInput {
    max-width: 100%;
  }
  
  #dataTable {
    font-size: 14px;
  }
  
  #dataTable td {
    padding: 0.75rem 0.5rem;
  }
  
  #dataTable.with-line-numbers td:first-child {
    width: 60px;
  }
}

@media (min-width: 769px) {
  .desktop-only {
    display: block;
  }
}

/* Loading state for when table is filtering */
.table-loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Easy song badge */
.easy-badge {
  display: inline-block;
  background: var(--accent-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
}

/* Search stats */
.search-stats {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(44, 82, 130, 0.05);
  border-radius: var(--radius);
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
}

/* Checkbox styling for consistent sizing */
.filter-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  accent-color: var(--primary-color);
  cursor: pointer;
  vertical-align: middle;
}

.filter-checkbox label {
  cursor: pointer;
  display: inline-block;
  vertical-align: middle;
  font-size: 16px;
  line-height: 1.4;
}

/* Per-song "show all versions" button */
.show-all-versions-btn {
  margin-left: 0.75rem;
  padding: 4px 12px;
  font-size: 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--primary-color);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.show-all-versions-btn:hover,
.show-all-versions-btn[data-expanded="true"] {
  background: var(--primary-color);
  color: #fff;
}

/* Hidden additional versions - remove gaps */
.additional-version[style*="display: none"],
.additional-version[style*="display:none"] {
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
  overflow: hidden !important;
}

/* Hide br tags that immediately follow hidden additional-version links */
.additional-version[style*="display: none"] + br,
.additional-version[style*="display:none"] + br {
  display: none !important;
}

</style>
	</head>

"""

CUSTOM_HEADER_DESKTOP_ONLY_STYLE = """
<style>
.desktop-only { display: none; }
@media (min-width: 769px) {
  .desktop-only { display: block; }
}
</style>
"""

KEYWORD_DIRECTIVE_PATTERN = re.compile(r"\{\s*keywords?\s*:(.*?)\}", re.IGNORECASE)
KEYWORD_LINE_PATTERN = re.compile(r"^\s*(?:#\s*)?keywords?\s*:(.*)$", re.IGNORECASE)
SUBTITLE_DIRECTIVE_PATTERN = re.compile(r"\{\s*(?:subtitle|st)\s*:(.*?)\}", re.IGNORECASE)
SUBTITLE_LINE_PATTERN = re.compile(r"^\s*(?:#\s*)?(?:subtitle|st)\s*:(.*)$", re.IGNORECASE)
TITLE_DIRECTIVE_PATTERN = re.compile(r"\{\s*(?:title|t)\s*:(.*?)\}", re.IGNORECASE)
TITLE_LINE_PATTERN = re.compile(r"^\s*(?:#\s*)?(?:title|t)\s*:(.*)$", re.IGNORECASE)
CHORD_PATTERN = re.compile(r"\[[^\]]+\]")


def _split_keyword_values(raw_value):
  return [token.strip().lower() for token in re.split(r"[;,]", raw_value) if token.strip()]


def _keywords_from_line(line):
  keywords = []
  for directive in KEYWORD_DIRECTIVE_PATTERN.findall(line):
    keywords.extend(_split_keyword_values(directive))

  line_match = KEYWORD_LINE_PATTERN.match(line)
  if line_match:
    keywords.extend(_split_keyword_values(line_match.group(1)))

  return keywords


def _subtitles_from_line(line):
  subtitles = []
  for directive in SUBTITLE_DIRECTIVE_PATTERN.findall(line):
    subtitles.append(directive.strip())

  line_match = SUBTITLE_LINE_PATTERN.match(line)
  if line_match:
    subtitles.append(line_match.group(1).strip())

  return [subtitle for subtitle in subtitles if subtitle]


def _titles_from_line(line):
  titles = []
  for directive in TITLE_DIRECTIVE_PATTERN.findall(line):
    titles.append(directive.strip())

  line_match = TITLE_LINE_PATTERN.match(line)
  if line_match:
    titles.append(line_match.group(1).strip())

  return [title for title in titles if title]


def _lyric_from_line(line):
  stripped = line.strip()
  if not stripped:
    return None
  if stripped.startswith('#'):
    return None
  if stripped.startswith('{') and stripped.endswith('}'):
    return None
  sanitized = _sanitize_lyric_text(stripped)
  return sanitized if sanitized else None


def _sanitize_lyric_text(line):
  """Remove inline chord markers and lyric hyphenation artifacts to improve searchability."""

  without_chords = CHORD_PATTERN.sub('', line)
  # Chord writers often split syllables like merri-[D7]-ly; join those while keeping true hyphenated words readable
  def _normalize_hyphenation(text):
    pattern = re.compile(r"(\b\w+)(?:\s*-\s*)+(\w+\b)")

    def _replacer(match):
      left = match.group(1)
      right = match.group(2)
      left_last = left[-1].lower()
      right_first = right[0].lower()
      left_is_short = len(left) <= 2
      right_is_short = len(right) <= 2
      left_ends_with_vowel = left_last in "aeiouy"
      right_starts_with_vowel = right_first in "aeiouy"

      # Join when the hyphen is clearly splitting one word across syllables
      if left_is_short or right_is_short or left_ends_with_vowel or right_starts_with_vowel:
        return f"{left}{right}"

      # Otherwise treat it as a separator (e.g., old-fashioned -> old fashioned)
      return f"{left} {right}"

    previous = None
    current = text
    while current != previous:
      previous = current
      current = pattern.sub(_replacer, current)
    return current

  smoothed = _normalize_hyphenation(without_chords)
  normalized = re.sub(r"\s+", " ", smoothed).strip()
  return normalized


def extract_chopro_metadata(file_path):
  metadata = {
    "keywords": set(),
    "titles": set(),
    "subtitles": set(),
    "lyrics": []
  }

  try:
    with open(file_path, "r", encoding="utf-8") as song_file:
      for line in song_file:
        metadata["keywords"].update(_keywords_from_line(line))
        metadata["titles"].update(_titles_from_line(line))
        metadata["subtitles"].update(_subtitles_from_line(line))
        lyric_line = _lyric_from_line(line)
        if lyric_line:
          metadata["lyrics"].append(lyric_line)
  except (OSError, UnicodeDecodeError) as exc:
    print(f"Warning: Could not read metadata from {file_path}: {exc}", file=sys.stderr)

  return metadata


def main():
    """Main entry point for genlist CLI"""
    parser = argparse.ArgumentParser(
        description="Generate HTML catalogs from music notation files with git-based version tracking"
    )
    parser.add_argument("musicFolder", help="Path to the directory containing music files")
    parser.add_argument("outputFile", help="Path where the HTML catalog will be written")
    parser.add_argument("--intro", action=argparse.BooleanOptionalAction, default=True,
                        help="Include/exclude introduction section (default: include)")
    parser.add_argument("--genPDF", action=argparse.BooleanOptionalAction, default=False,
                        help="Generate PDFs from ChordPro files (default: no)")
    parser.add_argument("--forcePDF", action=argparse.BooleanOptionalAction, default=False,
                        help="Regenerate all PDFs even if they exist (default: no)")
    parser.add_argument("--filter", choices=["none", "hidden", "timestamp"], default="timestamp",
                        help="Filter method: 'none' (show all files), 'hidden' (hide files with .hide), 'timestamp' (show newest versions only)")
    parser.add_argument("--line-numbers", action=argparse.BooleanOptionalAction, default=True,
                        help="Include/exclude row numbers in the generated table (default: include)")
    args = parser.parse_args()

    print("Generating Music List (this takes a few seconds)", file=sys.stderr)
    print(f"Using filter method: {args.filter}", file=sys.stderr)

    musicFolder = args.musicFolder
    outputFile = args.outputFile
    intro = args.intro
    forceNewPDF = args.forcePDF
    genPDF = args.genPDF
    filterMethod = args.filter
    showLineNumbers = args.line_numbers

    now = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")

    def append_cache_bust(url):
      if not url:
        return url
      separator = '&' if '?' in url else '?'
      return f"{url}{separator}cb={now}"

    markerExtensions = {".easy", ".hide"}
    nonVersionedExtensions = markerExtensions | {".urltxt"}

    # lambda filename accepts a path and returns just the filename without an extension
    filename = lambda p: str(os.path.splitext(os.path.basename(p))[0])

    # lambda ext is like lambda filename, except it returns the file extension
    ext = lambda p: str(os.path.splitext(os.path.basename(p))[1]).lower()

    def createPDFs():
        linuxpath = ["perl",
                     "/home/paul/chordpro/script/chordpro.pl",
                     "--config=/home/paul/chordpro/lib/ChordPro/res/config/ukulele.json",
                     "--config=/home/paul/chordpro/lib/ChordPro/res/config/ukulele-ly.json"
                     ]

        winpath = ["chordpro",
                   "--config=Ukulele",
                   "--config=Ukulele-ly"
                   ]

        chordproSettings=[
            "--define=pdf:diagrams:show=top",
            "--define=settings:inline-chords=true",
            "--define=pdf:margintop=70",
            "--define=pdf:marginbottom=0",
            "--define=pdf:marginleft=20",
            "--define=pdf:marginright=20",
            "--define=pdf:headspace=50",
            "--define=pdf:footspace=10",
            "--define=pdf:head-first-only=true",
            "--define=pdf:fonts:chord:color=red",
            "--text-font=helvetica",
            "--chord-font=helvetica"
        ]

        if os.name == "nt":
            chordproSettings = winpath + chordproSettings
        else:
            chordproSettings = linuxpath + chordproSettings

        extensions = [".chopro", ".cho"]
        for p in Path(musicFolder).rglob('*'):
            if ext(p) in (extension.lower() for extension in extensions):
                pdfFile = str(os.path.splitext(str(p))[0]) + ".pdf"
                if not os.path.exists(pdfFile) or forceNewPDF:
                    print("Generating " + pdfFile)
                    subprocess.run(chordproSettings + [str(p)])

    # A file with the extension ".hide" will prevent other files within the same
    # folder with the same name (but all extensions) from being adding to the
    # archive table. This is a way to conceal older versions of a song, without
    # breaking old links to the older versions (the files still exist, but there
    # will be no HTML links to them in the new archive table).

    # A file with the extension ".easy" will mark other files within the same
    # folder with the same name as "easy" songs for filtering purposes.
    def getEasySongs(allFiles):
        # Use set comprehension for better performance
        return {str(os.path.splitext(f)[0]).lower() 
                for f in allFiles if ext(f).lower() == ".easy"}

    def getAllGitTimestamps(files):
        """Get git timestamps for all files in one batch operation using a single git command"""
        timestamps = {}
        
        # Try to find git root from current directory
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_root = result.stdout.strip()
            else:
                # If no git repo found, fall back to mtimes
                return {f: int(os.path.getmtime(f)) for f in files}
        except:
            # If git command fails, fall back to mtimes
            return {f: int(os.path.getmtime(f)) for f in files}
        
        try:
            # Convert all file paths to relative paths
            relative_files = {}
            for f in files:
                abs_path = os.path.abspath(f)
                try:
                    rel_path = os.path.relpath(abs_path, git_root)
                    # Normalize path separators for git
                    rel_path = rel_path.replace('\\', '/')
                    relative_files[rel_path] = f
                except:
                    # If we can't get relative path, fall back to mtime
                    timestamps[f] = int(os.path.getmtime(f))
            
            if not relative_files:
                return timestamps
            
            # Use git log with --name-only and custom format to get all timestamps at once
            # Format: timestamp on one line, then changed files on following lines
            result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:%ct"],
                capture_output=True,
                text=True,
                cwd=git_root,
                timeout=30  # Longer timeout for the full log
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse the output: timestamp followed by list of files
                lines = result.stdout.strip().split('\n')
                current_timestamp = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if line is a timestamp (all digits)
                    if line.isdigit():
                        current_timestamp = int(line)
                    elif current_timestamp and line in relative_files:
                        # This is a file path and we don't have its timestamp yet
                        orig_path = relative_files[line]
                        if orig_path not in timestamps:
                            timestamps[orig_path] = current_timestamp
            
            # For any files not found in git log, use file modification time
            for rel_path, orig_path in relative_files.items():
                if orig_path not in timestamps:
                    timestamps[orig_path] = int(os.path.getmtime(orig_path))
            
            return timestamps
            
        except Exception as e:
            print(f"Error getting git timestamps: {e}", file=sys.stderr)
            # Return mtimes as fallback for all files
            return {f: int(os.path.getmtime(f)) for f in files}

    def keepNewestVersionsOnly(allFiles):
        """Keep only the newest version of each song file by extension type"""
        # Group files by base name (without extension) and extension
        filesByBasenameAndExt = defaultdict(list)
        
        for f in allFiles:
            extension = ext(f).lower()
            if extension in nonVersionedExtensions:
                continue  # Skip marker and non-versioned files

            baseName = dictCompare(filename(f))
            filesByBasenameAndExt[(baseName, extension)].append(f)
        
        # Collect all files that need timestamps (files with duplicates)
        filesNeedingTimestamps = []
        for (baseName, extension), files in filesByBasenameAndExt.items():
            if len(files) > 1:
                filesNeedingTimestamps.extend(files)
        
        # Get all timestamps in batch if there are any files with duplicates
        if filesNeedingTimestamps:
            print(f"Fetching git timestamps for {len(filesNeedingTimestamps)} files with duplicates...", file=sys.stderr)
            gitTimestamps = getAllGitTimestamps(filesNeedingTimestamps)
        else:
            gitTimestamps = {}
        
        # For each group, keep only the file with the newest git timestamp
        newestFiles = []
        for (baseName, extension), files in filesByBasenameAndExt.items():
            if len(files) == 1:
                newestFiles.extend(files)
            else:
                # Multiple files with same basename and extension - keep the newest
                filesWithTimestamps = []
                for f in files:
                    timestamp = gitTimestamps.get(f, 0)
                    filesWithTimestamps.append((timestamp, f))
                
                # Sort by timestamp (newest first) and take the first one
                filesWithTimestamps.sort(reverse=True)
                newestFile = filesWithTimestamps[0][1]
                newestFiles.append(newestFile)
                
                print(f"Multiple versions found for {baseName}{extension}:", file=sys.stderr)
                for timestamp, f in filesWithTimestamps:
                    marker = "* KEPT" if f == newestFile else "  ignored"
                    print(f"  {marker}: {f} (timestamp: {timestamp})", file=sys.stderr)
        
        # Add back the marker files (.hide, .easy)
        for f in allFiles:
            if ext(f).lower() in nonVersionedExtensions:
                newestFiles.append(f)
        
        return newestFiles

    def removeHiddenFiles(allFiles):
        # Use set for O(1) lookup instead of list with O(n) lookup
        hideFiles = set()
        visibleFiles = []
        
        # Single pass to collect hide files
        for f in allFiles:
            if ext(f).lower() == ".hide":
                hideFiles.add(str(os.path.splitext(f)[0]).lower())
        
        # Second pass to filter visible files
        for f in allFiles:
            basename = str(os.path.splitext(f)[0]).lower()
            if basename not in hideFiles:
                visibleFiles.append(f)

        return visibleFiles

    # dictCompare removes articles that appear as the first word in a filename
    articles = {'a', 'an', 'the'}  # Use set for faster lookup
    def dictCompare(s):
        sWords = s.split()
        if sWords and sWords[0].lower() in articles:
            formattedS = ' '.join(sWords[1:])
        else:
            formattedS = s

        # Remove punctuation in one pass using translate
        return formattedS.translate(str.maketrans('', '', '\',\'')).lower()

    # Load HTML header - check for custom file first, otherwise use embedded default
    custom_header_used = False
    if os.path.exists("HTMLheader.txt"):
        with open("HTMLheader.txt", "r", encoding='utf-8') as headerText:
            header = headerText.readlines()
        print("Using custom HTMLheader.txt from current directory", file=sys.stderr)
        custom_header_used = True
    else:
        # Use the embedded default header
        header = DEFAULT_HTML_HEADER.splitlines(keepends=True)

    extra_desktop_style = CUSTOM_HEADER_DESKTOP_ONLY_STYLE if custom_header_used else ""

    introduction = f"""{extra_desktop_style}
  <h1>Tuesday Ukes' Archive of Ukulele Songs and Chords</h1>

  <section class="archive card">
    <div class="archive-overview card desktop-only">
      <p>Whether you're a beginner ukulele player looking for easy songs or a longtime
      player searching for fun songs, this is the resource for you. Here you will find
      ukulele chords and chord diagrams for uke players of all levels.</p>

      <p>This collection of the best ukulele songs has been built over time by members
      of Austin's Tuesday Ukulele Group. </p>

      <h2>Lots of Popular Songs</h2>
      <p>There's a big range: Easy ukulele songs with simple chords for beginner
      ukulele players with just 3 chords or 4 chords. You will find great songs by
      Paul McCartney, Neil Diamond, Bob Dylan, John Denver, and Bob Marley turned into
      ukulele music. More-advanced ukulele music players can find finger-stretching
      chord changes and chord shapes applied to popular ukulele songs. </p>
    </div>
  """

    searchControls = """
<div class="search-controls">
    <h2>Search & Filter</h2>
    <input type="text" id="searchInput" placeholder="🔍 Search songs by title, keyword, or lyrics..." autocorrect="off" autocapitalize="off" spellcheck="false">
    <div class="filter-checkbox">
        <input type="checkbox" id="easyFilter">
        <label for="easyFilter">🎵 Show only easy songs (perfect for beginners!)</label>
    </div>
    <div class="filter-checkbox">
      <input type="checkbox" id="lyricSearchToggle" checked>
      <label for="lyricSearchToggle">📝 Include lyric search (may be slower)</label>
    </div>
    <div id="searchStats" class="search-stats" style="display: none;">
        Showing <span id="visibleCount">0</span> of <span id="totalCount">0</span> songs
    </div>
</div>
"""

    searchScript = """
  </section>
<script>
    const searchInput = document.getElementById('searchInput');
    const easyFilter = document.getElementById('easyFilter');
    const lyricSearchToggle = document.getElementById('lyricSearchToggle');
    const table = document.getElementById('dataTable');
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    const searchStats = document.getElementById('searchStats');
    const visibleCountSpan = document.getElementById('visibleCount');
    const totalCountSpan = document.getElementById('totalCount');
    const versionToggleButtons = document.querySelectorAll('.show-all-versions-btn');

    // Normalize text so Safari smart quotes match the ASCII titles stored in the catalog
    function normalizeSearchText(input) {
      if (!input) {
        return '';
      }

      let normalized = input;
      if (typeof normalized.normalize === 'function') {
        normalized = normalized.normalize('NFKD');
      }

      return normalized
        .replace(/[\u2018\u2019\u201A\u201B\u2032\u2035\u02BC]/g, "'")
        .replace(/[\u201C\u201D\u201E\u201F\u2033\u2036]/g, '"')
        .replace(/\u00A0/g, ' ')
        .toLowerCase();
    }

    // Set total count
    totalCountSpan.textContent = rows.length;

    function updateSearchStats(visibleCount) {
      visibleCountSpan.textContent = visibleCount;
      const showStats = searchInput.value || easyFilter.checked || (lyricSearchToggle && !lyricSearchToggle.checked);
      searchStats.style.display = showStats ? 'block' : 'none';
    }

    function applyAdditionalVersionVisibility(row) {
        const toggleButton = row.querySelector('.show-all-versions-btn');
        const isExpanded = toggleButton && toggleButton.getAttribute('data-expanded') === 'true';
        const additionalVersions = row.querySelectorAll('.additional-version');
        additionalVersions.forEach(link => {
            link.style.display = isExpanded ? '' : 'none';
        });
    }

    function filterRows() {
        const searchFilter = normalizeSearchText(searchInput.value);
        const easyOnly = easyFilter.checked;
        const lyricSearchEnabled = lyricSearchToggle ? lyricSearchToggle.checked : true;
        let visibleCount = 0;

        // Add loading effect
        table.classList.add('table-loading');

        setTimeout(() => {
            for (let i = 0; i < rows.length; i++) {
                const rowText = normalizeSearchText(rows[i].textContent);
                const metadataText = normalizeSearchText(rows[i].dataset.metadata || '');
                const lyricText = lyricSearchEnabled ? normalizeSearchText(rows[i].dataset.lyrics || '') : '';
                let isEasy = rows[i].classList.contains('easy-song');

                let showBySearch = !searchFilter || rowText.includes(searchFilter) || metadataText.includes(searchFilter) || (lyricText && lyricText.includes(searchFilter));
                let showByEasy = !easyOnly || isEasy;

                const shouldShow = showBySearch && showByEasy;
                rows[i].style.display = shouldShow ? '' : 'none';

                if (shouldShow) {
                    visibleCount++;
                    applyAdditionalVersionVisibility(rows[i]);
                }
            }

            updateSearchStats(visibleCount);
            table.classList.remove('table-loading');
        }, 50);
    }

    // Enhanced input with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(filterRows, 300);
    });

    easyFilter.addEventListener('change', filterRows);
    if (lyricSearchToggle) {
        lyricSearchToggle.addEventListener('change', filterRows);
    }

    versionToggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const expanded = button.getAttribute('data-expanded') === 'true';
            const newState = !expanded;
            button.setAttribute('data-expanded', newState.toString());
            button.setAttribute('aria-expanded', newState.toString());
            button.textContent = newState ? 'Hide older versions' : 'Show all versions';
            const row = button.closest('tr');
            if (row) {
                applyAdditionalVersionVisibility(row);
            }
        });
    });

    // Initialize with default filtering based on server-side filter method
    // Hide additional versions by default unless filter method was "none"
    const defaultFilterMethod = '""" + filterMethod + """';
    if (defaultFilterMethod !== 'none') {
        // Hide additional file versions by default
        const additionalVersions = document.querySelectorAll('.additional-version');
        additionalVersions.forEach(link => {
            link.style.display = 'none';
        });
    }
    
    // Update initial stats
    filterRows();
</script>
"""

    if genPDF:
        createPDFs()

    # Pre-convert extensions to lowercase for faster comparison
    extensions = {".pdf", ".chopro", ".cho", ".mscz", ".urltxt", ".hide", ".easy", ".mp3", ".m4a"}
    allFiles = []
    # Use a single rglob call and filter more efficiently
    for p in Path(musicFolder).rglob('*'):
        if p.suffix.lower() in extensions:
            allFiles.append(p.as_posix())

    # Determine which files should be filtered out for JavaScript handling
    # Always include all files in HTML, but mark filtered ones with CSS classes
    visibleFiles = allFiles

    # Determine which files would be filtered by timestamp filtering
    newestFiles = keepNewestVersionsOnly(allFiles)
    hiddenByTimestamp = set(allFiles) - set(newestFiles)

    # Determine which files would be filtered by .hide files  
    visibleByHide = removeHiddenFiles(allFiles)
    hiddenByHideFiles = set(allFiles) - set(visibleByHide)

    # Apply the selected filtering method for the default view state
    if filterMethod == "none":
        defaultHiddenFiles = set()
    elif filterMethod == "hidden":
        defaultHiddenFiles = hiddenByHideFiles
    elif filterMethod == "timestamp":
        # Files hidden by timestamp OR by .hide files
        defaultHiddenFiles = hiddenByTimestamp | hiddenByHideFiles
    else:
        # Fallback to timestamp method if somehow an invalid value gets through
        defaultHiddenFiles = hiddenByTimestamp | hiddenByHideFiles

    easySongs = getEasySongs(allFiles)

    # Precompute searchable metadata pulled from each ChordPro file so the HTML can expose it to the search UI
    choproSearchIndex = defaultdict(lambda: {"keywords": set(), "titles": set(), "subtitles": set(), "lyrics": []})
    for filePath in allFiles:
        if ext(filePath).lower() == ".chopro":
            metadata = extract_chopro_metadata(filePath)
            if not any(metadata.values()):
                continue
            titleKey = dictCompare(filename(filePath))
            entry = choproSearchIndex[titleKey]
            entry["keywords"].update(metadata["keywords"])
            entry["titles"].update(metadata["titles"])
            entry["subtitles"].update(metadata["subtitles"])
            if metadata["lyrics"]:
                entry["lyrics"].extend(metadata["lyrics"])

    # return the first file that matches basename (there should be only zero or one
    # matches). Return None if no matches found.
    def findMatchingBasename(files, basename):
        return first((f for f in files if dictCompare(f[0]) == dictCompare(filename(basename))))

    # allTitles will be an array of arrays. Each element's [0] entry will be the
    # song title. The other entries will be file paths that contain that title.
    # Use dictionary for faster lookup, then convert to list
    titleDict = {}
    for p in visibleFiles:
        title = filename(p)
        titleKey = dictCompare(title)
        if titleKey in titleDict:
            titleDict[titleKey].append(str(p))
        else:
            titleDict[titleKey] = [title, str(p)]

    allTitles = list(titleDict.values())

    downloadExtensions = [".cho", ".chopro"]
    sortedTitles = sorted(allTitles, key=(lambda e: dictCompare(e[0]).casefold()))
    with open(outputFile, "w", encoding='utf-8') as htmlOutput:
        htmlOutput.writelines(header)
        if intro:
            htmlOutput.writelines(introduction)
        htmlOutput.writelines(searchControls)
        tableClass = 'class="with-line-numbers"' if showLineNumbers else 'class="no-line-numbers"'
        htmlOutput.write(f'<table id="dataTable" {tableClass}>')
        htmlOutput.write("<thead>\n")
        if showLineNumbers:
            htmlOutput.write("<tr><th>#</th><th>Song Title</th><th>Downloads</th></tr>\n")
        else:
            htmlOutput.write("<tr><th>Song Title</th><th>Downloads</th></tr>\n")
        htmlOutput.write("</thead>\n")
        htmlOutput.write("<tbody>\n")
        row_number = 1
        for f in sortedTitles:
            try:
                # Check if this song is marked as easy
                isEasy = any(str(os.path.splitext(file)[0]).lower() in easySongs for file in f[1:])
                
                # Check if this song has additional versions hidden by the default filter
                # Used to determine whether to render a per-song "show all versions" button
                relevantDownloads = [file for file in f[1:] if ext(file) not in markerExtensions]
                hiddenDownloads = [file for file in relevantDownloads if file in defaultHiddenFiles]
                visibleDownloads = [file for file in relevantDownloads if file not in defaultHiddenFiles]
                hasAdditionalVersions = bool(visibleDownloads) and bool(hiddenDownloads)
                forceRevealHiddenDownloads = not visibleDownloads and bool(hiddenDownloads)
                
                # Only mark as hidden-version if there are additional filtered versions available
                # This helps users notice that more downloads exist in the same row
                isHiddenVersion = hasAdditionalVersions
                
                # Build CSS classes
                cssClasses = []
                if isEasy:
                    cssClasses.append("easy-song")
                if isHiddenVersion:
                    cssClasses.append("hidden-version")

                titleKey = dictCompare(f[0])
                titleMetadata = choproSearchIndex.get(titleKey)

                attributeParts = []
                if cssClasses:
                    attributeParts.append(f'class="{" ".join(cssClasses)}"')

                if titleMetadata:
                  metadataTokens = []
                  if titleMetadata["keywords"]:
                    metadataTokens.append(" ".join(sorted(titleMetadata["keywords"])))
                  if titleMetadata["titles"]:
                    metadataTokens.append(" ".join(sorted(titleMetadata["titles"])))
                  if titleMetadata["subtitles"]:
                    metadataTokens.append(" ".join(sorted(titleMetadata["subtitles"])))

                  if metadataTokens:
                    metadataValue = escape(" ".join(metadataTokens).lower(), quote=True)
                    attributeParts.append(f'data-metadata="{metadataValue}"')

                  if titleMetadata["lyrics"]:
                    lyricsValue = escape(" ".join(titleMetadata["lyrics"]).lower(), quote=True)
                    attributeParts.append(f'data-lyrics="{lyricsValue}"')

                attrString = f" {' '.join(attributeParts)}" if attributeParts else ''

                htmlOutput.write(f"<tr{attrString}>")
                # conditionally include row number column
                if showLineNumbers:
                    htmlOutput.write(f"  <td>{row_number}</td>")
                # song title column + optional per-row version toggle
                htmlOutput.write("  <td>")
                htmlOutput.write(f"{f[0]}")
                if hasAdditionalVersions:
                    htmlOutput.write(
                        ' <button type="button" class="show-all-versions-btn" data-expanded="false" aria-expanded="false">Show all versions</button>'
                    )
                htmlOutput.write("</td>\n<td>")
                # the remainder of f's elements are files that match the title in f[0]
                # Sort the files to ensure consistent ordering across operating systems
                # Sort by extension first, then by the complete normalized path
                sorted_files = sorted(f[1:], key=lambda x: (ext(x), x.lower().replace('\\', '/')))
                for i in sorted_files:
                    # Skip .easy and .hide marker files - they shouldn't appear as downloads
                    if ext(i) in [".easy", ".hide"]:
                        continue
                    
                    # Determine if this file is hidden by the current filter method
                    isHiddenByDefault = i in defaultHiddenFiles
                    shouldForceVisible = forceRevealHiddenDownloads and isHiddenByDefault
                    fileClass = '' if shouldForceVisible else (' class="additional-version"' if isHiddenByDefault else '')
                    
                    if ext(i) == ".urltxt":
                      with open(i, "r") as urlFile:
                        label = urlFile.readline().strip()
                        address = urlFile.readline().strip()
                      busted_address = append_cache_bust(address)
                      htmlOutput.write(
                        f"<a href=\"{escape(busted_address, quote=True)}\" target=\"_blank\"{fileClass}>{escape(label)}</a><br>\n"
                      )
                    elif ext(i) in downloadExtensions:
                        htmlOutput.write(f" <a href=\"{str(i).replace(' ','%20')}?v={now}\" download=\"{filename(i)}{ext(i)}\" target=\"_blank\"{fileClass}>{ext(i)}</a><br>\n")
                    else:
                        htmlOutput.write(f"  <a href=\"{str(i).replace(' ','%20')}?v={now}\" target=\"_blank\"{fileClass}>{ext(i)}</a><br>\n")

                # close each table row (and the table data containing file links)
                htmlOutput.write("</td></tr>\n")
                row_number += 1
            except:
                print(f"failed to write {f[1:]}")

        #close the table etc.
        htmlOutput.write("</tbody>")
        htmlOutput.write("</table>")
        htmlOutput.write(searchScript)
        htmlOutput.write("</div>\n")
        htmlOutput.write("</div>\n")
        htmlOutput.write("</body>\n")

    print("Done!", file=sys.stderr)


if __name__ == "__main__":
    main()
