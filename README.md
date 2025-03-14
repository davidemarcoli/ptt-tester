# PTT Tester

A Python tool for systematic testing and evaluation of the PTT (Parse Torrent Title) library against large datasets or single torrent titles.

## Overview

This tool helps you validate the accuracy of the PTT library by:

1. Parsing single torrent titles for quick testing
2. Randomly sampling torrent titles from your dataset
3. Parsing them with PTT's `parse_title` function
4. Collecting your feedback on parsing accuracy
5. Tracking results across different library versions
6. Providing statistics on parsing accuracy

## Features

- **Single title parsing**: Test individual torrent titles directly without a dataset
- **Random sampling**: Tests random titles from your dataset to ensure broad coverage
- **Progress tracking**: Saves results to avoid retesting the same titles
- **Version control**: Supports testing across different versions of the PTT library
- **Resumable testing**: Can pause and resume testing sessions
- **Statistical reporting**: Provides accuracy metrics for each library version
- **Notes support**: Allows adding notes to failed parses for future reference
- **Retest mode**: Supports retesting previously evaluated titles with new library versions
- **Improved UX**: Default "yes" for correct parses and only ask for notes when needed

## Installation

1. Clone this repository
2. Install dependencies using Poetry:

```bash
poetry install
```

This will install both the script dependencies and the PTT library.

## Dependencies

- Python 3.12+
- [PTT (Parse Torrent Title)](https://github.com/dreulavelle/PTT) - The torrent parsing library being tested

## Usage

### Single Title Mode

Test a single torrent title directly:

```bash
python torrent_tester.py --title "Your.Torrent.Title.S01E01.1080p.HEVC"
```

Save the result to your results file:

```bash
python torrent_tester.py --title "Your.Torrent.Title.S01E01.1080p.HEVC" --save
```

### Dataset Mode

Test random titles from your dataset:

```bash
python torrent_tester.py path/to/torrent_titles.txt --version "1.5.9"
```

### Command-line Arguments

- `dataset`: Path to the text file containing torrent titles (one per line, optional)
- `--title`, `-t`: Process a single torrent title instead of reading from a file
- `--save`, `-s`: Save the result when testing a single title
- `--results`: Path to save test results (default: `parser_test_results.json`)
- `--version`: Version identifier of the PTT library being tested (default: `dev`)
- `--retest`: Retest previously tested titles with a new library version
- `--stats`: Print statistics and exit without testing

### Examples

Testing a single title:

```bash
python torrent_tester.py --title "Breaking.Bad.S01E05.720p.BluRay.x264"
```

Testing with a specific version and custom results file:

```bash
python torrent_tester.py data/torrents.txt --version "1.5.9" --results my_results.json
```

Retesting previously tested titles with a new version:

```bash
python torrent_tester.py data/torrents.txt --version "1.6.0" --retest
```

View current statistics without testing:

```bash
python torrent_tester.py data/torrents.txt --stats
```

## Interactive Testing Flow

During testing, you'll see:

1. The original torrent title
2. The parsed result from PTT
3. A prompt to evaluate the result:
   - `Y` or Enter - Correctly parsed (default)
   - `n` - Incorrectly parsed
   - `s` - Skip this title
   - `q` - Quit testing session

Notes are only requested for incorrect parses to streamline the workflow.

## Results Storage

Results are saved in a JSON file with the following structure:

```json
{
  "versions": {
    "1.5.9": {
      "tested_count": 25,
      "correct_count": 20,
      "timestamp": "2025-03-13T14:30:45"
    }
  },
  "titles": {
    "Example.Torrent.Title.720p.x264": {
      "1.5.9": {
        "is_correct": true,
        "parsed_result": { ... },
        "notes": "",
        "timestamp": "2025-03-13T14:25:30"
      }
    }
  }
}
```

This structure allows tracking:
- Overall statistics per version
- Individual parse results per title and version
- Notes for failed parses to guide improvements

## Best Practices

1. **Use single title mode** for quick testing during development
2. **Use dataset mode** for systematic testing before releases
3. **Use version numbers** that match the PTT library's versioning
4. **Save backups** of your results file periodically
5. **Test incrementally** rather than trying to test all titles at once
6. **Add detailed notes** for incorrect parses to help identify patterns
7. **Retest after updating** the PTT library to verify improvements

## Troubleshooting

### Corrupted Results File

If the results file becomes corrupted, the tool will automatically create a backup and start fresh. You can manually restore from the backup if needed.

### Large Datasets

For very large datasets (millions of titles), consider:
- Using a subset for initial testing
- Running shorter test sessions
- Monitoring memory usage

## Contributing

If you find issues with the PTT library's parsing, consider contributing to the main repository:
- File issues on the [PTT GitHub repository](https://github.com/dreulavelle/PTT)
- Submit pull requests with fixes for common parsing issues
- Share your test results with the library maintainer

## Project Structure

```
ptt-tester/
├── README.md
├── pyproject.toml
└── torrent_tester.py
```

## License

This tool is provided as-is. Feel free to modify and use it according to your needs.