#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: bash scripts/clear_gcp_cache.sh <project_id|config.yaml>" 1>&2
  echo " - If a project_id is provided, config is assumed at projects/<project_id>/configs/project_config.yaml" 1>&2
  echo " - Reads model.parameters.cache.object_store.{type,bucket,prefix} and deletes gs://bucket/prefix/**" 1>&2
  echo " - Also deletes metrics at gs://bucket/projects/<project_id>/metrics/** and charts at gs://bucket/projects/<project_id>/charts/**" 1>&2
  echo " - Optionally reads credentials from model.parameters.cache.backend.credentials_json and sets GOOGLE_APPLICATION_CREDENTIALS" 1>&2
  echo " - Set MLOPS_CLEAR_ALL=1 to delete entire bucket when no prefix is configured (dangerous)." 1>&2
  exit 1
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || ${#} -lt 1 ]]; then
  usage
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

INPUT="$1"
if [[ "$INPUT" == *.yaml ]]; then
  CONFIG_PATH="$INPUT"
else
  CONFIG_PATH="${REPO_ROOT}/projects/${INPUT}/configs/project_config.yaml"
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Config not found: $CONFIG_PATH" 1>&2
  exit 2
fi

TYPE=""; BUCKET=""; PREFIX=""; CREDS=""; GCP_PROJECT=""

# Determine project id early for metrics deletion path
PROJECT_FOR_METRICS=""
if [[ "$INPUT" == *.yaml ]]; then
  PROJECT_FOR_METRICS="$(basename "$(cd "$(dirname "$CONFIG_PATH")/.." && pwd)")"
else
  PROJECT_FOR_METRICS="$INPUT"
fi

# Fast path: allow env overrides to avoid YAML parsing/deps
if [[ -n "${MLOPS_GCS_BUCKET:-}" ]]; then
  TYPE="gcs"
  BUCKET="${MLOPS_GCS_BUCKET}"
  PREFIX="${MLOPS_GCS_PREFIX:-}"
  CREDS="${GOOGLE_APPLICATION_CREDENTIALS:-}"
  GCP_PROJECT="${GOOGLE_CLOUD_PROJECT:-}"
else
  # Parse YAML to obtain GCS settings and optional credentials
  if command -v python3 >/dev/null 2>&1; then
    PY_CMD=python3
  elif command -v python >/dev/null 2>&1; then
    PY_CMD=python
  else
    echo "Python is required to parse YAML; not found. Set MLOPS_GCS_BUCKET and MLOPS_GCS_PREFIX to skip parsing." 1>&2
    exit 3
  fi

  PY_OUT=$($PY_CMD - "$CONFIG_PATH" <<'PY'
import sys, json, re
p = sys.argv[1]

def parse_with_pyyaml(path):
    try:
        import yaml
    except Exception:
        return None
    try:
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        model = (cfg.get('model') or {})
        params = (model.get('parameters') or {})
        cache = (params.get('cache') or {})
        backend = (cache.get('backend') or {})
        store = (cache.get('object_store') or {})
        return {
            'type': store.get('type') or '',
            'bucket': store.get('bucket') or '',
            'prefix': (store.get('prefix') or '').strip('/') if isinstance(store.get('prefix'), str) else '',
            'creds': backend.get('credentials_json') or '',
            'gcp_project': backend.get('gcp_project') or '',
        }
    except Exception:
        return None

def parse_minimal(path):
    vals = {'type':'','bucket':'','prefix':'','creds':'','gcp_project':''}
    stack = []  # list of (indent, key)
    targets = {
        'obj': ['model','parameters','cache','object_store'],
        'bkd': ['model','parameters','cache','backend'],
    }
    with open(path, 'r') as f:
        for raw in f:
            line = raw.split('#',1)[0].rstrip('\n')
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(' '))
            while stack and indent <= stack[-1][0]:
                stack.pop()
            stripped = line.strip()
            m = re.match(r'([A-Za-z0-9_]+):\s*(.*)$', stripped)
            if not m:
                continue
            key, val = m.group(1), m.group(2)
            path_keys = [k for _,k in stack] + [key]
            if val == '' or val is None:
                stack.append((indent, key))
                continue
            # normalize value
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if path_keys[:-1] == targets['obj']:
                if key == 'type':
                    vals['type'] = val
                elif key == 'bucket':
                    vals['bucket'] = val
                elif key == 'prefix':
                    vals['prefix'] = val.strip('/')
            if path_keys[:-1] == targets['bkd']:
                if key == 'credentials_json':
                    vals['creds'] = val
                elif key == 'gcp_project':
                    vals['gcp_project'] = val
    return vals

data = parse_with_pyyaml(p)
if data is None:
    data = parse_minimal(p)
print(json.dumps(data))
PY
  )

  TYPE=$(printf '%s' "$PY_OUT" | $PY_CMD -c 'import sys,json; print((json.load(sys.stdin) or {}).get("type",""))')
  BUCKET=$(printf '%s' "$PY_OUT" | $PY_CMD -c 'import sys,json; print((json.load(sys.stdin) or {}).get("bucket",""))')
  PREFIX=$(printf '%s' "$PY_OUT" | $PY_CMD -c 'import sys,json; print((json.load(sys.stdin) or {}).get("prefix",""))')
  CREDS=$(printf '%s' "$PY_OUT" | $PY_CMD -c 'import sys,json; print((json.load(sys.stdin) or {}).get("creds",""))')
  GCP_PROJECT=$(printf '%s' "$PY_OUT" | $PY_CMD -c 'import sys,json; print((json.load(sys.stdin) or {}).get("gcp_project",""))')
fi

if [[ "$TYPE" != "gcs" ]]; then
  echo "Config object_store.type is not 'gcs' (type='$TYPE'). Nothing to clear." 1>&2
  exit 0
fi

if [[ -n "$CREDS" ]]; then
  # Try REPO_ROOT-relative and CWD-relative
  if [[ -f "$REPO_ROOT/$CREDS" ]]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$REPO_ROOT/$CREDS"
  elif [[ -f "$CREDS" ]]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$CREDS"
  fi
fi
if [[ -n "$GCP_PROJECT" && -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  export GOOGLE_CLOUD_PROJECT="$GCP_PROJECT"
fi

if [[ -z "$BUCKET" ]]; then
  echo "No bucket configured; cannot clear cache." 1>&2
  exit 4
fi

URI="gs://$BUCKET"
if [[ -n "$PREFIX" ]]; then
  URI="$URI/$PREFIX"
fi

METRICS_PREFIX="projects/${PROJECT_FOR_METRICS}/metrics"
METRICS_URI="gs://$BUCKET/$METRICS_PREFIX"
CHARTS_PREFIX="projects/${PROJECT_FOR_METRICS}/charts"
CHARTS_URI="gs://$BUCKET/$CHARTS_PREFIX"

if [[ -z "$PREFIX" && "${MLOPS_CLEAR_ALL:-}" != "1" ]]; then
  echo "Refusing to delete entire bucket without confirmation for cache prefix. Set MLOPS_CLEAR_ALL=1 to proceed." 1>&2
  echo "Would delete: ${URI}/** (skipping cache prefix deletion)" 1>&2
  SKIP_CACHE_DELETE=1
fi

if [[ -z "${SKIP_CACHE_DELETE:-}" ]]; then
  echo "Clearing GCS cache at: ${URI}/**"
else
  echo "Skipping cache prefix deletion; proceeding to clear metrics/charts at: ${METRICS_URI}/** and ${CHARTS_URI}/**"
fi

# Prefer gcloud storage if available (handles auth, avoids manual JWT path)
if command -v gcloud >/dev/null 2>&1; then
  (gcloud config set project "$GCP_PROJECT" >/dev/null 2>&1 || true)
  if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    (gcloud auth activate-service-account --key-file "$GOOGLE_APPLICATION_CREDENTIALS" --quiet >/dev/null 2>&1 || true)
  fi
  if [[ -z "${SKIP_CACHE_DELETE:-}" ]]; then
    gcloud storage rm -r --quiet "${URI}/**" || true
  fi
  # Always clear metrics and charts trees
  gcloud storage rm -r --quiet "${METRICS_URI}/**" || true
  gcloud storage rm -r --quiet "${CHARTS_URI}/**" || true
  echo "Done (gcloud storage)."
elif command -v gsutil >/dev/null 2>&1; then
  # -m parallel; -r recursive; -f force ignore missing
  if [[ -z "${SKIP_CACHE_DELETE:-}" ]]; then
    gsutil -m rm -r -f "${URI}/**" || true
  fi
  gsutil -m rm -r -f "${METRICS_URI}/**" || true
  gsutil -m rm -r -f "${CHARTS_URI}/**" || true
  echo "Done (gsutil)."
else

# Fallback: Direct HTTP deletion using service account JSON (no extra installs)
# Determine credentials JSON path
CREDS_PATH=""
CONFIG_DIR="$(cd "$(dirname "$CONFIG_PATH")" && pwd)"
PROJECT_DIR="$(cd "${CONFIG_DIR}/.." && pwd)"
if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
  CREDS_PATH="${GOOGLE_APPLICATION_CREDENTIALS}"
elif [[ -n "$CREDS" ]]; then
  # Try common locations: repo root, alongside config, CWD
  if [[ -f "$REPO_ROOT/$CREDS" ]]; then CREDS_PATH="$REPO_ROOT/$CREDS"; fi
  if [[ -z "$CREDS_PATH" && -f "$PROJECT_DIR/$CREDS" ]]; then CREDS_PATH="$PROJECT_DIR/$CREDS"; fi
  if [[ -z "$CREDS_PATH" && -f "$CONFIG_DIR/$CREDS" ]]; then CREDS_PATH="$CONFIG_DIR/$CREDS"; fi
  if [[ -z "$CREDS_PATH" && -f "$CREDS" ]]; then CREDS_PATH="$CREDS"; fi
fi
if [[ -z "$CREDS_PATH" ]]; then
  echo "No credentials_json found via config (tried: $REPO_ROOT/$CREDS, $PROJECT_DIR/$CREDS, $CONFIG_DIR/$CREDS, $CREDS) and GOOGLE_APPLICATION_CREDENTIALS not set; cannot authenticate to GCS." 1>&2
  exit 6
fi

if command -v python3 >/dev/null 2>&1; then PY_CMD=python3; elif command -v python >/dev/null 2>&1; then PY_CMD=python; else echo "Python required for minimal JSON parsing." 1>&2; exit 6; fi

# Extract client_email and token_uri and write private key to temp file
TMP_KEY="$(mktemp)"
CREDS_LINES_RAW=$($PY_CMD - "$CREDS_PATH" "$TMP_KEY" <<'PY'
import sys, json
p, out = sys.argv[1], sys.argv[2]
with open(p, 'r') as f:
    obj = json.load(f)
key = obj.get('private_key')
if not key:
    sys.stderr.write('NO_PRIVATE_KEY\n')
    sys.exit(1)
open(out, 'w').write(key)
print(obj.get('client_email',''))
print(obj.get('token_uri', 'https://oauth2.googleapis.com/token'))
PY
) || { echo "Credentials JSON missing private_key; install gcloud/gsutil or set GOOGLE_APPLICATION_CREDENTIALS to a service account key." 1>&2; rm -f "$TMP_KEY"; exit 6; }
CLIENT_EMAIL="$(printf '%s' "$CREDS_LINES_RAW" | sed -n '1p')"
TOKEN_URI="$(printf '%s' "$CREDS_LINES_RAW" | sed -n '2p')"
if [[ -z "$CLIENT_EMAIL" ]]; then echo "Failed to read client_email from credentials." 1>&2; rm -f "$TMP_KEY"; exit 6; fi

# Build JWT for OAuth 2.0 Service Account flow
b64url() { base64 | tr -d '\n' | tr '+/' '-_' | tr -d '='; }
NOW=$(date +%s)
EXP=$((NOW + 3600))
JWT_HEADER='{"alg":"RS256","typ":"JWT"}'
JWT_CLAIM=$(cat <<EOF
{"iss":"$CLIENT_EMAIL","scope":"https://www.googleapis.com/auth/devstorage.full_control","aud":"$TOKEN_URI","exp":$EXP,"iat":$NOW}
EOF
)
HDR_B64=$(printf '%s' "$JWT_HEADER" | b64url)
CLM_B64=$(printf '%s' "$JWT_CLAIM" | b64url)
DATA="$HDR_B64.$CLM_B64"
SIG=$(printf '%s' "$DATA" | openssl dgst -binary -sha256 -sign "$TMP_KEY" | base64 | tr -d '\n' | tr '+/' '-_' | tr -d '=')
JWT="$DATA.$SIG"

# Exchange for access token
TOKEN_JSON=$(curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  --data-urlencode "assertion=$JWT" "$TOKEN_URI")
ACCESS_TOKEN=$(printf '%s' "$TOKEN_JSON" | $PY_CMD -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')
rm -f "$TMP_KEY"
if [[ -z "$ACCESS_TOKEN" ]]; then echo "Failed to obtain access token." 1>&2; exit 7; fi

# Paginate listing and delete using Python stdlib only; delete both cache prefix and metrics/charts trees
TOTAL=$($PY_CMD - "$BUCKET" "$PREFIX" "$ACCESS_TOKEN" "$METRICS_PREFIX" "$CHARTS_PREFIX" <<'PY'
import sys, json, urllib.request, urllib.parse
bucket, prefix, token, metrics_prefix, charts_prefix = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
base = f"https://storage.googleapis.com/storage/v1/b/{urllib.parse.quote(bucket)}/o"
params = {'fields': 'items(name),nextPageToken'}
if prefix:
    params['prefix'] = prefix
next_token = None
total = 0
while True:
    q = dict(params)
    if next_token:
        q['pageToken'] = next_token
    url = base + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    for item in data.get('items', []) or []:
        name = item.get('name')
        if not name:
            continue
        enc = urllib.parse.quote(name, safe='')
        del_url = f"https://storage.googleapis.com/storage/v1/b/{urllib.parse.quote(bucket)}/o/{enc}"
        del_req = urllib.request.Request(del_url, method='DELETE', headers={'Authorization': f'Bearer {token}'})
        try:
            urllib.request.urlopen(del_req).read()
            total += 1
        except Exception as e:
            sys.stderr.write(f"Failed to delete {name}: {e}\n")
    next_token = data.get('nextPageToken')
    if not next_token:
        break
def _delete_tree(pref):
    if not pref:
        return 0
    params2 = {'fields': 'items(name),nextPageToken', 'prefix': pref}
    next_token = None
    removed = 0
    while True:
        q2 = dict(params2)
        if next_token:
            q2['pageToken'] = next_token
        url2 = base + "?" + urllib.parse.urlencode(q2)
        req2 = urllib.request.Request(url2, headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req2) as resp2:
            data2 = json.loads(resp2.read().decode('utf-8'))
        for item in data2.get('items', []) or []:
            name = item.get('name')
            if not name:
                continue
            enc = urllib.parse.quote(name, safe='')
            del_url = f"https://storage.googleapis.com/storage/v1/b/{urllib.parse.quote(bucket)}/o/{enc}"
            del_req = urllib.request.Request(del_url, method='DELETE', headers={'Authorization': f'Bearer {token}'})
            try:
                urllib.request.urlopen(del_req).read()
                removed += 1
            except Exception as e:
                sys.stderr.write(f"Failed to delete {name}: {e}\n")
        next_token = data2.get('nextPageToken')
        if not next_token:
            break
    return removed

total += _delete_tree(metrics_prefix)
total += _delete_tree(charts_prefix)
print(total)
PY
)

echo "Deleted ${TOTAL} objects from ${URI}, ${METRICS_URI} and ${CHARTS_URI}"
fi

# -------------------- Firestore cleanup --------------------
PROJECT_DOC_ID=""
if [[ "$INPUT" == *.yaml ]]; then
  # Attempt to infer project id as parent directory of configs
  CONFIG_DIR_NAME="$(basename "$(cd "$(dirname "$CONFIG_PATH")/.." && pwd)")"
  PROJECT_DOC_ID="$CONFIG_DIR_NAME"
else
  PROJECT_DOC_ID="$INPUT"
fi

if [[ -z "$GCP_PROJECT" && -n "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  GCP_PROJECT="$GOOGLE_CLOUD_PROJECT"
fi

if [[ -z "$GCP_PROJECT" ]]; then
  echo "Skipping Firestore cleanup: GOOGLE_CLOUD_PROJECT not set and not found in config backend.gcp_project." 1>&2
else
  echo "Clearing Firestore data at: projects/${GCP_PROJECT}/databases/(default)/documents/mlops_projects/${PROJECT_DOC_ID} (recursive)"
  if command -v gcloud >/dev/null 2>&1; then
    # Best-effort: use gcloud recursive delete if available
    (gcloud config set project "$GCP_PROJECT" >/dev/null 2>&1 || true)
    gcloud firestore documents delete "mlops_projects/${PROJECT_DOC_ID}" --recursive --quiet || true
    echo "Done (gcloud)."
  else
    # HTTP fallback using service account JSON or emulator
    # Determine credentials JSON path (reuse earlier logic)
    CREDS_PATH_FS=""
    if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
      CREDS_PATH_FS="${GOOGLE_APPLICATION_CREDENTIALS}"
    elif [[ -n "$CREDS" ]]; then
      if [[ -f "$REPO_ROOT/$CREDS" ]]; then CREDS_PATH_FS="$REPO_ROOT/$CREDS"; fi
      if [[ -z "$CREDS_PATH_FS" && -f "$PROJECT_DIR/$CREDS" ]]; then CREDS_PATH_FS="$PROJECT_DIR/$CREDS"; fi
      if [[ -z "$CREDS_PATH_FS" && -f "$CONFIG_DIR/$CREDS" ]]; then CREDS_PATH_FS="$CONFIG_DIR/$CREDS"; fi
      if [[ -z "$CREDS_PATH_FS" && -f "$CREDS" ]]; then CREDS_PATH_FS="$CREDS"; fi
    fi

    if [[ -z "${FIRESTORE_EMULATOR_HOST:-}" && -z "$CREDS_PATH_FS" ]]; then
      echo "Skipping Firestore cleanup: no credentials and no emulator configured." 1>&2
    else
      if command -v python3 >/dev/null 2>&1; then PY_CMD=python3; elif command -v python >/dev/null 2>&1; then PY_CMD=python; else echo "Python required for Firestore HTTP cleanup." 1>&2; exit 0; fi

      ACCESS_TOKEN_FS=""
      if [[ -z "${FIRESTORE_EMULATOR_HOST:-}" ]]; then
        # Build OAuth token from service account JSON
        TMP_KEY_FS="$(mktemp)"
        CREDS_LINES_RAW=$($PY_CMD - "$CREDS_PATH_FS" "$TMP_KEY_FS" <<'PY'
import sys, json
p, out = sys.argv[1], sys.argv[2]
with open(p, 'r') as f:
    obj = json.load(f)
open(out, 'w').write(obj['private_key'])
print(obj['client_email'])
print(obj.get('token_uri', 'https://oauth2.googleapis.com/token'))
PY
)
        CLIENT_EMAIL_FS="$(printf '%s' "$CREDS_LINES_RAW" | sed -n '1p')"
        TOKEN_URI_FS="$(printf '%s' "$CREDS_LINES_RAW" | sed -n '2p')"
        b64url() { base64 | tr -d '\n' | tr '+/' '-_' | tr -d '='; }
        NOW_FS=$(date +%s)
        EXP_FS=$((NOW_FS + 3600))
        JWT_HEADER_FS='{"alg":"RS256","typ":"JWT"}'
        JWT_CLAIM_FS=$(cat <<EOF
{"iss":"$CLIENT_EMAIL_FS","scope":"https://www.googleapis.com/auth/datastore","aud":"$TOKEN_URI_FS","exp":$EXP_FS,"iat":$NOW_FS}
EOF
)
        HDR_B64_FS=$(printf '%s' "$JWT_HEADER_FS" | b64url)
        CLM_B64_FS=$(printf '%s' "$JWT_CLAIM_FS" | b64url)
        DATA_FS="$HDR_B64_FS.$CLM_B64_FS"
        SIG_FS=$(printf '%s' "$DATA_FS" | openssl dgst -binary -sha256 -sign "$TMP_KEY_FS" | base64 | tr -d '\n' | tr '+/' '-_' | tr -d '=')
        JWT_FS="$DATA_FS.$SIG_FS"
        TOKEN_JSON_FS=$(curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
          --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
          --data-urlencode "assertion=$JWT_FS" "$TOKEN_URI_FS")
        ACCESS_TOKEN_FS=$(printf '%s' "$TOKEN_JSON_FS" | $PY_CMD -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')
        rm -f "$TMP_KEY_FS"
      fi

      # Python cleanup: recursively delete mlops_projects/{project_id}
      $PY_CMD - "$GCP_PROJECT" "$PROJECT_DOC_ID" "$ACCESS_TOKEN_FS" <<'PY'
import sys, json, urllib.request, urllib.parse

project_id, proj_doc, token = sys.argv[1], sys.argv[2], sys.argv[3]
emulator = False
base = f"https://firestore.googleapis.com/v1"
host = None
import os
host = os.environ.get('FIRESTORE_EMULATOR_HOST')
if host:
    emulator = True
    if not host.startswith('http'):
        base = f"http://{host}/v1"
    else:
        base = f"{host}/v1"

def _req(method, url, data=None):
    headers = {"Content-Type": "application/json"}
    if not emulator and token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=(json.dumps(data).encode('utf-8') if isinstance(data, dict) else data), method=method, headers=headers)
    with urllib.request.urlopen(req) as resp:
        if resp.status == 204:
            return None
        body = resp.read().decode('utf-8')
        return json.loads(body) if body else None

def list_collections(doc_path):
    url = f"{base}/{doc_path}:listCollectionIds"
    out = _req("POST", url, {"pageSize": 200}) or {}
    ids = out.get('collectionIds', [])
    # no pagination for simplicity; collections are few here
    return ids

def list_documents(coll_path):
    # coll_path like projects/.../documents/mlops_projects/{id}/step_indices
    url = f"{base}/{coll_path}"
    docs = []
    page_token = None
    while True:
        q = {}
        if page_token:
            url2 = url + ("&" if "?" in url else "?") + urllib.parse.urlencode({"pageToken": page_token})
        else:
            url2 = url
        out = _req("GET", url2) or {}
        for d in out.get('documents', []) or []:
            docs.append(d.get('name'))
        page_token = out.get('nextPageToken')
        if not page_token:
            break
    return docs

def delete_document(doc_name):
    url = f"{base}/{doc_name}"
    try:
        _req("DELETE", url)
    except Exception:
        pass

root_doc = f"projects/{project_id}/databases/(default)/documents/mlops_projects/{proj_doc}"

def recurse_delete(doc_path):
    # List and delete subcollections
    for cid in list_collections(doc_path):
        coll_path = f"{doc_path}/{cid}"
        # If this is a collection listing endpoint, convert to documents path
        docs = list_documents(coll_path)
        for dname in docs:
            # Recurse on child doc before delete (handles nested collections)
            recurse_delete(dname)
            delete_document(dname)

recurse_delete(root_doc)
# Delete the root doc last
delete_document(root_doc)
print("Firestore cleanup completed.")
PY
      echo "Done (HTTP)."
    fi
  fi
fi

echo "Completed cache cleanup for project: ${PROJECT_DOC_ID}"
exit 0


