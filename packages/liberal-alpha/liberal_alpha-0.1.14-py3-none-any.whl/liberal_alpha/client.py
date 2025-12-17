# liberal_alpha/client.py
from __future__ import annotations

import os
import time
import math
import json
import gzip
import hashlib
import logging
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

import requests

logger = logging.getLogger(__name__)

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore

try:
    import msgpack
except Exception:  # pragma: no cover
    msgpack = None  # type: ignore

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from eth_account import Account
from eth_account.messages import encode_defunct

from .crypto import get_wallet_address, decrypt_alpha_message

# ---- endpoints ----
DEFAULT_API_BASE = os.getenv("LIBALPHA_API_BASE", "https://api.liberalalpha.com").rstrip("/")
AUTH_PATH = "/api/users/auth"                              # POST
WITHOUT_ENTRIES_PATH = "/api/entries/v2/without_entries"   # GET
ENTRIES_PATH = "/api/entries/v2/entries"                   # GET

# upload endpoints (api-key auth)
UPLOAD_CREATE_PATH = "/api/entries/upload-session/create"                 # POST (json)
UPLOAD_PROGRESS_PATH = "/api/entries/upload-session/{session_id}/progress"  # GET
UPLOAD_CHUNK_PATH = "/api/entries/upload-session/{session_id}/chunk"        # POST (multipart)
UPLOAD_FINALIZE_PATH = "/api/entries/upload-session/{session_id}/finalize"  # POST


# ----------------------------
# Exceptions (keep simple)
# ----------------------------
class ConfigurationError(Exception):
    pass


class RequestError(Exception):
    pass


# ----------------------------
# helpers
# ----------------------------
def _ensure_pandas():
    if pd is None:
        raise ImportError("pandas is required. Please `pip install pandas`.")


def _ensure_msgpack():
    if msgpack is None:
        raise ImportError("msgpack is required for upload_data(). Please `pip install msgpack`.")


def _normalize_private_key(pk: Optional[str]) -> Optional[str]:
    if not pk:
        return None
    pk = pk.strip()
    if not pk.startswith("0x"):
        pk = "0x" + pk
    return pk


def _utc_iso_z(ts: Optional[dt.datetime] = None) -> str:
    if ts is None:
        ts = dt.datetime.now(dt.timezone.utc)
    ts = ts.astimezone(dt.timezone.utc)
    # keep milliseconds for stable cursor
    return ts.replace(microsecond=(ts.microppsecond // 1000) * 1000).isoformat().replace("+00:00", "Z")


# fix typo if any environments copy/paste; keep a safe alias
def _utc_iso_z(ts: Optional[dt.datetime] = None) -> str:
    if ts is None:
        ts = dt.datetime.now(dt.timezone.utc)
    ts = ts.astimezone(dt.timezone.utc)
    return ts.replace(microsecond=(ts.microsecond // 1000) * 1000).isoformat().replace("+00:00", "Z")


def _parse_iso_any(s: str) -> Optional[dt.datetime]:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return dt.datetime.fromisoformat(s)
    except Exception:
        return None


def _normalize_tz(tz_info: Union[dt.tzinfo, str, int, float, None]) -> dt.tzinfo:
    """
    Accept:
      - tzinfo instance
      - "Asia/Singapore"
      - "+8" / "-4"
      - 8 / -4 / 5.5 etc
    """
    if tz_info is None:
        return dt.timezone.utc

    if isinstance(tz_info, dt.tzinfo):
        return tz_info

    if isinstance(tz_info, (int, float)):
        hours = float(tz_info)
        minutes = int(round((hours - math.trunc(hours)) * 60))
        return dt.timezone(dt.timedelta(hours=int(math.trunc(hours)), minutes=minutes))

    if isinstance(tz_info, str):
        s = tz_info.strip()
        # "+8" "-4" "5.5"
        if (s.startswith(("+", "-")) and s[1:].replace(".", "", 1).isdigit()) or s.replace(".", "", 1).isdigit():
            return _normalize_tz(float(s))
        # "Asia/xxx"
        if ZoneInfo is None:
            raise ImportError("zoneinfo not available. Use tz offset int like 8 / -4.")
        return ZoneInfo(s)

    raise TypeError(f"Unsupported tz_info type: {type(tz_info)}")


def _guess_timestamp_ms(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        iv = int(value)
    except Exception:
        return None
    # seconds vs ms heuristic
    if iv < 10_000_000_000:
        return iv * 1000
    return iv


def _local_yyyymmdd(ts_ms: int, tz: dt.tzinfo) -> int:
    d = dt.datetime.fromtimestamp(ts_ms / 1000.0, tz=dt.timezone.utc).astimezone(tz).date()
    return d.year * 10000 + d.month * 100 + d.day


def _ensure_0x(hex_str: str) -> str:
    if not isinstance(hex_str, str):
        hex_str = str(hex_str)
    hex_str = hex_str.strip()
    if not hex_str.startswith("0x"):
        return "0x" + hex_str
    return hex_str


def _strip_0x(hex_str: str) -> str:
    if not isinstance(hex_str, str):
        hex_str = str(hex_str)
    hex_str = hex_str.strip()
    if hex_str.startswith("0x"):
        return hex_str[2:]
    return hex_str


# ----------------------------
# Client
# ----------------------------
class LiberalAlphaClient:
    """
    API client (no local runner required).

    Auth model:
      - For upload endpoints: API key (X-API-Key).
      - For entries download endpoint (/api/entries/v2/...): Authorization: Bearer <JWT>.
      - This client can auto-get JWT via POST /api/users/auth using your private key.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key: Optional[str] = None,
        api_base: str = DEFAULT_API_BASE,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.getenv("LIBALPHA_API_KEY")
        self.private_key = _normalize_private_key(private_key or os.getenv("LIBALPHA_PRIVATE_KEY"))
        self.api_base = (api_base or DEFAULT_API_BASE).rstrip("/")
        self.timeout = timeout

        self.wallet: Optional[str] = None
        if self.private_key:
            self.wallet = get_wallet_address(self.private_key)
            logger.info("Wallet address derived: %s", self.wallet)

        self._jwt_token: Optional[str] = None
        self._jwt_obtained_at: Optional[float] = None
        self._auth_scheme_used: Optional[str] = None

        # Upload defaults (do NOT expose in public method signature)
        self._upload_chunk_size = int(os.getenv("LIBALPHA_UPLOAD_CHUNK_SIZE", str(1024 * 1024)))  # 1MB
        self._upload_max_retries = int(os.getenv("LIBALPHA_UPLOAD_MAX_RETRIES", "3"))
        self._upload_resume = os.getenv("LIBALPHA_UPLOAD_RESUME", "1") != "0"
        self._upload_timeout = int(os.getenv("LIBALPHA_UPLOAD_TIMEOUT", "60"))

        # Optional batch_id via env (since public API has only 2 args)
        env_batch = os.getenv("LIBALPHA_UPLOAD_BATCH_ID", "").strip()
        self._upload_batch_id: Optional[int] = int(env_batch) if env_batch.isdigit() else None

        # Session cache for real resume across process restarts
        self._upload_cache_path = Path(
            os.getenv("LIBALPHA_UPLOAD_CACHE_PATH", str(Path.home() / ".libalpha_upload_sessions.json"))
        )

    # ----------------------------
    # Auth: get JWT via /api/users/auth
    # ----------------------------
    def _build_auth_candidates(self, wallet_checksum: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Return list of (scheme_name, payload) to try.
        Compatible variants:
          - wallet checksum vs lowercase
          - signature with 0x vs without 0x
          - timestamp in seconds vs milliseconds
          - personal_sign(text=timestamp or template)
        """
        now_sec = int(time.time())
        now_ms = int(time.time() * 1000)

        ts_candidates = [str(now_sec), str(now_ms)]
        msg_tmpl = os.getenv("LIBALPHA_AUTH_MSG_TEMPLATE", "{timestamp}")

        def sign_personal(message_text: str) -> str:
            msg = encode_defunct(text=message_text)
            signed = Account.sign_message(msg, private_key=self.private_key)  # type: ignore[arg-type]
            return signed.signature.hex()

        candidates: List[Tuple[str, Dict[str, Any]]] = []
        seen = set()

        for ts in ts_candidates:
            message_text = msg_tmpl.format(timestamp=ts, wallet=wallet_checksum)

            sig = sign_personal(message_text)
            sig_with_0x = _ensure_0x(sig)
            sig_no_0x = _strip_0x(sig_with_0x)

            for wallet_variant in [wallet_checksum, wallet_checksum.lower()]:
                for sig_variant, sig_tag in [(sig_with_0x, "sig_0x"), (sig_no_0x, "sig_no0x")]:
                    scheme = f"personal_sign(msg='{message_text}', ts='{ts}', wallet='{wallet_variant}', {sig_tag})"
                    payload = {
                        "wallet_address": wallet_variant,
                        "signature": sig_variant,
                        "timestamp": ts,
                        "metadata": {
                            "sdk": "liberal_alpha_python_sdk",
                            "auth_scheme": scheme,
                        },
                    }
                    key = (payload["wallet_address"], payload["signature"], payload["timestamp"])
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append((scheme, payload))

        return candidates

    def _ensure_jwt(self, force_refresh: bool = False) -> str:
        if self._jwt_token and not force_refresh:
            return self._jwt_token

        if not self.private_key:
            raise ConfigurationError("Missing private_key (LIBALPHA_PRIVATE_KEY). Entries download needs JWT.")

        wallet_checksum = Account.from_key(self.private_key).address
        self.wallet = wallet_checksum
        logger.info("Wallet address derived: %s", self.wallet)

        url = f"{self.api_base}{AUTH_PATH}"
        candidates = self._build_auth_candidates(wallet_checksum)

        last_401_text = None

        for scheme, payload in candidates:
            try:
                msg_tmpl = os.getenv("LIBALPHA_AUTH_MSG_TEMPLATE", "{timestamp}")
                message_text = msg_tmpl.format(timestamp=payload["timestamp"], wallet=wallet_checksum)
                msg = encode_defunct(text=message_text)
                sig_local = _ensure_0x(payload["signature"])
                recovered = Account.recover_message(msg, signature=sig_local)
                if recovered.lower() != wallet_checksum.lower():
                    logger.debug("Skip scheme (local recover mismatch): %s recovered=%s", scheme, recovered)
                    continue
            except Exception as e:
                logger.debug("Skip scheme (local check error): %s err=%s", scheme, e)
                continue

            try:
                resp = requests.post(url, json=payload, timeout=self.timeout, headers={"Accept": "application/json"})
            except requests.RequestException as e:
                raise RequestError(f"Auth request failed: {e}") from e

            if resp.status_code == 401:
                last_401_text = resp.text.strip()
                logger.debug("Auth 401 with scheme: %s, resp=%s", scheme, last_401_text[:300])
                continue

            if resp.status_code >= 400:
                raise RequestError(f"Auth HTTP {resp.status_code}: {resp.text.strip()}")

            try:
                data = resp.json()
            except Exception:
                raise RequestError(f"Auth response not JSON: {resp.text[:200]}")

            token = None
            if isinstance(data, dict):
                d = data.get("data")
                if isinstance(d, dict):
                    token = d.get("token") or d.get("jwt") or d.get("access_token")
                if token is None and "token" in data:
                    token = data.get("token")

            if not token:
                raise RequestError(f"Auth succeeded but no token in response: {data}")

            self._jwt_token = token
            self._jwt_obtained_at = time.time()
            self._auth_scheme_used = scheme
            logger.info("JWT token obtained via /api/users/auth (scheme=%s)", scheme)
            return token

        raise RequestError(
            "Auth HTTP 401: Invalid signature for all tried signing variants. "
            f"Last 401 response: {last_401_text or ''}".strip()
        )

    # ----------------------------
    # HTTP helpers
    # ----------------------------
    def _headers_api_key(self) -> Dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    def _headers_bearer(self) -> Dict[str, str]:
        token = self._ensure_jwt()
        return {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        auth: str = "bearer",  # "bearer" or "api_key" or "none"
        _retry: bool = True,
    ) -> Any:
        url = f"{self.api_base}{path}"

        if auth == "bearer":
            headers = self._headers_bearer()
        elif auth == "api_key":
            headers = self._headers_api_key()
            if not self.api_key:
                raise ConfigurationError("Missing api_key (LIBALPHA_API_KEY).")
        else:
            headers = {"Accept": "application/json"}

        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise RequestError(f"HTTP request failed: {e}") from e

        if resp.status_code == 401 and auth == "bearer" and _retry:
            self._ensure_jwt(force_refresh=True)
            return self._request(method, path, params=params, json_body=json_body, auth=auth, _retry=False)

        if resp.status_code >= 400:
            raise RequestError(f"HTTP {resp.status_code}: {resp.text.strip()}")

        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            try:
                return resp.json()
            except Exception:
                return resp.text

        try:
            return resp.json()
        except Exception:
            return resp.text

    # ----------------------------
    # Records endpoint (optional)
    # ----------------------------
    def my_records(self) -> Any:
        return self._request("GET", "/api/records", auth="api_key")

    # ----------------------------
    # Download helpers: get symbols
    # ----------------------------
    def _get_symbols_via_without_entries(self, record_id: int) -> List[str]:
        payload = self._request(
            "GET",
            WITHOUT_ENTRIES_PATH,
            params={"record_id": int(record_id)},
            auth="bearer",
        )

        if not isinstance(payload, dict):
            return []

        data = payload.get("data")
        if not isinstance(data, dict):
            return []

        record = data.get("record")
        if isinstance(record, dict):
            syms = record.get("symbols")
            if isinstance(syms, list):
                return [str(s).strip() for s in syms if str(s).strip()]

            sd = record.get("symbol_data")
            if isinstance(sd, dict):
                return [str(k).strip() for k in sd.keys() if str(k).strip()]

        syms = data.get("symbols")
        if isinstance(syms, list):
            return [str(s).strip() for s in syms if str(s).strip()]

        return []

    # ----------------------------
    # Extract entries
    # ----------------------------
    def _extract_entries(self, payload: Any) -> List[Dict[str, Any]]:
        """
        Supports both:
          data.entries = [ {...}, {...} ]
          data.entries = { "SYM": [ {...}, {...} ], ... }
        """
        if payload is None:
            return []
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
        if not isinstance(payload, dict):
            return []

        data = payload.get("data")

        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]

        if isinstance(data, dict):
            v = data.get("entries")

            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]

            if isinstance(v, dict):
                out: List[Dict[str, Any]] = []
                for sym, arr in v.items():
                    if isinstance(arr, list):
                        for item in arr:
                            if isinstance(item, dict):
                                if "symbol" not in item and isinstance(sym, str):
                                    item = dict(item)
                                    item["symbol"] = sym
                                out.append(item)
                return out

        return []

    # ----------------------------
    # Entry -> row
    # ----------------------------
    def _entry_to_row(
        self,
        e: Dict[str, Any],
        *,
        record_id: int,
        tz: dt.tzinfo,
        decrypt_if_needed: bool,
    ) -> Dict[str, Any]:
        symbol = e.get("symbol") or e.get("target_asset") or e.get("asset") or ""

        ts_ms = (
            _guess_timestamp_ms(e.get("timestamp_ms"))
            or _guess_timestamp_ms(e.get("timestamp"))
            or _guess_timestamp_ms(e.get("time"))
            or _guess_timestamp_ms(e.get("created_at"))
        ) or 0

        utc_dt = dt.datetime.fromtimestamp(ts_ms / 1000.0, tz=dt.timezone.utc) if ts_ms else None
        local_dt = utc_dt.astimezone(tz) if utc_dt else None
        local_date = _local_yyyymmdd(ts_ms, tz) if ts_ms else None

        batch_id = e.get("batch_id") or e.get("batchId")

        plain_data: Dict[str, Any] = {}
        encrypted_payload = None

        if isinstance(e.get("data"), dict):
            plain_data = e["data"]
        elif isinstance(e.get("data"), str):
            encrypted_payload = e["data"]
        else:
            for k in ("encrypted_data", "encryptedData", "encrypted_payload", "encryptedPayload"):
                if k in e:
                    encrypted_payload = e.get(k)
                    break

        decrypted_obj = None
        if encrypted_payload is not None and decrypt_if_needed and self.private_key:
            decrypted_obj = decrypt_alpha_message(self.private_key, encrypted_payload)
            if isinstance(decrypted_obj, dict):
                plain_data = decrypted_obj

        return {
            "record_id": record_id,
            "symbol": symbol,
            "timestamp_ms": ts_ms,
            "datetime_utc": utc_dt.isoformat() if utc_dt else None,
            "datetime_local": local_dt.isoformat() if local_dt else None,
            "local_date": local_date,
            "batch_id": batch_id,
            "is_encrypted": encrypted_payload is not None,
            "decrypt_ok": isinstance(decrypted_obj, dict) if encrypted_payload is not None else None,
            "data": plain_data if isinstance(plain_data, dict) else {},
            "raw_entry": e,
        }

    # ----------------------------
    # Public API: download_data()
    # ----------------------------
    def download_data(
        self,
        record_id: int,
        symbols: List[str],
        dates: List[int],
        tz_info: Union[dt.tzinfo, str, int, float] = "Asia/Singapore",
        *,
        size: int = 500,
        max_pages: int = 2000,
        cursor: Optional[str] = None,
        decrypt_if_needed: bool = True,
        auto_symbols: bool = True,
    ):
        _ensure_pandas()

        if record_id <= 0:
            raise ValueError("record_id must be positive int")

        tz = _normalize_tz(tz_info)

        sym_list = [s.strip() for s in (symbols or []) if isinstance(s, str) and s.strip()]
        sym_set = set(sym_list)
        date_set = set(int(d) for d in (dates or []))

        if auto_symbols and not sym_list:
            fetched = self._get_symbols_via_without_entries(record_id)
            sym_list = fetched
            sym_set = set(sym_list)

        cur = cursor.strip() if isinstance(cursor, str) and cursor.strip() else _utc_iso_z()

        rows: List[Dict[str, Any]] = []

        for _page in range(1, max_pages + 1):
            params: Dict[str, Any] = {
                "record_id": int(record_id),
                "size": int(size),
                "cursor": cur,
            }
            if sym_list:
                params["symbol"] = ",".join(sym_list)

            payload = self._request("GET", ENTRIES_PATH, params=params, auth="bearer")
            entries = self._extract_entries(payload)

            if not entries:
                break

            batch_oldest_dt: Optional[dt.datetime] = None
            batch_oldest_ms: Optional[int] = None

            for e in entries:
                row = self._entry_to_row(e, record_id=record_id, tz=tz, decrypt_if_needed=decrypt_if_needed)

                if sym_set:
                    sym = (row.get("symbol") or "").strip()
                    if sym and sym not in sym_set:
                        continue

                if date_set:
                    yyyymmdd = row.get("local_date")
                    if yyyymmdd not in date_set:
                        continue

                rows.append(row)

                ca = e.get("created_at")
                ca_dt = _parse_iso_any(ca) if isinstance(ca, str) else None
                if ca_dt:
                    if batch_oldest_dt is None or ca_dt < batch_oldest_dt:
                        batch_oldest_dt = ca_dt

                tms = _guess_timestamp_ms(e.get("timestamp")) or _guess_timestamp_ms(e.get("timestamp_ms"))
                if tms:
                    if batch_oldest_ms is None or tms < batch_oldest_ms:
                        batch_oldest_ms = tms

            next_cursor = None
            if batch_oldest_dt:
                batch_oldest_dt = batch_oldest_dt.astimezone(dt.timezone.utc) - dt.timedelta(milliseconds=1)
                next_cursor = batch_oldest_dt.isoformat().replace("+00:00", "Z")
            elif batch_oldest_ms:
                odt = dt.datetime.fromtimestamp(batch_oldest_ms / 1000.0, tz=dt.timezone.utc) - dt.timedelta(milliseconds=1)
                next_cursor = odt.isoformat().replace("+00:00", "Z")

            if not next_cursor or next_cursor == cur:
                break
            cur = next_cursor

            if len(entries) < int(size):
                break

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        if "data" in df.columns:
            data_df = pd.json_normalize(df["data"].apply(lambda x: x if isinstance(x, dict) else {}))
            for c in list(data_df.columns):
                if c in df.columns:
                    data_df.rename(columns={c: f"data.{c}"}, inplace=True)
            df = df.drop(columns=["data"]).reset_index(drop=True)
            df = pd.concat([df, data_df], axis=1)

        return df

    # ============================================================
    # Historical Upload API (Public): upload_data(record_id, df)->bool
    # ============================================================
    def upload_data(self, record_id: int, df) -> bool:
        """
        Historical Upload API (Python)

        Public interface: ONLY (record_id, df) -> bool

        Expected df columns:
          - record_id (int)
          - symbol (str)
          - data (dict)
          - timestamp (int, ms)   # seconds accepted and auto converted

        Auth: api_key (X-API-Key)

        Uses resumable chunked upload with local session cache:
          ~/.libalpha_upload_sessions.json (configurable via LIBALPHA_UPLOAD_CACHE_PATH)
        """
        try:
            _ensure_pandas()
            _ensure_msgpack()

            if record_id <= 0:
                raise ValueError("record_id must be positive int")

            if not self.api_key:
                raise ConfigurationError("Missing api_key (LIBALPHA_API_KEY). Upload needs X-API-Key.")

            if df is None or getattr(df, "empty", True):
                logger.info("upload_data: empty dataframe, nothing to upload.")
                return True

            compressed, checksum, total_size, meta = self._prepare_compressed_payload(record_id, df)
            batch_id = meta.get("batch_id")

            # resume via local cache (keyed by record_id + checksum)
            session_id = None
            if self._upload_resume:
                session_id = self._load_cached_session_id(record_id, checksum)

            if session_id:
                logger.info("upload_data: resume with cached session_id=%s", session_id)

            # if no session or progress fails => create new session
            if not session_id:
                session_id = self._upload_create_session(total_size=total_size, checksum=checksum, metadata=meta)
                if self._upload_resume:
                    self._save_cached_session_id(record_id, checksum, session_id)

            ok = self._upload_data_internal(
                session_id=session_id,
                compressed_data=compressed,
                checksum=checksum,
                record_id=record_id,
                batch_id=batch_id,
            )

            if ok and self._upload_resume:
                self._delete_cached_session_id(record_id, checksum)

            return ok

        except Exception as e:
            logger.error("upload_data failed: %s", e)
            return False

    # ----------------------------
    # Upload internals
    # ----------------------------
    def _prepare_compressed_payload(self, record_id: int, df) -> Tuple[bytes, str, int, Dict[str, Any]]:
        required_cols = {"record_id", "symbol", "data", "timestamp"}
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"DataFrame missing columns: {missing}. Required: {sorted(required_cols)}")

        # batch_id: from df['batch_id'] (single value) OR env LIBALPHA_UPLOAD_BATCH_ID
        batch_id: Optional[int] = None
        if "batch_id" in df.columns:
            vals = [v for v in df["batch_id"].dropna().unique().tolist()]
            if len(vals) == 1:
                try:
                    batch_id = int(vals[0])
                except Exception:
                    batch_id = None
        if batch_id is None:
            batch_id = self._upload_batch_id

        # Validate record_id consistency (strict, safer)
        unique_rids = [int(x) for x in df["record_id"].dropna().unique().tolist()]
        if unique_rids and (len(unique_rids) != 1 or unique_rids[0] != int(record_id)):
            raise ValueError(
                f"DataFrame record_id mismatch: df has {unique_rids}, but argument record_id={record_id}. "
                "Please make them一致，或在构造df时全部写同一个record_id。"
            )

        items: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            rid = int(row["record_id"])
            sym = str(row["symbol"])

            data_obj = row["data"] if isinstance(row["data"], dict) else {}
            ts_ms = _guess_timestamp_ms(row["timestamp"]) or 0

            items.append({
                "record_id": rid,
                "symbol": sym,
                "data": data_obj,
                "timestamp": ts_ms,
            })

        meta = {
            "record_id": int(record_id),
            "batch_id": batch_id,
            "total_records": len(items),
            "compression": "msgpack+gzip",
            "created_at": int(time.time() * 1000),
            "sdk": "liberal_alpha_python_sdk",
        }

        payload = {"batch_id": batch_id, "items": items, "metadata": meta}

        raw = msgpack.packb(payload, use_bin_type=True)  # type: ignore[union-attr]
        compressed = gzip.compress(raw, compresslevel=6)
        checksum = hashlib.sha256(compressed).hexdigest()
        total_size = len(compressed)

        logger.info(
            "Prepared upload payload: records=%s raw=%sB compressed=%sB ratio=%.1f%% batch_id=%s",
            len(items), len(raw), len(compressed), (len(compressed) / max(len(raw), 1)) * 100.0, batch_id
        )

        return compressed, checksum, total_size, meta

    def _upload_data_internal(
        self,
        *,
        session_id: str,
        compressed_data: bytes,
        checksum: str,
        record_id: int,
        batch_id: Optional[int],
    ) -> bool:
        chunk_size = int(self._upload_chunk_size)
        max_retries = int(self._upload_max_retries)
        timeout = int(self._upload_timeout)

        total_size = len(compressed_data)
        total_chunks = int(math.ceil(total_size / chunk_size)) if total_size > 0 else 0
        logger.info("Uploading %s bytes in %s chunks (chunk_size=%s)", total_size, total_chunks, chunk_size)

        uploaded_chunks: set[int] = set()
        if self._upload_resume:
            try:
                prog = self._upload_get_progress(session_id, timeout=timeout)
                uploaded_chunks = set(int(x) for x in (prog.get("uploaded_chunks") or []))
                logger.info("Resume info: %s/%s chunks already uploaded", len(uploaded_chunks), total_chunks)
            except Exception as e:
                # session可能过期/不存在，fallback到新建session
                logger.warning("Progress query failed (session_id=%s): %s. Will recreate session.", session_id, e)
                session_id = self._upload_create_session(
                    total_size=total_size,
                    checksum=checksum,
                    metadata={
                        "record_id": int(record_id),
                        "batch_id": batch_id,
                        "total_records": None,
                        "compression": "msgpack+gzip",
                        "created_at": int(time.time() * 1000),
                        "sdk": "liberal_alpha_python_sdk",
                    },
                )
                if self._upload_resume:
                    self._save_cached_session_id(record_id, checksum, session_id)
                uploaded_chunks = set()

        for idx in range(total_chunks):
            if self._upload_resume and idx in uploaded_chunks:
                logger.info("Chunk %s already uploaded, skipping (resume)", idx)
                continue

            start = idx * chunk_size
            end = min(start + chunk_size, total_size)
            chunk = compressed_data[start:end]
            chunk_checksum = hashlib.sha256(chunk).hexdigest()
            is_last = (idx == total_chunks - 1)

            ok = False
            for attempt in range(max_retries):
                if self._upload_chunk(
                    session_id=session_id,
                    chunk_index=idx,
                    chunk_data=chunk,
                    chunk_checksum=chunk_checksum,
                    is_last=is_last,
                    timeout=timeout,
                ):
                    ok = True
                    break
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.info("Retry chunk %s in %ss ...", idx, wait)
                    time.sleep(wait)

            if not ok:
                logger.error("Failed to upload chunk %s after %s attempts (session_id=%s)", idx, max_retries, session_id)
                return False

            logger.info("Upload progress: %.1f%% (%s/%s)", (idx + 1) / total_chunks * 100, idx + 1, total_chunks)

        return self._upload_finalize(session_id, timeout=timeout)

    def _upload_create_session(self, *, total_size: int, checksum: str, metadata: Dict[str, Any]) -> str:
        url = f"{self.api_base}{UPLOAD_CREATE_PATH}"
        headers = self._headers_api_key()
        resp = requests.post(
            url,
            json={"total_size": int(total_size), "checksum": checksum, "metadata": metadata},
            headers=headers,
            timeout=self.timeout,
        )
        if resp.status_code >= 400:
            raise RequestError(f"Create upload session HTTP {resp.status_code}: {resp.text.strip()}")

        data = resp.json()
        if data.get("status") != "success":
            raise RequestError(f"Create upload session failed: {data}")

        session_id = data["data"]["session_id"]
        logger.info("Created upload session: %s", session_id)
        return session_id

    def _upload_get_progress(self, session_id: str, *, timeout: int) -> Dict[str, Any]:
        url = f"{self.api_base}{UPLOAD_PROGRESS_PATH.format(session_id=session_id)}"
        headers = self._headers_api_key()
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            raise RequestError(f"Get upload progress HTTP {resp.status_code}: {resp.text.strip()}")

        data = resp.json()
        if data.get("status") != "success":
            raise RequestError(f"Get upload progress failed: {data}")

        return data["data"]

    def _upload_chunk(
        self,
        *,
        session_id: str,
        chunk_index: int,
        chunk_data: bytes,
        chunk_checksum: str,
        is_last: bool,
        timeout: int,
    ) -> bool:
        url = f"{self.api_base}{UPLOAD_CHUNK_PATH.format(session_id=session_id)}"
        headers = self._headers_api_key()

        files = {"chunk": ("chunk", chunk_data, "application/octet-stream")}
        data = {
            "chunk_index": str(int(chunk_index)),
            "chunk_checksum": chunk_checksum,
            "is_last": "true" if is_last else "false",
        }

        try:
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
        except requests.RequestException as e:
            logger.error("Chunk %s upload error: %s", chunk_index, e)
            return False

        if resp.status_code >= 400:
            logger.error("Chunk %s upload HTTP %s: %s", chunk_index, resp.status_code, resp.text.strip())
            return False

        try:
            out = resp.json()
        except Exception:
            logger.error("Chunk %s upload non-JSON response: %s", chunk_index, resp.text[:200])
            return False

        if out.get("status") != "success":
            logger.error("Chunk %s upload failed: %s", chunk_index, out)
            return False

        logger.info("Chunk %s uploaded successfully", chunk_index)
        return True

    def _upload_finalize(self, session_id: str, *, timeout: int) -> bool:
        url = f"{self.api_base}{UPLOAD_FINALIZE_PATH.format(session_id=session_id)}"
        headers = self._headers_api_key()
        resp = requests.post(url, headers=headers, timeout=timeout)

        if resp.status_code >= 400:
            logger.error("Finalize upload HTTP %s: %s", resp.status_code, resp.text.strip())
            return False

        data = resp.json()
        if data.get("status") != "success":
            logger.error("Finalize upload failed: %s", data)
            return False

        logger.info("Upload session %s finalized successfully", session_id)
        return True

    # -------- session cache (resume across restarts) --------
    def _load_cached_session_id(self, record_id: int, checksum: str) -> Optional[str]:
        key = f"{int(record_id)}:{checksum}"
        try:
            if not self._upload_cache_path.exists():
                return None
            obj = json.loads(self._upload_cache_path.read_text("utf-8"))
            v = obj.get(key)
            return str(v) if v else None
        except Exception:
            return None

    def _save_cached_session_id(self, record_id: int, checksum: str, session_id: str) -> None:
        key = f"{int(record_id)}:{checksum}"
        try:
            obj = {}
            if self._upload_cache_path.exists():
                obj = json.loads(self._upload_cache_path.read_text("utf-8"))
            obj[key] = session_id
            self._upload_cache_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), "utf-8")
        except Exception:
            # cache failure should not block upload
            return

    def _delete_cached_session_id(self, record_id: int, checksum: str) -> None:
        key = f"{int(record_id)}:{checksum}"
        try:
            if not self._upload_cache_path.exists():
                return
            obj = json.loads(self._upload_cache_path.read_text("utf-8"))
            if key in obj:
                obj.pop(key, None)
                self._upload_cache_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), "utf-8")
        except Exception:
            return


# ----------------------------
# Keep compatibility with liberal_alpha/__init__.py
# ----------------------------
liberal: Optional[LiberalAlphaClient] = None


def initialize(
    api_key: Optional[str] = None,
    private_key: Optional[str] = None,
    api_base: str = DEFAULT_API_BASE,
    timeout: int = 30,
) -> LiberalAlphaClient:
    global liberal
    liberal = LiberalAlphaClient(
        api_key=api_key,
        private_key=private_key,
        api_base=api_base,
        timeout=timeout,
    )
    return liberal
