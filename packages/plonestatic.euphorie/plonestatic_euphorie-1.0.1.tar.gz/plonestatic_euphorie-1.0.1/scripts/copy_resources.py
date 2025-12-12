#!/usr/bin/env python3
from itertools import chain
from pathlib import Path
from shutil import copy

import logging
import re
import sys


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("plonestatic.euphorie")

PROTO_PATH = Path("var/prototype/_site")
RESOURCES_DIR = Path("src/plonestatic/euphorie/resources")

# Regexp to match the links to the resources
resources_pattern = re.compile(r'(/(?:media|style|feedback)/[^\'"\s:\)\?#]+)')

# Regexp to match the font filenames in the fontello.css
font_pattern = re.compile(r"url\(['\"]?.*/([^/?#]+)")

# This list all the resources that are known to be linked
# but are not actually present in prototype
known_bogus_resources = {
    "feedback/messages-unread",
    "style/fonts/roboto-condensed/RobotoCondensed-Bold.svg",
    "style/fonts/roboto-condensed/RobotoCondensed-Light.svg",
}

# We set up some limits for the resources directory size after the copy
# operation.
# This is to make sure that:
#
# 1. we don't miss anything
# 2. we don't check in too many files
#
MINIMUM_EXPECTED_SIZE = 30  # MB
MAXIMUM_EXPECTED_SIZE = 40  # MB


def extract_resources(text):
    """Extract the relative paths of the resources linked in the text."""
    return {match.group(0).lstrip("/") for match in resources_pattern.finditer(text)}


def run():
    """Be sure that all the resources linked by the files html and css files
    in the resources directory will be copied from the prototype directory.

    This includes, e.g:

    - images
    - html files
    - fonts
    """
    if not PROTO_PATH.exists():
        logger.error("Run `make jekyll` first.")
        sys.exit(1)

    if not RESOURCES_DIR.exists():
        logger.error("Run `make resource-install` first.")
        sys.exit(1)

    required_resources = set()

    for filepath in chain(
        RESOURCES_DIR.rglob("*.css"),
        RESOURCES_DIR.rglob("*.html"),
    ):
        # We want to use the Plone provided plone.patternslib > 1,
        # which is a dependency of this package
        #
        text = re.sub(
            r"assets/oira/script/.*bundle.min.js",
            "++resource++patternslib/bundle.min.js",
            filepath.read_text()
        )

        # parse the file for the resources it links
        if filepath.parent.stem != "illustrations":
            # Everything that lives under illustrations
            # does not require extracting the resources
            required_resources.update(extract_resources(text))

        text = text.replace(
            "/assets/",
            "/++resource++euphorie.resources/assets/",
        ).replace(
            "/media/",
            "++resource++euphorie.resources/media/",
        )
        # write the text back to the file
        filepath.write_text(text)

    for resource in sorted(required_resources):
        # Resource in the style/flags directory are treated differently.
        if not resource.startswith("style/flags/"):
            if resource.startswith("style/"):
                source = PROTO_PATH / "assets" / "oira" / resource
                target = RESOURCES_DIR / "assets" / "oira" / resource
            else:
                source = PROTO_PATH / resource
                target = RESOURCES_DIR / resource

            if not source.exists():
                if resource not in known_bogus_resources:
                    logger.error("Missing resource: %r", resource)

                continue

            if resource in known_bogus_resources:
                logger.warning(
                    "The resource %r was found, you might want to remove it from the `known_bogus_resources` variable",  # noqa: E501
                    resource,
                )

        if not target.parent.exists():
            logger.info("Creating directory %r", target.parent)
            target.parent.mkdir(parents=True)
        copy(source, target)

        logger.info("Copied %r", resource)

    # Find and copy the fontello css and include the fontello font files
    fontellos = (RESOURCES_DIR / "assets" / "oira" / "style").rglob("fontello.css")
    for fontello in fontellos:
        text = fontello.read_text()
        font_filenames = {match.group(1) for match in font_pattern.finditer(text)}
        for font_filename in font_filenames:
            source = (
                PROTO_PATH
                / fontello.parent.parent.relative_to(RESOURCES_DIR)
                / "font"
                / font_filename
            )
            target = fontello.parent.parent / "font" / font_filename
            if not target.parent.exists():
                target.parent.mkdir(parents=True)
            copy(source, target)
            logger.info("Copied %s", font_filename)

    # Finally perform a sanity check on the resources directory size
    size = int(
        sum(f.stat().st_size for f in RESOURCES_DIR.rglob("*") if f.is_file())
        / 1024
        / 1024
    )
    if size < MINIMUM_EXPECTED_SIZE:
        logger.error(
            (
                "The resources directory is less than %r MB. "
                "The minimum expected size is %r MB. "
            ),
            size,
            MINIMUM_EXPECTED_SIZE,
        )
    if size > MAXIMUM_EXPECTED_SIZE:
        logger.warning(
            (
                "The resources directory is more than %r MB. "
                "The maximum expected size is %r MB. "
            ),
            size,
            MAXIMUM_EXPECTED_SIZE,
        )


if __name__ == "__main__":
    run()
