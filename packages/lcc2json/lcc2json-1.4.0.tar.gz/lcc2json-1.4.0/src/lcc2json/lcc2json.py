#!/usr/bin/env python3
"""Extract LCC (Library of Congress Classification) outlines from downloaded JSON files.

This script processes JSON files downloaded from id.loc.gov and produces
a unified LCC classification file (lcc.json).
"""

import argparse
import json
import re
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict, field_serializer


def _serialize_number(value: float) -> int | float:
    """Serialize a number, converting to int if it's a whole number."""
    if value == int(value):
        return int(value)
    return value


class Classification(BaseModel):
    """A single LCC classification entry."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = ""
    parents: list[str] = Field(default_factory=list)
    prefix: str
    start: float
    stop: float
    subject: str
    scope_note: str | None = None

    @field_serializer("start", "stop")
    @staticmethod
    def serialize_numbers(value: float) -> int | float:
        """Serialize start/stop as int when they are whole numbers."""
        return _serialize_number(value)


# JSON-LD property URIs
MADS_AUTH_LABEL = "http://www.loc.gov/mads/rdf/v1#authoritativeLabel"
MADS_BROADER = "http://www.loc.gov/mads/rdf/v1#hasBroaderAuthority"
MADS_NARROWER = "http://www.loc.gov/mads/rdf/v1#hasNarrowerAuthority"
MADS_CODE = "http://www.loc.gov/mads/rdf/v1#code"
MADS_SCOPE_NOTE = "http://www.loc.gov/mads/rdf/v1#scopeNote"
SKOS_SCOPE_NOTE = "http://www.w3.org/2004/02/skos/core#scopeNote"
SKOS_MEMBER = "http://www.w3.org/2004/02/skos/core#member"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
RDFS_COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"
RDF_TYPE = "@type"
LCC_CLASS_NUMBER = "http://id.loc.gov/ontologies/lcc#ClassNumber"
LCC_RANGE = "http://id.loc.gov/ontologies/lcc#Range"
MADS_COLLECTION = "http://www.loc.gov/mads/rdf/v1#MADSCollection"
CLASSIFICATION_BASE = "http://id.loc.gov/authorities/classification/"


def extract_id(uri: str) -> str:
    """Extract classification ID from a full URI.

    Args:
        uri: Full URI like "http://id.loc.gov/authorities/classification/AC999"

    Returns:
        Short ID like "AC999"
    """
    if uri.startswith(CLASSIFICATION_BASE):
        return uri[len(CLASSIFICATION_BASE) :]
    return uri


def parse_lcc_code(code: str) -> tuple[str, float, float] | None:
    """Parse an LCC code into prefix, start, and stop values.

    Args:
        code: The LCC code string (e.g., "AC999", "AC1-AC1100", "F1170.52").

    Returns:
        Tuple of (prefix, start, stop) or None if parsing fails.
    """
    # Remove brackets and parentheses from around the entire code
    working_code = code
    if working_code.startswith("[") and working_code.endswith("]"):
        working_code = working_code[1:-1]
    elif working_code.startswith("(") and working_code.endswith(")"):
        working_code = working_code[1:-1]

    # Extract prefix (letters at the start)
    prefix_match = re.match(r"^([A-Z]+)", working_code)
    if not prefix_match:
        return None
    prefix = prefix_match.group(1)

    # Get the rest after the prefix
    rest = working_code[len(prefix) :]

    # Handle range codes like "1-AC1100" or "1-1100"
    if "-" in rest:
        parts = rest.split("-")

        # Parse first part (number after prefix)
        first_match = re.match(r"^([0-9]+(?:\.[0-9]+)?)", parts[0])
        if not first_match:
            return None
        start = float(first_match.group(1))

        # Parse second part (may have prefix repeated or just number)
        second_part = parts[1]

        # Remove prefix if repeated (e.g., "AC1100" -> "1100")
        if second_part.startswith(prefix):
            second_part = second_part[len(prefix) :]

        # Handle decimal shorthand (e.g., ".52" means same integer + .52)
        if second_part.startswith("."):
            int_part = int(start)
            try:
                stop = float(str(int_part) + second_part)
            except ValueError:
                return None
        else:
            # Extract numeric portion
            second_match = re.match(r"^([0-9]+(?:\.[0-9]+)?)", second_part)
            if second_match:
                stop = float(second_match.group(1))
            else:
                stop = start

        # Ensure start <= stop
        if stop < start:
            start, stop = stop, start

        return prefix, start, stop
    else:
        # Single number (no range)
        num_match = re.match(r"^([0-9]+(?:\.[0-9]+)?)", rest)
        if num_match:
            num = float(num_match.group(1))
            return prefix, num, num
        # Handle top-level classifications (just letters, no numbers)
        # e.g., "A", "B", "BC" - these represent the entire range for that prefix
        if rest == "":
            return prefix, 0, float("inf")
        return None


def get_label(item: dict) -> str:
    """Extract the subject label from a JSON-LD item.

    Prefers authoritativeLabel, falls back to rdfs:comment (for top-level
    classifications), then rdfs:label.

    Args:
        item: JSON-LD item dictionary

    Returns:
        Subject label string
    """
    # Try authoritativeLabel first (short form)
    auth_labels = item.get(MADS_AUTH_LABEL, [])
    if auth_labels:
        return auth_labels[0].get("@value", "")

    # For top-level classifications (MADSCollection), use rdfs:comment
    # which contains the actual subject like "B -- PHILOSOPHY. PSYCHOLOGY. RELIGION"
    types = item.get(RDF_TYPE, [])
    if MADS_COLLECTION in types:
        comments = item.get(RDFS_COMMENT, [])
        if comments:
            comment = comments[0].get("@value", "").strip()
            # Extract subject from format like "B -- PHILOSOPHY. PSYCHOLOGY. RELIGION"
            if "--" in comment:
                return comment.split("--", 1)[1].strip()
            return comment

    # Fall back to rdfs:label (may be full breadcrumb)
    rdfs_labels = item.get(RDFS_LABEL, [])
    if rdfs_labels:
        label = rdfs_labels[0].get("@value", "")
        # If it's a breadcrumb path, extract the last part
        if "--" in label:
            return label.split("--")[-1].strip()
        return label

    return ""


def get_scope_note(item: dict) -> str | None:
    """Extract scope note from a JSON-LD item.

    Checks both MADS and SKOS scope note properties.

    Args:
        item: JSON-LD item dictionary

    Returns:
        Scope note string or None if not present
    """
    # Try SKOS scope note first (more standard)
    skos_notes = item.get(SKOS_SCOPE_NOTE, [])
    if skos_notes:
        note = skos_notes[0].get("@value", "")
        if note:
            return note.strip()

    # Fall back to MADS scope note
    mads_notes = item.get(MADS_SCOPE_NOTE, [])
    if mads_notes:
        note = mads_notes[0].get("@value", "")
        if note:
            return note.strip()

    return None


def get_broader_ids(item: dict) -> list[str]:
    """Extract parent classification IDs from a JSON-LD item.

    Args:
        item: JSON-LD item dictionary

    Returns:
        List of parent classification IDs
    """
    broader = item.get(MADS_BROADER, [])
    parents = []
    for b in broader:
        uri = b.get("@id", "")
        if uri.startswith(CLASSIFICATION_BASE):
            parents.append(extract_id(uri))
    return parents


def get_narrower_ids(item: dict) -> list[str]:
    """Extract child classification IDs from a JSON-LD item.

    This extracts the hasNarrowerAuthority relationships, which define
    the authoritative parent-child relationships in the LCC hierarchy.

    Args:
        item: JSON-LD item dictionary

    Returns:
        List of child classification IDs
    """
    narrower = item.get(MADS_NARROWER, [])
    children = []
    for n in narrower:
        uri = n.get("@id", "")
        if uri.startswith(CLASSIFICATION_BASE):
            children.append(extract_id(uri))
    return children


def get_member_ids(item: dict) -> list[str]:
    """Extract member classification IDs from a JSON-LD item.

    This extracts the skos:member relationships, which define
    the membership relationships for top-level collections (A, B, C, etc.).

    Args:
        item: JSON-LD item dictionary

    Returns:
        List of member classification IDs
    """
    members = item.get(SKOS_MEMBER, [])
    result = []
    for m in members:
        uri = m.get("@id", "")
        if uri.startswith(CLASSIFICATION_BASE):
            result.append(extract_id(uri))
    return result


def is_classification_entry(item: dict) -> bool:
    """Check if a JSON-LD item is a classification entry.

    Args:
        item: JSON-LD item dictionary

    Returns:
        True if this is a classification entry
    """
    item_id = item.get("@id", "")
    if not item_id.startswith(CLASSIFICATION_BASE):
        return False

    # Must have a type
    types = item.get(RDF_TYPE, [])
    if not types:
        return False

    # Accept ClassNumber or Range types, or Authority/Concept with a label
    if LCC_CLASS_NUMBER in types or LCC_RANGE in types:
        return True

    # Also accept items that have labels (some entries use Authority/Concept type)
    if item.get(MADS_AUTH_LABEL) or item.get(RDFS_LABEL):
        return True

    return False


def process_json_file(
    json_path: Path, include_scope: bool = False
) -> tuple[list[tuple[str, Classification]], dict[str, str], dict[str, str]]:
    """Process a single JSON file and extract classifications.

    Args:
        json_path: Path to the JSON file
        include_scope: Whether to include scope notes in the output

    Returns:
        Tuple of:
        - List of (id, Classification) tuples
        - Dict mapping child_id -> parent_id (from hasNarrowerAuthority)
        - Dict mapping member_id -> collection_id (from skos:member)
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    classifications = []
    narrower_map: dict[str, str] = {}  # child_id -> parent_id
    member_map: dict[str, str] = {}  # member_id -> collection_id

    for item in data:
        # Extract narrower relationships from ALL items (not just classification entries)
        # This captures the authoritative parent-child relationships
        item_id = item.get("@id", "")
        if item_id.startswith(CLASSIFICATION_BASE):
            parent_id = extract_id(item_id)
            narrower_ids = get_narrower_ids(item)
            for child_id in narrower_ids:
                # Map each child to this parent
                narrower_map[child_id] = parent_id

            # Extract skos:member relationships (for top-level collections)
            # This captures the membership relationships like P -> PQ1-PQ3999
            member_ids = get_member_ids(item)
            for member_id in member_ids:
                # Map each member to this collection
                member_map[member_id] = parent_id

        if not is_classification_entry(item):
            continue

        # Extract ID
        item_id = extract_id(item.get("@id", ""))
        if not item_id:
            continue

        # Get subject label
        subject = get_label(item)
        if not subject:
            continue

        # Parse the code
        parsed = parse_lcc_code(item_id)
        if not parsed:
            continue

        prefix, start, stop = parsed

        # Get parent links from hasBroaderAuthority
        parents = get_broader_ids(item)

        # Get scope note if requested
        scope_note = get_scope_note(item) if include_scope else None

        classifications.append(
            (
                item_id,
                Classification(
                    id=item_id,
                    parents=parents,
                    prefix=prefix,
                    start=start,
                    stop=stop,
                    subject=subject,
                    scope_note=scope_note,
                ),
            )
        )

    return classifications, narrower_map, member_map


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract LCC outlines from downloaded JSON files."
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=str,
        default="json",
        help="Directory containing JSON files (default: json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="lcc.json",
        help="Output file path (default: lcc.json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--ranges",
        action="store_true",
        help="Include start/stop/prefix range fields in output (larger file size)",
    )
    parser.add_argument(
        "--scope",
        action="store_true",
        help="Include scope notes in output (when available)",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        print("Run download_json.py first to download the JSON files.")
        return

    # Collect all classifications, narrower mappings, and member mappings
    all_classifications: dict[str, list[Classification]] = {}
    global_narrower_map: dict[str, str] = {}  # child_id -> parent_id
    global_member_map: dict[str, str] = {}  # member_id -> collection_id
    seen_ids: set[str] = set()
    total_files = 0
    total_entries = 0

    # Process all JSON files
    json_files = sorted(input_dir.glob("*.json"))

    # Skip the root classification file (it's just an index)
    skip_files = {"classification.json"}

    for json_path in json_files:
        if json_path.name in skip_files:
            continue

        if args.verbose:
            print(f"Processing: {json_path.name}")

        total_files += 1

        try:
            classifications, narrower_map, member_map = process_json_file(
                json_path, include_scope=args.scope
            )
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error processing {json_path}: {e}")
            continue

        # Merge narrower mappings (child -> parent relationships)
        global_narrower_map.update(narrower_map)

        # Merge member mappings (member -> collection relationships from skos:member)
        global_member_map.update(member_map)

        for item_id, classification in classifications:
            # Skip duplicates (same ID might appear in multiple files)
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            prefix = classification.prefix
            if prefix not in all_classifications:
                all_classifications[prefix] = []
            all_classifications[prefix].append(classification)
            total_entries += 1

    # Sort entries within each prefix by start value
    for prefix in all_classifications:
        all_classifications[prefix].sort(key=lambda c: (c.start, c.stop))

    if args.verbose:
        print(
            f"Built narrower map with {len(global_narrower_map)} child->parent relationships"
        )
        print(
            f"Built member map with {len(global_member_map)} member->collection relationships"
        )

    # Build a lookup for all classifications by ID
    all_entries_by_id: dict[str, Classification] = {}
    for prefix, classifications in all_classifications.items():
        for classification in classifications:
            all_entries_by_id[classification.id] = classification

    # Set parent relationships using hasNarrowerAuthority first (authoritative),
    # then skos:member (for top-level collection membership),
    # then fall back to range-based computation
    for prefix, classifications in all_classifications.items():
        for i, classification in enumerate(classifications):
            # First, check if this entry has an explicit parent from hasNarrowerAuthority
            if classification.id in global_narrower_map:
                immediate_parent = global_narrower_map[classification.id]

                # Build the full parent chain by walking up the hierarchy
                parent_chain = []
                current = classification.id
                while current in global_narrower_map:
                    parent = global_narrower_map[current]
                    parent_chain.append(parent)
                    current = parent

                # Reverse to get most general first (matches existing format)
                parent_chain.reverse()
                classification.parents = parent_chain
                continue

            # Skip if we already have parents from hasBroaderAuthority in the JSON data
            if classification.parents:
                continue

            # Check if this entry is a member of a top-level collection (via skos:member)
            # This handles cases like P -> PQ1-PQ3999, E -> E11-E143, B -> BC1-BC199
            if classification.id in global_member_map:
                collection_id = global_member_map[classification.id]
                classification.parents = [collection_id]
                continue

            # Fall back to range-based computation for entries without explicit relationships
            # Find all valid parents (ranges that contain this entry)
            valid_parents = []
            for j, other in enumerate(classifications):
                # Can't be parent of itself
                if i == j:
                    continue

                # Parent must start at or before this entry
                if classification.start < other.start:
                    continue

                # Parent must end at or after this entry
                if classification.stop > other.stop:
                    continue

                # If same range, earlier entry is not a parent of later entry
                if (
                    classification.start == other.start
                    and classification.stop == other.stop
                    and j > i
                ):
                    continue

                valid_parents.append((other.start, other.stop, other.id))

            # Sort parents by start (ascending) then stop (descending) to get hierarchy
            valid_parents.sort(key=lambda x: (x[0], -x[1]))
            classification.parents = [p[2] for p in valid_parents]

    # Convert to serializable format
    # Build exclude set based on options
    exclude_fields: set[str] = set()
    if not args.ranges:
        exclude_fields.update({"start", "stop", "prefix"})
    if not args.scope:
        exclude_fields.add("scope_note")

    output_data = {
        prefix: [
            cls.model_dump(exclude=exclude_fields, exclude_none=True)
            for cls in classifications
        ]
        for prefix, classifications in sorted(all_classifications.items())
    }

    # Write output
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Processed {total_files} files")
    print(f"Extracted {total_entries} classification entries")
    print(f"Found {len(all_classifications)} unique prefixes")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
