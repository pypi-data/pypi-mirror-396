#!/usr/bin/env python3
from pathlib import Path
from lxml import etree
from functools import partial
import logging
import tempfile
import requests
import shutil

ID_SEPARATOR = ":"
NSMAP = {
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
}
OUT_DIR = Path("./documents2")
TIMEOUT = 30

def download_to_file(url, file_name, logger=None):
    if logger is None:
        logger = logging
    logger.info(f"Download: {url}")
    try:
        result = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        result.raise_for_status()
    except requests.ConnectionError as e:
        logger.warning("No Connection.")
        raise e
    except requests.exceptions.HTTPError as e:
        logging.warning(f"HTTP error {e}")
        return
    if file_name.exists():
        logger.info(f"Skip existing file: {file_name}")
        return
    with tempfile.NamedTemporaryFile() as fh:
        fh.write(result.content)
        shutil.copyfile(fh.name, file_name)


def dispatch(batch, logger=None, meta=None):
    root = batch.xml.getroottree()
    out_dir = OUT_DIR
    out_dir.mkdir(exist_ok=True)
    for record in root.xpath("//oai:record", namespaces=NSMAP):
        identifier = record.xpath("./oai:header/oai:identifier", namespaces=NSMAP)[
            0
        ].text
        numeral_identifier = identifier.split(ID_SEPARATOR)[-1]
        identifiers = record.xpath(
            "./oai:metadata/oai_dc:dc/dc:identifier", namespaces=NSMAP
        )
        if identifiers:
            pdf_links = [
                identifier.text
                for identifier in identifiers
                if identifier.text.lower().endswith(".pdf")
            ]
        else:
            pdf_links = []
        folder = out_dir / Path(numeral_identifier)
        folder.mkdir(exist_ok=True)
        with (folder / f"{numeral_identifier}_metadata.xml").open("wb") as fh:
            fh.write(
                etree.tostring(
                    record, pretty_print=True, xml_declaration=True, encoding="utf-8"
                )
            )
        if pdf_links:
            for pdf_link in pdf_links:
                name = Path(pdf_link).name
                download_to_file(pdf_link, folder / name, logger=logger)


