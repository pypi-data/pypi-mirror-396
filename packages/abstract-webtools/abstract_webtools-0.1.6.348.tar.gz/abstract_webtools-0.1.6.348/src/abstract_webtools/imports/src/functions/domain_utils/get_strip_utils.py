from ..imports import *
import os

def get_http(domain: str | None) -> str | None:
    """Return 'http' or 'https' if detected, otherwise None."""
    if not domain:
        return None
    domain = str(domain).strip()
    if domain.startswith("https"):
        return "https"
    if domain.startswith("http"):
        return "http"
    return None


def strip_http(domain: str | None, http: str | None = None) -> str | None:
    """Remove http(s):// from domain if present."""
    if not domain:
        return None
    http = http or get_http(domain)
    try:
        if http:
            domain = domain[len(http) + 3 :] if "://" in domain else domain[len(http):]
        domain = eatAll(domain, [":", "/"])
        return domain.strip()
    except Exception:
        return domain


def get_www(domain: str | None, http: str | None = None) -> bool:
    """Return True if domain starts with www."""
    if not domain:
        return False
    http = http or get_http(domain)
    domain = strip_http(domain, http)
    return bool(domain and domain.startswith("www."))


def strip_www(domain: str | None, http: str | None = None) -> str | None:
    """Remove leading www. and restore http prefix if any."""
    if not domain:
        return None
    http = http or get_http(domain)
    domain = strip_http(domain, http)
    try:
        if domain and domain.startswith("www."):
            domain = domain[len("www.") :]
        if http:
            domain = f"{http}://{domain}"
        return domain.strip()
    except Exception:
        return domain


def get_http_www(domain: str | None) -> dict:
    """Return dict with detected http and www info."""
    if not domain:
        return {"http": None, "www": False}
    http = get_http(domain)
    www = get_www(domain, http)
    return {"http": http, "www": www}


def strip_http_www(domain: str | None, http: str | None = None) -> str | None:
    """Remove both http(s) and www."""
    if not domain:
        return None
    http = http or get_http(domain)
    domain = strip_www(domain, http)
    domain = strip_http(domain, http)
    return domain


def get_stripped_domain(domain: str | None, http: str | None = None) -> list[str] | None:
    """Return list of domain parts, safely."""
    if not domain:
        return None
    domain = strip_http_www(domain, http)
    return domain.split("/") if domain else None


def get_domain_paths(domain: str | None, http: str | None = None) -> dict:
    """Return {'domain': <domain>, 'path': <path>} even if None."""
    if not domain:
        return {"domain": None, "path": ""}
    domain = strip_http_www(domain, http)
    domain_paths = str(domain).split("/") if domain else [""]
    return {
        "domain": domain_paths[0] if domain_paths else None,
        "path": "/".join(domain_paths[1:]) if len(domain_paths) > 1 else "",
    }


def get_domain(domain: str | None, http: str | None = None) -> str | None:
    """Extract bare domain from URL."""
    return get_domain_paths(domain, http).get("domain")


def get_domain_path(domain: str | None, http: str | None = None) -> str:
    """Extract path component from URL."""
    return get_domain_paths(domain, http).get("path", "")


def get_domain_name_ext(domain: str | None, http: str | None = None) -> dict:
    """Return {'name': name, 'ext': ext} safely."""
    if not domain:
        return {"name": None, "ext": None}
    domain_only = get_domain(domain, http)
    if not domain_only:
        return {"name": None, "ext": None}
    name, ext = os.path.splitext(domain_only)
    return {"name": name or None, "ext": ext or None}


def get_extension(domain: str | None = None, http: str | None = None, parsed=None, options=None) -> str | None:
    """Get file extension safely, even if parsed URL object is missing."""
    try:
        if parsed:
            domain = getattr(parsed, "netloc", domain)
            http = getattr(parsed, "scheme", http)
    except Exception:
        pass
    return get_domain_name_ext(domain, http).get("ext")


def get_domain_name(domain: str | None, http: str | None = None) -> str | None:
    """Get domain name without extension."""
    return get_domain_name_ext(domain, http).get("name")


# Backward compatibility alias
get_extention = get_extension
