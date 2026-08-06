from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

MAJOR_SHARE_HOSTS = {
    "onedrive.live.com",
    "1drv.ms",
    "sharepoint.com",
    "icloud.com",
    "www.icloud.com",
    "photos.google.com",
    "box.com",
    "app.box.com",
}

IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "image/tiff",
    "image/bmp",
}


def collect_item(item: str, destination: Path, base) -> list[Path]:
    parsed = base.parse_protocol_url(item)
    if parsed:
        item = parsed

    local = Path(item.strip().strip('"'))
    if local.exists():
        return [local]

    if not item.lower().startswith(("http://", "https://")):
        raise ValueError("This does not appear to be a working link or file.")

    destination.mkdir(parents=True, exist_ok=True)
    host = urllib.parse.urlparse(item).netloc.lower()

    if "drive.google.com" in host:
        return base.download_google_drive(item, destination)
    if "dropbox.com" in host or "dropboxusercontent.com" in host:
        return [base.download_dropbox(item, destination)]
    if host == "1drv.ms" or "onedrive.live.com" in host or "sharepoint.com" in host:
        return download_onedrive(item, destination, base)
    if "icloud.com" in host:
        return download_shared_page(item, destination, base, "iCloud")
    if host == "photos.google.com":
        return download_shared_page(item, destination, base, "Google Photos")
    if host == "box.com" or host.endswith(".box.com"):
        return download_box(item, destination, base)

    return download_url_or_page(item, destination, base)


def download_onedrive(url: str, destination: Path, base) -> list[Path]:
    resolved = resolve_url(url)
    parts = urllib.parse.urlsplit(resolved)
    query = urllib.parse.parse_qs(parts.query)
    query["download"] = ["1"]
    direct = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query, doseq=True), parts.fragment)
    )
    return download_url_or_page(direct, destination, base, page_name="OneDrive")


def download_box(url: str, destination: Path, base) -> list[Path]:
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qs(parts.query)
    query["download"] = ["1"]
    direct = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query, doseq=True), parts.fragment)
    )
    return download_url_or_page(direct, destination, base, page_name="Box")


def resolve_url(url: str) -> str:
    with requests.get(url, timeout=45, allow_redirects=True, stream=True, headers=browser_headers()) as response:
        response.raise_for_status()
        return response.url


def download_url_or_page(
    url: str,
    destination: Path,
    base,
    page_name: str = "shared page",
) -> list[Path]:
    with requests.get(url, timeout=90, allow_redirects=True, stream=True, headers=browser_headers()) as response:
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()

        if content_type in IMAGE_CONTENT_TYPES or content_type in {"application/zip", "application/octet-stream"}:
            return [save_response(response, destination, base)]

        if content_type in {"text/html", "application/xhtml+xml", ""}:
            page_url = response.url
            page_text = response.text
            return download_images_from_html(page_text, page_url, destination, base, page_name)

        return [save_response(response, destination, base)]


def download_shared_page(url: str, destination: Path, base, page_name: str) -> list[Path]:
    with requests.get(url, timeout=90, allow_redirects=True, headers=browser_headers()) as response:
        response.raise_for_status()
        return download_images_from_html(response.text, response.url, destination, base, page_name)


def download_images_from_html(
    page_text: str,
    page_url: str,
    destination: Path,
    base,
    page_name: str,
) -> list[Path]:
    urls = extract_media_urls(page_text, page_url)
    downloaded: list[Path] = []

    for index, media_url in enumerate(urls[:500], start=1):
        try:
            with requests.get(
                media_url,
                timeout=90,
                allow_redirects=True,
                stream=True,
                headers={**browser_headers(), "Referer": page_url},
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                if content_type not in IMAGE_CONTENT_TYPES and content_type not in {
                    "application/zip",
                    "application/octet-stream",
                }:
                    continue
                path = save_response(response, destination, base, fallback_name=f"picture-{index}")
                if path.stat().st_size >= 8_000:
                    downloaded.append(path)
                else:
                    path.unlink(missing_ok=True)
        except requests.RequestException:
            continue

    if not downloaded:
        raise ValueError(
            f"{page_name} did not provide downloadable pictures. The link may require permission, sign-in, or a new share link."
        )
    return downloaded


def extract_media_urls(page_text: str, page_url: str) -> list[str]:
    decoded = html.unescape(page_text).replace("\\/", "/").replace("\\u0026", "&")
    soup = BeautifulSoup(decoded, "html.parser")
    candidates: list[str] = []

    for tag in soup.find_all(["img", "source", "a", "meta"]):
        for attribute in ("src", "href", "content", "data-src", "data-download-url"):
            value = tag.get(attribute)
            if value:
                candidates.append(str(value))
        srcset = tag.get("srcset")
        if srcset:
            candidates.extend(part.strip().split(" ", 1)[0] for part in str(srcset).split(","))

    candidates.extend(
        re.findall(
            r'https?://[^\s"\'<>]+?(?:\.jpe?g|\.png|\.webp|\.heic|\.heif|\.tiff?|\.bmp|/download[^\s"\'<>]*)[^\s"\'<>]*',
            decoded,
            flags=re.IGNORECASE,
        )
    )

    results: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip().strip('"\'')
        if not candidate or candidate.startswith(("data:", "blob:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(page_url, candidate)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        normalized = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
        if normalized not in seen:
            seen.add(normalized)
            results.append(normalized)
    return results


def save_response(response: requests.Response, destination: Path, base, fallback_name: str = "download") -> Path:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
    filename = base.filename_from_response(response.url, response.headers.get("content-disposition"))
    if filename == "download" and fallback_name:
        filename = fallback_name
    if not Path(filename).suffix:
        filename += base.extension_from_content_type(content_type)
    target = base.unique_path(destination / base.sanitize_filename(filename))
    with target.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 256):
            if chunk:
                file.write(chunk)
    return target


def browser_headers() -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/zip,image/avif,image/webp,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
