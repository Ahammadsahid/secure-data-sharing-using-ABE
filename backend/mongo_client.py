from __future__ import annotations

import os
import ssl
from typing import Optional

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import certifi


def _env_bool(name: str, default: bool = False) -> bool:
    value = (os.getenv(name) or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "y", "on"}


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    """Create a MongoDB client for Atlas/ReplicaSet connections.

    IMPORTANT:
    - Never hardcode the MongoDB URI in source code.
    - Store it in environment variables (e.g., MONGODB_URI) loaded from `.env`.

    Parameters
    ----------
    uri:
        MongoDB connection string. If omitted, reads from `MONGODB_URI`.

    Returns
    -------
    MongoClient
        A configured PyMongo client using Stable API v1.
    """
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured. Set it in your environment or .env.")

    server_selection_timeout_ms = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS") or "3000")
    connect_timeout_ms = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS") or "3000")
    socket_timeout_ms = int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS") or "3000")

    # For debugging on restrictive networks (NOT recommended for production).
    tls_insecure = _env_bool("MONGODB_TLS_INSECURE", default=False)

    # Some proxies / SSL inspection setups break TLS 1.3 negotiation.
    # Forcing TLS 1.2 can restore connectivity on those networks.
    force_tls12 = _env_bool("MONGODB_FORCE_TLS12", default=False)

    # Some environments have trouble with OCSP endpoint checks.
    disable_ocsp = _env_bool("MONGODB_DISABLE_OCSP", default=False)

    # PyMongo forbids combining tlsInsecure with certain TLS verification options.
    if tls_insecure:
        disable_ocsp = False

    # Explicit CA bundle helps avoid SSL handshake issues on some Windows setups.

    base_kwargs: dict[str, object] = {
        "serverSelectionTimeoutMS": server_selection_timeout_ms,
        "connectTimeoutMS": connect_timeout_ms,
        "socketTimeoutMS": socket_timeout_ms,
    }
    if disable_ocsp:
        base_kwargs["tlsDisableOCSPEndpointCheck"] = True

    if force_tls12:
        context = ssl.create_default_context(cafile=certifi.where())
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_2
        if tls_insecure:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        try:
            return MongoClient(
                uri,
                server_api=ServerApi("1"),
                tls=True,
                ssl_context=context,
                **base_kwargs,
            )
        except Exception:
            # If the running PyMongo build doesn't accept ssl_context (or any TLS option),
            # fall back to the default configuration below.
            pass

    return MongoClient(
        uri,
        server_api=ServerApi("1"),
        tls=True,
        tlsCAFile=certifi.where(),
        tlsInsecure=tls_insecure,
        **base_kwargs,
    )


def ping_mongo(client: MongoClient) -> bool:
    """Ping the deployment to confirm connectivity."""
    client.admin.command("ping")
    return True
