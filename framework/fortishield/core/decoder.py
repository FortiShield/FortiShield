# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
from enum import Enum

from fortishield.core import common
from fortishield.core.exception import FortishieldError, FortishieldInternalError
from fortishield.core.utils import load_fortishield_xml, add_dynamic_detail

REQUIRED_FIELDS = ['filename', 'position']
SORT_FIELDS = ['filename', 'relative_dirname', 'name', 'position', 'status']
DYNAMIC_OPTIONS = {'program_name', 'prematch', 'regex'}
DECODER_FIELDS = ['filename', 'relative_dirname', 'name', 'position', 'status', 'details']
DECODER_FILES_FIELDS = ['filename', 'relative_dirname', 'status']
DECODER_FILES_REQUIRED_FIELDS = ['filename']


class Status(Enum):
    S_ENABLED = 'enabled'
    S_DISABLED = 'disabled'
    S_ALL = 'all'


def add_detail(detail: str, value: str, details: dict):
    """Add a decoder detail (i.e. regex, order, prematch, etc.).

    Parameters
    ----------
    detail : str
        Detail name.
    value : str
        Detail value.
    details : dict
        Details dict.
    """
    # We return regex detail in an array
    if detail == 'regex':
        if detail in details:
            details[detail].append(value)
        else:
            details[detail] = [value]
    else:
        details[detail] = value


def check_status(status: str) -> str:
    """Validate status with the Status class.

    Parameter
    ---------
    status : str
        Status to be validated.

    Raises
    ------
    FortishieldError(1202)
        Argument \'status\' must be: enabled, disabled or all.
    """
    if status is None:
        return Status.S_ALL.value
    elif status in [Status.S_ALL.value, Status.S_ENABLED.value, Status.S_DISABLED.value]:
        return status
    else:
        raise FortishieldError(1202)


def load_decoders_from_file(decoder_file: str, decoder_path: str, decoder_status: str) -> list:
    """Load decoders from file.

    Parameters
    ----------
    decoder_file : str
        Name of the decoder file.
    decoder_path : str
        Path to the decoder file.
    decoder_status : str
        Decoder status.

    Raises
    ------
    FortishieldError(1502)
        Error reading decoders file (permissions).
    FortishieldInternalError(1501)
        Generic error reading decoders file.

    Returns
    -------
    list
        List containing the decoders.
    """
    try:
        decoders = list()
        position = 0
        root = load_fortishield_xml(os.path.join(common.FORTISHIELD_PATH, decoder_path, decoder_file))

        for xml_decoder in list(root):
            # New decoder
            if xml_decoder.tag.lower() == "decoder":
                decoder = {'filename': decoder_file, 'relative_dirname': decoder_path, 'status': decoder_status,
                           'name': xml_decoder.attrib['name'], 'position': position, 'details': dict()}
                position += 1

                for k in xml_decoder.attrib:
                    if k != 'name':
                        decoder['details'][k] = xml_decoder.attrib[k]

                for xml_decoder_tags in list(xml_decoder):
                    tag = xml_decoder_tags.tag.lower()
                    value = xml_decoder_tags.text
                    attribs = xml_decoder_tags.attrib
                    if tag in DYNAMIC_OPTIONS:
                        add_dynamic_detail(tag, value, attribs, decoder['details'])
                    else:
                        decoder['details'][tag] = value
                decoders.append(decoder)
    except OSError:
        raise FortishieldError(1502, extra_message=os.path.join('FORTISHIELD_HOME', decoder_path, decoder_file))
    except Exception:
        raise FortishieldInternalError(1501, extra_message=os.path.join('FORTISHIELD_HOME', decoder_path, decoder_file))

    return decoders