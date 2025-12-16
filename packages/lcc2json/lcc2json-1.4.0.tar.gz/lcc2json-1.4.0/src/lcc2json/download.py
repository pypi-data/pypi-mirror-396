#!/usr/bin/env python3
"""
Download Library of Congress Classification JSON files from id.loc.gov.

This script downloads the LCC hierarchy as combined JSON files:
1. Fetches the main classification scheme to get top-level classes (A-Z)
2. For each class, fetches subclass ranges (e.g., AC1-AC1100)

The subclass range files contain all the classification data needed,
including individual classification numbers embedded within them.

Files are saved to a 'json/' directory with the classification ID as filename.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://id.loc.gov/authorities/classification"
DEFAULT_OUTPUT_DIR = "json"
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 5  # seconds
REQUEST_TIMEOUT = 30  # seconds
DEFAULT_MAX_DEPTH = 2  # Download root + classes + subclass ranges


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download Library of Congress Classification JSON files from id.loc.gov",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Download all classifications to ./json/ (depth 2)
  %(prog)s --max-depth 4       # Download to depth 4 (includes subdivisions)
  %(prog)s -o lcc_data         # Download to ./lcc_data/
  %(prog)s -v                  # Verbose output
  %(prog)s --dry-run           # Show what would be downloaded

Depth levels:
  0 = Root classification scheme
  1 = Main classes (A-Z)
  2 = Subclass ranges (e.g., PR1-PR9680) [default]
  3 = Period/topic divisions (e.g., PR6050-PR6076)
  4 = Alphabetical ranges (e.g., PR6066.A-PR6066.Z)
  5+ = Individual entries (e.g., PR6066.A84)
        """,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for JSON files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"Maximum depth to crawl (default: {DEFAULT_MAX_DEPTH})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )
    return parser.parse_args()


def create_session() -> requests.Session:
    """Create a requests session with appropriate headers."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "LCC-JSON-Downloader/1.0 (Library research tool)",
            "Accept": "application/json",
        }
    )
    return session


def download_with_retry(
    session: requests.Session,
    url: str,
    max_retries: int = MAX_RETRIES,
    initial_delay: float = INITIAL_RETRY_DELAY,
) -> Optional[dict]:
    """
    Download JSON from URL with exponential backoff retry.

    Args:
        session: requests Session object
        url: URL to download
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry

    Returns:
        Parsed JSON data or None if all retries failed
    """
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed for {url}: {e}"
                )
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"All {max_retries + 1} attempts failed for {url}: {e}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            return None

    return None


def extract_classification_id(uri: str) -> str:
    """
    Extract the classification ID from a full URI.

    Example: "http://id.loc.gov/authorities/classification/AC1" -> "AC1"
    """
    return urlparse(uri).path.split("/")[-1]


def get_safe_filename(classification_id: str) -> str:
    """
    Convert a classification ID to a safe filename.

    Replaces characters that might cause filesystem issues.
    """
    # Replace problematic characters
    safe_name = classification_id.replace("/", "_").replace("\\", "_")
    return f"{safe_name}.json"


def save_json(data: dict, output_path: Path) -> bool:
    """
    Save JSON data to a file.

    Args:
        data: JSON data to save
        output_path: Path to save the file

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        logger.error(f"Failed to save {output_path}: {e}")
        return False


def extract_member_uris(data: list, include_narrower: bool = False) -> list[str]:
    """
    Extract member URIs from a JSON-LD response.

    Looks for MADS and SKOS collection member properties, and optionally
    hasNarrowerAuthority for deeper traversal.

    Args:
        data: JSON-LD data list
        include_narrower: If True, also extract hasNarrowerAuthority links
    """
    member_uris = set()

    for item in data:
        # Check for MADS collection members
        mads_members = item.get(
            "http://www.loc.gov/mads/rdf/v1#hasMADSCollectionMember", []
        )
        for member in mads_members:
            if "@id" in member:
                uri = member["@id"]
                if uri.startswith("http://id.loc.gov/authorities/classification/"):
                    member_uris.add(uri)

        # Check for SKOS collection members
        skos_members = item.get("http://www.w3.org/2004/02/skos/core#member", [])
        for member in skos_members:
            if "@id" in member:
                uri = member["@id"]
                if uri.startswith("http://id.loc.gov/authorities/classification/"):
                    member_uris.add(uri)

        # Check for MADS scheme members (top-level)
        scheme_members = item.get(
            "http://www.loc.gov/mads/rdf/v1#hasMADSSchemeMember", []
        )
        for member in scheme_members:
            if "@id" in member:
                uri = member["@id"]
                if uri.startswith("http://id.loc.gov/authorities/classification/"):
                    member_uris.add(uri)

        # Check for narrower authority links (for deeper traversal)
        if include_narrower:
            narrower_members = item.get(
                "http://www.loc.gov/mads/rdf/v1#hasNarrowerAuthority", []
            )
            for member in narrower_members:
                if "@id" in member:
                    uri = member["@id"]
                    if uri.startswith("http://id.loc.gov/authorities/classification/"):
                        member_uris.add(uri)

    return sorted(member_uris)


def download_classification(
    session: requests.Session,
    classification_id: str,
    output_dir: Path,
    dry_run: bool = False,
) -> Optional[list]:
    """
    Download a single classification JSON file.

    Args:
        session: requests Session object
        classification_id: Classification ID (e.g., "A", "AC1-AC1100")
        output_dir: Directory to save files
        dry_run: If True, don't actually download

    Returns:
        Parsed JSON data if downloaded, None if skipped or failed
    """
    filename = get_safe_filename(classification_id)
    output_path = output_dir / filename

    # Check if file already exists
    if output_path.exists():
        logger.debug(f"Skipping {classification_id} (already exists)")
        # Load and return existing data for member extraction
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
        return None

    if dry_run:
        logger.info(f"[DRY RUN] Would download: {classification_id}")
        return None

    # Construct URL
    url = f"{BASE_URL}/{classification_id}.json"
    logger.info(f"Downloading: {classification_id}")

    # Download with retry
    data = download_with_retry(session, url)
    if data is None:
        return None

    # Save to file
    if save_json(data, output_path):
        logger.debug(f"Saved: {output_path}")
        return data

    return None


def crawl_classifications(
    session: requests.Session,
    output_dir: Path,
    max_depth: int = DEFAULT_MAX_DEPTH,
    dry_run: bool = False,
) -> dict:
    """
    Crawl and download LCC classifications to specified depth.

    Downloads:
    - Root classification scheme (depth 0)
    - Top-level classes A-Z (depth 1)
    - Subclass ranges like AC1-AC1100 (depth 2)
    - Deeper subdivisions if max_depth > 2

    Args:
        session: requests Session object
        output_dir: Directory to save files
        max_depth: Maximum depth to crawl (default: 2)
        dry_run: If True, don't actually download

    Returns:
        Statistics dictionary
    """
    stats = {
        "downloaded": 0,
        "skipped": 0,
        "failed": 0,
        "total_discovered": 0,
    }

    # For depths > 2, we need to follow hasNarrowerAuthority links
    include_narrower = max_depth > 2

    # Queue of (classification_id, depth) tuples
    queue: list[tuple[str, int]] = [
        ("", 0)
    ]  # Empty string = root classification scheme
    visited: set[str] = set()

    while queue:
        classification_id, depth = queue.pop(0)

        # Skip if already visited
        if classification_id in visited:
            continue
        visited.add(classification_id)

        # Stop at max depth
        if depth > max_depth:
            continue

        # For root, we need to use the base URL without an ID
        if not classification_id:
            url = f"{BASE_URL}.json"
            filename = "classification.json"
            output_path = output_dir / filename

            if output_path.exists():
                logger.debug("Skipping root classification (already exists)")
                stats["skipped"] += 1
                try:
                    with open(output_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (OSError, json.JSONDecodeError):
                    data = None
            elif dry_run:
                logger.info("[DRY RUN] Would download: root classification")
                data = None
            else:
                logger.info("Downloading: root classification")
                data = download_with_retry(session, url)
                if data:
                    if save_json(data, output_path):
                        stats["downloaded"] += 1
                    else:
                        stats["failed"] += 1
                        data = None
                else:
                    stats["failed"] += 1
        else:
            # Download the classification
            output_path = output_dir / get_safe_filename(classification_id)
            if output_path.exists():
                stats["skipped"] += 1
                try:
                    with open(output_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (OSError, json.JSONDecodeError):
                    data = None
            else:
                data = download_classification(
                    session, classification_id, output_dir, dry_run
                )
                if data:
                    stats["downloaded"] += 1
                elif not dry_run:
                    stats["failed"] += 1

        # Extract member URIs and add to queue (only if within depth limit)
        if data and depth < max_depth:
            member_uris = extract_member_uris(data, include_narrower=include_narrower)
            for uri in member_uris:
                member_id = extract_classification_id(uri)
                if member_id not in visited:
                    queue.append((member_id, depth + 1))
                    stats["total_discovered"] += 1

        # Log progress periodically
        if (stats["downloaded"] + stats["skipped"]) % 100 == 0:
            logger.info(
                f"Progress: {stats['downloaded']} downloaded, "
                f"{stats['skipped']} skipped, {stats['failed']} failed, "
                f"{len(queue)} in queue"
            )

    return stats


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create output directory
    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir.absolute()}")

    # Create session
    session = create_session()

    # Start crawling
    logger.info(
        f"Starting LCC classification download (max depth: {args.max_depth})..."
    )
    if args.dry_run:
        logger.info("DRY RUN MODE - no files will be downloaded")

    try:
        stats = crawl_classifications(
            session,
            output_dir,
            max_depth=args.max_depth,
            dry_run=args.dry_run,
        )
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        return 1

    # Print summary
    logger.info("=" * 50)
    logger.info("Download complete!")
    logger.info(f"  Downloaded: {stats['downloaded']}")
    logger.info(f"  Skipped (existing): {stats['skipped']}")
    logger.info(f"  Failed: {stats['failed']}")
    logger.info(f"  Total discovered: {stats['total_discovered']}")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
