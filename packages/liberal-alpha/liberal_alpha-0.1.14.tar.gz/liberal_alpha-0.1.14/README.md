# Liberal Alpha Python SDK (Historical HTTP APIs)

This SDK provides **historical upload** and **historical download** APIs over HTTP.

## Install

```bash
pip install liberal_alpha
# Optional: override default API base (default is https://api.liberalalpha.com)
export LIBALPHA_API_BASE="https://api.liberalalpha.com"

# Upload auth (X-API-Key)
export LIBALPHA_API_KEY="YOUR_API_KEY"

# Download auth (used to obtain JWT via /api/users/auth)
export LIBALPHA_PRIVATE_KEY="0xYOUR_PRIVATE_KEY"

Optional upload tuning:

export LIBALPHA_UPLOAD_BATCH_ID="12345"      # optional batch id (int)
export LIBALPHA_UPLOAD_CHUNK_SIZE="1048576"  # default 1MB
export LIBALPHA_UPLOAD_RESUME="1"            # 1=enable resume, 0=disable

Initialize Client

from liberal_alpha.client import LiberalAlphaClient

# api_base defaults to https://api.liberalalpha.com
# can be overridden by env LIBALPHA_API_BASE or by passing api_base=...
client = LiberalAlphaClient(
    api_key="YOUR_API_KEY",            # optional if using env LIBALPHA_API_KEY
    private_key="0xYOUR_PRIVATE_KEY",  # optional if using env LIBALPHA_PRIVATE_KEY
)

Historical Upload API (Python)

def upload_data(record_id: int, df: pandas.DataFrame) -> bool:
    pass

DataFrame Format

Your DataFrame must contain these columns:

-record_id (int)

-symbol (str)

-data (dict) — e.g. {"open": 50000.0, "close": 51000.0}

-timestamp (int) — milliseconds since epoch
(seconds are also accepted and will be auto-converted to milliseconds)

Example

import pandas as pd
from liberal_alpha.client import LiberalAlphaClient

client = LiberalAlphaClient(
    api_key="YOUR_API_KEY",
    # api_base defaults to https://api.liberalalpha.com
)

sample_data = []
for i in range(1000):
    sample_data.append({
        "record_id": 4,
        "symbol": "BNfBTC",
        "data": {"open": 50000.0 + i, "close": 51000.0 + i},
        "timestamp": 1733299200000 + i * 1000,
    })

df = pd.DataFrame(sample_data)

# Optional batch_id: set via env because public API has only 2 args
# export LIBALPHA_UPLOAD_BATCH_ID=12345
ok = client.upload_data(record_id=4, df=df)
print("Upload ok:", ok)

Notes:

-Upload uses X-API-Key authentication.

-Upload is chunked and supports resume if enabled (default enabled).

Historical Download API (Python)

def download_data(
    record_id: int,
    symbols: list[str],
    dates: list[int],
    tz_info: datetime.tzinfo | str = "Asia/Singapore"
) -> pandas.DataFrame:
    pass

Parameters

-record_id: the record id to download

-symbols: list of symbols, e.g. ["BTCUSDT", "ETHUSDT"]

If you pass [], the SDK will automatically fetch all symbols (if supported by backend).

-dates: list of local dates in YYYYMMDD format, e.g. [20251214, 20251215]

If you pass [], no date filter is applied.

-tz_info: controls how local_date is computed

"Asia/Singapore" (IANA tz string)

numeric offsets like 8, -4, or strings like "+8", "-4"

8 means UTC+8 (SGT/HKT)

-4 means UTC-4 (NYC during DST)

Example

from liberal_alpha.client import LiberalAlphaClient

client = LiberalAlphaClient(
    private_key="0xYOUR_PRIVATE_KEY",
    # api_base defaults to https://api.liberalalpha.com
)

df = client.download_data(
    record_id=24,
    symbols=[],              # empty => auto fetch all symbols
    dates=[],                # empty => no date filter
    tz_info="Asia/Singapore" # or tz_info=8
)

print(df.head())
print("rows:", len(df))

