import ipaddress
import logging
from typing import Optional, Tuple
from urllib.parse import urlparse

import puremagic
import requests

"""
Utilities for safely downloading media files to memory.

This module provides functions for downloading media files from URLs
and handling them in memory with validation and error handling.
"""
DOWNLOAD_CHUNK_SIZE_BYTES = 16 * 1024
DOWNLOAD_DATA_TIMEOUT_SECONDS = 120
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB default limit


logger = logging.getLogger(__name__)


class MediaDownloadException(Exception):
    def __init__(self, message: str = 'Error occurred while downloading media file.') -> None:
        self.message = message
        super().__init__(self.message)


class InvalidURLException(MediaDownloadException):
    pass


class SSRFProtectionException(MediaDownloadException):
    pass


class FileSizeExceededException(MediaDownloadException):
    pass


def _is_private_ip(ip_str: str) -> bool:
    """
    Check if an IP address is private, localhost, or reserved.

    :param ip_str: IP address as string
    :return: True if IP is private/reserved, False otherwise
    """
    ip = ipaddress.ip_address(ip_str)
    is_private = (
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast
    )
    return is_private


def _validate_url_safety(url: str) -> None:
    """
    Validate URL for security issues before downloading.

    :param url: The URL to validate
    :raises InvalidURLException: If URL scheme is not allowed
    :raises SSRFProtectionException: If URL points to private/internal network
    """
    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        raise InvalidURLException(
            f'Invalid URL scheme "{parsed.scheme}" is not allowed. Only http/https are permitted. '
            f'URL: {url}'
        )

    # Check for SSRF - block private IPs
    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLException(f'URL must have a valid hostname. URL: {url}')

    normalized_hostname = hostname.rstrip('.').lower()
    if (
        normalized_hostname == 'localhost'
        or normalized_hostname.endswith('.localhost')
        or normalized_hostname == 'localhost.localdomain'
    ):
        raise SSRFProtectionException(
            f'Access to private/internal IP addresses is not allowed: {hostname}. URL: {url}'
        )

    # Check if hostname is an IP address and validate it
    try:
        ip = ipaddress.ip_address(hostname)
        if _is_private_ip(str(ip)):
            raise SSRFProtectionException(
                f'Access to private/internal IP addresses is not allowed: {hostname}. URL: {url}'
            )
    except ValueError:
        pass


def _validate_content_length(content_length: Optional[str], max_size: int) -> None:
    if content_length:
        try:
            size = int(content_length)
            if size > max_size:
                raise FileSizeExceededException(
                    f'File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes).'
                )
        except ValueError:
            pass
    else:
        logger.info('No content-length header present, skipping pre-download size check')


def download_file_bytes_with_mime_type(
    url: str,
    max_size: int = MAX_FILE_SIZE_BYTES,
) -> Tuple[bytes, str]:
    """
    Downloads a file from a given URL and returns the file data as bytes along with the MIME type.
    MIME type is identified based on file signatures using puremagic.

    :param url: The URL of the file to be downloaded
    :param max_size: Maximum allowed file size in bytes (default: 100MB)
    :return: A tuple containing the file data as bytes and the MIME type as a string
    """
    file_data = safe_download_file_bytes_from_url(url, max_size=max_size)
    mime_type = puremagic.from_string(file_data, mime=True)
    return file_data, mime_type


def safe_download_file_bytes_from_url(
    url: str,
    chunk_size: int = DOWNLOAD_CHUNK_SIZE_BYTES,
    timeout: int = DOWNLOAD_DATA_TIMEOUT_SECONDS,
    max_size: int = MAX_FILE_SIZE_BYTES,
) -> bytes:
    """
    Safely downloads a file from a given URL with security validations.

    Performs the following safety checks:
    - URL scheme validation (only http/https)
    - SSRF protection (blocks private/internal IPs)
    - SSL certificate verification (for HTTPS URLs)
    - File size limits (both header check and streaming enforcement)

    :param url: The URL of the file to be downloaded
    :param chunk_size: Size of chunks to read in bytes (default: 16KB)
    :param timeout: Request timeout in seconds (default: 120s)
    :param max_size: Maximum allowed file size in bytes (default: 100MB)

    :return: The file data as bytes
    :raises InvalidURLException: If URL is invalid or uses disallowed scheme
    :raises SSRFProtectionException: If URL points to private/internal network
    :raises FileSizeExceededException: If file size exceeds limit
    :raises requests.HTTPError: If the HTTP request fails
    """
    _validate_url_safety(url)
    response = requests.get(url, stream=True, timeout=timeout, verify=True)
    response.raise_for_status()

    content_length = response.headers.get('Content-Length')
    _validate_content_length(content_length, max_size)

    chunks = []
    total_size = 0
    for chunk in response.iter_content(chunk_size=chunk_size):
        chunks.append(chunk)
        total_size += len(chunk)
        if total_size > max_size:
            raise FileSizeExceededException(
                f'File size exceeded maximum allowed size ({max_size} bytes) during download.'
            )
    return b''.join(chunks)
