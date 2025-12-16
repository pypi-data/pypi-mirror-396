import re
import logging
from re import Pattern, Match
from dataclasses import dataclass

logger = logging.getLogger()

CODE_BLOCK_PATTERN = re.compile(r"```(?P<content>[\s\S]*?)```")
INLINE_CODE_PATTERN = re.compile(r"`(?P<content>[^`\n]+)`")

# Basic Markdown references
BASIC_REFERENCE_PATTERN = re.compile(r"!*\[(?P<text>[^\]]+)\]\((?P<link>[^)]+)\)")  # []() and ![]()
BASIC_IMAGE_PATTERN = re.compile(r"!\[(?P<text>[^(){}\[\]]+)\]\((?P<link>[^(){}\[\]]+)\)")  # ![]()

# Inline Links - <http://example.com>
INLINE_LINK_PATTERN = re.compile(r"<(?P<link>(?:https?://|mailto:|[a-zA-Z0-9._%+-]+@)[^>]+)>")

RAW_LINK_PATTERN = re.compile(
    r"(^| )(?:(https?://\S+))"
)  # all links that are surrounded by nothing or spaces
HTML_LINK_PATTERN = re.compile(
    r"<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1"
)  # <a href="http://example.com">

# Local File References - scripts, markdown files, and local images
HTML_IMAGE_PATTERN = re.compile(
    r"<img\s+(?:[^>]*?\s+)?src=([\"\'])(.*?)\1"
)  # <img src="image.png">


@dataclass
class Reference:
    """Data class to store reference information.

    Attributes:
        file_path: Path to the file where the reference was found.
        line_number: Line number where the reference was found.
        syntax: Syntax of the reference, e.g. `[text](link)`.
        link: The link part of the reference, e.g. `link` in `[text](link)`.
        is_remote: Whether the reference is a remote reference.
    """

    file_path: str
    line_number: int
    syntax: str
    link: str
    is_remote: bool

    def __str__(self):
        """Return a user-friendly string representation of the Reference."""
        remote_status = "Remote" if self.is_remote else "Local"
        return (
            f"Reference:\n"
            f"  File Path: {self.file_path}\n"
            f"  Line Number: {self.line_number}\n"
            f"  Syntax: {self.syntax}\n"
            f"  Link: {self.link}\n"
            f"  Status: {remote_status}"
        )


@dataclass
class ReferenceMatch:
    line_number: int
    match: Match


class MarkdownParser:
    def parse_markdown_file(self, file_path: str) -> dict[str, list[Reference]]:
        """Parse a markdown file to extract references.

        Args:
            file_path: Path to the markdown file.

        Returns:
            A dictionary containing lists of references found in the markdown file.
        """
        logger.info(f"Parsing markdown file: '{file_path}' ...")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return {}
        except IOError as e:
            print(f"Error: An I/O error occurred while reading the file {file_path}: {e}")
            return {}

        # Get all code blocks, such as ```python ... ```, or ```text``` for ensuring that found references are not part
        # of code blocks.
        logger.info("Extracting code blocks ...")
        code_blocks = self._find_matches_with_line_numbers(CODE_BLOCK_PATTERN, content)
        logger.info(f"Found {len(code_blocks)} code blocks.")

        # Get all inline code spans with backticks
        logger.info("Extracting inline code ...")
        inline_code = self._find_matches_with_line_numbers(INLINE_CODE_PATTERN, content)
        logger.info(f"Found {len(inline_code)} inline code spans.")

        # Combine code blocks and inline code for filtering
        all_code = code_blocks + inline_code

        # Get all references that look like this: [text](reference)
        logger.info("Extracting basic references ...")
        basic_reference_matches = self._find_matches_with_line_numbers(
            BASIC_REFERENCE_PATTERN, content
        )
        basic_reference_matches = [
            ref for ref in basic_reference_matches if not ref.match[0].startswith("!")
        ]
        logger.info(f"Found {len(basic_reference_matches)} basic reference matches:")
        for ref_match in basic_reference_matches:
            logger.info(ref_match.__repr__())

        basic_reference_matches = self._drop_code_references(basic_reference_matches, all_code)
        logger.info("Processing reference matches...")
        basic_references = self._process_basic_references(file_path, basic_reference_matches)

        # Get all image references that look like this: ![text](reference)
        logger.info("Extracting basic images ...")
        basic_image_matches = self._find_matches_with_line_numbers(BASIC_IMAGE_PATTERN, content)
        logger.info(f"Found {len(basic_image_matches)} basic images.")
        basic_image_matches = self._drop_code_references(basic_image_matches, all_code)
        basic_images = self._process_basic_references(file_path, basic_image_matches)

        logger.info("Extracting inline links ...")
        inline_link_matches = self._find_matches_with_line_numbers(INLINE_LINK_PATTERN, content)
        logger.info(f"Found {len(inline_link_matches)} inline links.")
        inline_link_matches = self._drop_code_references(inline_link_matches, all_code)
        inline_links = self._process_basic_references(file_path, inline_link_matches)

        return {
            "basic_references": basic_references,
            "basic_images": basic_images,
            "inline_links": inline_links,
        }

    def _drop_code_references(
        self, references: list[ReferenceMatch], code_sections: list[ReferenceMatch]
    ) -> list[ReferenceMatch]:
        """Drop references that are part of code blocks or inline code."""
        logger.info("Dropping references that are part of code blocks or inline code ...")

        # Filter out references that are inside code blocks or inline code
        filtered_references = []
        dropped_counter = 0

        for ref in references:
            is_in_code = False
            for code_section in code_sections:
                logger.debug(ref.match.group(0))

                # Check if reference is within the code section content
                if code_section.match.lastindex and code_section.match.lastindex >= 1:
                    content = code_section.match.group(1)
                    logger.debug(f"Code content: {content}")
                    if ref.match.group(0) in content:
                        logger.info(f"Dropping reference: {ref.match.group(0)}")
                        is_in_code = True
                        dropped_counter += 1
                        break

            if not is_in_code:
                filtered_references.append(ref)

        if dropped_counter > 0:
            logger.info(f"Dropped {dropped_counter} references.")
        else:
            logger.info("No code references found.")

        return filtered_references

    def _is_remote_reference(self, link: str) -> bool:
        """Check if a link is a remote reference."""
        protocol_pattern = re.compile(
            r"^([a-zA-Z][a-zA-Z\d+\-.]*):.*"
        )  # matches anything that looks like a `protocol:`
        return bool(protocol_pattern.match(link))

    def _process_basic_references(
        self, file_path: str, matches: list[ReferenceMatch]
    ) -> list[Reference]:
        """Process basic references."""
        references: list[Reference] = []
        for match in matches:
            link = match.match.group("link")
            reference = Reference(
                file_path=file_path,
                line_number=match.line_number,
                syntax=match.match.group(0),
                link=link,
                is_remote=self._is_remote_reference(link),
            )
            references.append(reference)
        return references

    def _process_inline_links(
        self, file_path: str, matches: list[ReferenceMatch]
    ) -> list[Reference]:
        """Process inline links enclosed in angle brackets.

        Handles patterns like:
        - <http://example.com>
        - <a href="https://www.example.org">Example</a>
        - <img src="https://example.com/image.png" alt="Image">
        """
        references: list[Reference] = []
        for match in matches:
            link = match.match.group("link")
            reference = Reference(
                file_path=file_path,
                line_number=match.line_number,
                syntax=match.match.group(0),
                link=link,
                is_remote=self._is_remote_reference(link),
            )
            references.append(reference)
        return references

    def _find_matches_with_line_numbers(
        self, pattern: Pattern[str], text: str
    ) -> list[ReferenceMatch]:
        """Find regex matches along with their line numbers."""
        matches_with_line_numbers = []
        for match in re.finditer(pattern, text):
            start_pos = match.start(0)
            line_number = text.count("\n", 0, start_pos) + 1
            matches_with_line_numbers.append(ReferenceMatch(line_number=line_number, match=match))
        return matches_with_line_numbers
