# app.py
import json
import re
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
import requests
import streamlit as st


# =========================
# CONFIG: set your API info
# =========================
API_BASE_URL = "https://api.example.com"  # <-- change
API_HEADERS = {
    "Authorization": "Bearer YOUR_TOKEN",  # <-- change
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Define routes you want in the dropdown.
# You can include path params in {braces} and they'll show up as inputs.
ROUTES = [
    "/health",
    "/users",
    "/users/{user_id}",
    "/orders",
    "/orders/{order_id}",
]


# =========================
# Helpers
# =========================
PATH_PARAM_PATTERN = re.compile(r"{([^}]+)}")


def extract_path_params(route_template: str) -> List[str]:
    return PATH_PARAM_PATTERN.findall(route_template)


def build_route(route_template: str, param_values: Dict[str, str]) -> str:
    route = route_template
    for k, v in param_values.items():
        route = route.replace("{" + k + "}", str(v))
    return route


def safe_json_loads(s: str) -> Any:
    s = s.strip()
    if not s:
        return None
    return json.loads(s)


def flatten_records(data: Any) -> Tuple[pd.DataFrame | None, Any]:
    """
    If data is list[dict] => normalize to DataFrame
    If data is dict => 1-row DataFrame
    Else => None, return original
    """
    if isinstance(data, list):
        if all(isinstance(x, dict) for x in data):
            df = pd.json_normalize(data)
            return df, data
        # List but not dicts => show as single-col table
        return pd.DataFrame({"value": data}), data

    if isinstance(data, dict):
        df = pd.json_normalize(data)
        return df, data

    return None, data


def pick_display_payload(resp_json: Any) -> Any:
    """
    Heuristic: if response wraps data in common keys, prefer that.
    """
    if isinstance(resp_json, dict):
        for key in ["data", "results", "items", "rows"]:
            if key in resp_json:
                return resp_json[key]
    return resp_json


def request_api(
    method: str,
    base_url: str,
    route: str,
    headers: Dict[str, str],
    query_params: Dict[str, str],
    body: Any,
    timeout_s: int,
) -> requests.Response:
    url = base_url.rstrip("/") + "/" + route.lstrip("/")
    return requests.request(
        method=method,
        url=url,
        headers=headers,
        params={k: v for k, v in query_params.items() if v != ""},
        json=body,
        timeout=timeout_s,
    )


# =========================
# UI
# =========================
st.set_page_config(page_title="API Explorer", layout="wide")
st.title("API Explorer (Streamlit)")

with st.sidebar:
    st.header("API Settings")
    base_url = st.text_input("Base URL", value=API_BASE_URL)

    st.subheader("Headers")
    # Allow editing headers in UI, but default from vars
    headers_text = st.text_area(
        "Headers (JSON)",
        value=json.dumps(API_HEADERS, indent=2),
        height=180,
    )
    try:
        headers = safe_json_loads(headers_text) or {}
        if not isinstance(headers, dict):
            st.error("Headers must be a JSON object (dict).")
            headers = {}
    except Exception as e:
        st.error(f"Invalid headers JSON: {e}")
        headers = {}

    st.subheader("Request")
    method = st.selectbox("Method", ["GET", "POST", "PUT", "PATCH", "DELETE"], index=0)
    route_template = st.selectbox("Route", ROUTES, index=0)

    timeout_s = st.number_input("Timeout (seconds)", min_value=1, max_value=120, value=30, step=1)

st.divider()

# Path params based on route template
path_params = extract_path_params(route_template)
path_param_values: Dict[str, str] = {}

if path_params:
    st.subheader("Path Parameters")
    cols = st.columns(min(len(path_params), 4))
    for i, p in enumerate(path_params):
        with cols[i % len(cols)]:
            path_param_values[p] = st.text_input(p, value="")

route = build_route(route_template, path_param_values)

# Query params editor
st.subheader("Query Parameters")
qp_text = st.text_area(
    "Query params (JSON object, optional)",
    value='{\n  \n}',
    height=120,
    help='Example: {"limit":"50","status":"active"}',
)

query_params: Dict[str, str] = {}
try:
    qp = safe_json_loads(qp_text) or {}
    if not isinstance(qp, dict):
        st.error("Query params must be a JSON object (dict).")
    else:
        # Convert to str values to avoid requests issues
        query_params = {str(k): "" if v is None else str(v) for k, v in qp.items()}
except Exception as e:
    st.error(f"Invalid query params JSON: {e}")

# Body editor (only for non-GET typically, but allow always)
st.subheader("Request Body")
body_text = st.text_area(
    "Body (JSON, optional)",
    value="",
    height=160,
    help='Example: {"name":"Alice","email":"a@b.com"}',
)
body = None
if body_text.strip():
    try:
        body = safe_json_loads(body_text)
    except Exception as e:
        st.error(f"Invalid body JSON: {e}")
        body = None

colA, colB, colC = st.columns([1, 1, 3])
with colA:
    call = st.button("Call API", type="primary")
with colB:
    st.caption(f"Final route: `{route}`")
with colC:
    st.caption(f"Full URL: `{base_url.rstrip('/') + '/' + route.lstrip('/')}`")

if call:
    # Basic validation: require path params filled if present
    missing = [p for p in path_params if not path_param_values.get(p)]
    if missing:
        st.error(f"Missing path parameter(s): {', '.join(missing)}")
    else:
        try:
            with st.spinner("Calling API..."):
                resp = request_api(
                    method=method,
                    base_url=base_url,
                    route=route,
                    headers=headers,
                    query_params=query_params,
                    body=body,
                    timeout_s=int(timeout_s),
                )

            st.subheader("Response")
            meta1, meta2, meta3 = st.columns(3)
            meta1.metric("Status", str(resp.status_code))
            meta2.metric("Time (ms)", str(int(resp.elapsed.total_seconds() * 1000)))
            meta3.metric("Content-Type", resp.headers.get("Content-Type", ""))

            # Try JSON first
            resp_text = resp.text or ""
            parsed = None
            is_json = False
            try:
                parsed = resp.json()
                is_json = True
            except Exception:
                parsed = resp_text

            if not resp.ok:
                st.error("Request failed.")
                # Show payload for debugging
                if is_json:
                    st.json(parsed)
                else:
                    st.code(resp_text)
            else:
                if is_json:
                    payload = pick_display_payload(parsed)
                    df, original = flatten_records(payload)

                    tabs = st.tabs(["Table", "JSON", "Raw"])
                    with tabs[0]:
                        if df is not None:
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("Not table-shaped data; showing JSON view instead.")
                            st.json(payload)

                    with tabs[1]:
                        st.json(parsed)

                    with tabs[2]:
                        st.code(resp_text)
                else:
                    st.info("Non-JSON response; showing raw.")
                    st.code(resp_text)

        except requests.exceptions.Timeout:
            st.error("Request timed out.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
