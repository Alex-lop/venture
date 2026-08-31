#!/usr/bin/env bash
# prepush.sh — pre-push guard for a PUBLIC repo (CLAUDE.md v2 §2 "Identity and public-repo rules").
# Works as .git/hooks/pre-push (git feeds ref lines on stdin) and when run directly.
# Prints PASS/FAIL per check; exits 1 if any check FAILs. Appends one line to private/prepush.log.
set -uo pipefail

# git hands the hook "<local ref> <local sha> <remote ref> <remote sha>" lines on stdin. Drain, ignore.
# Never read from a TTY: a hook must not block waiting for a human.
[ -t 0 ] || cat >/dev/null 2>&1 || true

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "FAIL setup: not a git repo"; exit 1; }
cd "$ROOT" || exit 1

IDENTITY_FILE="private/IDENTITY.md"
DENYLIST_FILE="private/DENYLIST.txt"
LOG_FILE="private/prepush.log"
FAILED=""

fail() { FAILED="$FAILED $1"; echo "FAIL $1: $2"; }
pass() { echo "PASS $1: $2"; }
warn() { echo "WARN $1: $2"; }

# ---- source the prepush-vars block from private/IDENTITY.md -------------------
if [ ! -f "$IDENTITY_FILE" ]; then
  echo "FAIL setup: $IDENTITY_FILE missing (cannot verify identity)"
  printf '%s\tFAIL\tsetup(identity-file-missing)\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG_FILE" 2>/dev/null || true
  exit 1
fi
# values may contain spaces ("Alex Lopez"), so re-quote each one before eval
VARS=$(awk '/^```prepush-vars$/{f=1;next} /^```/{f=0}
  f && /^[A-Z_]+=/ { i=index($0,"="); k=substr($0,1,i-1); v=substr($0,i+1);
                     gsub(/\r/,"",v); gsub(/\047/,"",v); sub(/[ \t]+$/,"",v);
                     printf "%s=\047%s\047\n", k, v }' "$IDENTITY_FILE")
eval "$VARS"
for k in EXPECTED_AUTHOR_NAME EXPECTED_AUTHOR_EMAIL EXPECTED_REMOTE_REPO EXPECTED_GH_LOGIN; do
  eval "v=\${$k:-}"
  if [ -z "$v" ]; then
    echo "FAIL setup: $k missing from $IDENTITY_FILE prepush-vars block"
    printf '%s\tFAIL\tsetup(%s-missing)\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$k" >>"$LOG_FILE" 2>/dev/null || true
    exit 1
  fi
done

# ---- scope: tracked + staged, working-tree content, text files only ----------
SCOPE=$( { git ls-files; git diff --cached --name-only --diff-filter=ACMR; } | sort -u )
FILES=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue          # deleted-in-worktree: nothing to read
  grep -Iq . "$f" 2>/dev/null || continue   # binary or empty -> skip
  FILES="$FILES$f
"
done <<EOF
$SCOPE
EOF

# ---- 1. secrets --------------------------------------------------------------
if command -v gitleaks >/dev/null 2>&1; then
  gl=0
  out1=$(gitleaks detect --no-git --source . --redact 2>&1) || gl=1
  out2=$(gitleaks protect --staged --redact 2>&1) || gl=1
  if [ "$gl" -eq 0 ]; then
    pass secrets "gitleaks detect + protect clean"
  else
    fail secrets "gitleaks reported findings"
    printf '%s\n%s\n' "$out1" "$out2" | sed 's/^/    /'
  fi
else
  # regex fallback (gitleaks not installed)
  PATTERNS=(
    'AKIA[0-9A-Z]{16}'
    'gh[pousr]_[A-Za-z0-9]{36}'
    'github_pat_[A-Za-z0-9_]{22,}'
    'pypi-AgEI[A-Za-z0-9_-]{20,}'
    'xox[baprs]-[A-Za-z0-9-]{10,}'
    'AIza[0-9A-Za-z_-]{35}'
    '(sk|rk)_live_[A-Za-z0-9]{16,}'
    'sk-ant-[A-Za-z0-9_-]{20,}'
    'sk-[A-Za-z0-9]{32,}'
    '-----BEGIN [A-Z ]*PRIVATE KEY-----'
    "(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*['\"][^'\"]{12,}['\"]"
  )
  # obvious placeholders — not secrets
  PLACEHOLDER='(<[^>]*>|\$\{|\$[A-Za-z_]|xxx|example|changeme|redacted)'
  hits=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    for p in "${PATTERNS[@]}"; do
      while IFS= read -r m; do
        [ -n "$m" ] || continue
        ln=${m%%:*}; txt=${m#*:}
        printf '%s' "$txt" | grep -Eiq "$PLACEHOLDER" && continue
        hits=$((hits+1))
        printf '    %s:%s: ' "$f" "$ln"
        printf '%.6s' "$txt"
        printf '... (masked)\n'
      done <<EOT
$(grep -E -n -o "$p" "$f" 2>/dev/null)
EOT
    done
  done <<EOF
$FILES
EOF
  if [ "$hits" -eq 0 ]; then
    pass secrets "regex fallback, 0 hits over $(printf '%s' "$FILES" | grep -c . ) text files"
  else
    fail secrets "$hits candidate secret(s) — see above"
  fi
fi

# ---- 2. denylist -------------------------------------------------------------
if [ ! -f "$DENYLIST_FILE" ]; then
  fail denylist "$DENYLIST_FILE missing"
else
  dl_out=$(git grep -i -w -n -F -f "$DENYLIST_FILE" -- ':!private' ':!assets' 2>/dev/null)
  # staged-but-untracked-in-HEAD paths are already index entries (git grep covers them);
  # re-grep the working-tree copies anyway so a not-yet-indexed edit cannot slip through.
  st_out=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in private/*|assets/*) continue ;; esac
    [ -f "$f" ] || continue
    grep -Iq . "$f" 2>/dev/null || continue
    st_out="$st_out$(grep -i -w -n -F -f "$DENYLIST_FILE" "$f" 2>/dev/null | sed "s|^|$f:|")
"
  done <<EOF
$(git diff --cached --name-only --diff-filter=ACMR)
EOF
  all_out=$(printf '%s\n%s\n' "$dl_out" "$st_out" | grep . | sort -u)
  n_out=$(printf '%s' "$all_out" | grep -c . )
  if [ "$n_out" -eq 0 ]; then
    pass denylist "no denied string in tracked or staged files"
  else
    fail denylist "$n_out denied-string hit(s)"
    printf '%s\n' "$all_out" | cut -c1-120 | sed 's/^/    /'
  fi
fi

# ---- 3. identity -------------------------------------------------------------
id_bad=""
n=$(git config user.name || true)
e=$(git config user.email || true)
[ "$n" = "$EXPECTED_AUTHOR_NAME" ]  || id_bad="$id_bad user.name='$n'"
[ "$e" = "$EXPECTED_AUTHOR_EMAIL" ] || id_bad="$id_bad user.email='$e'"
r=$(git remote get-url origin 2>/dev/null || true)
case "$r" in
  "git@github.com:$EXPECTED_REMOTE_REPO"|"git@github.com:$EXPECTED_REMOTE_REPO.git"| \
  "https://github.com/$EXPECTED_REMOTE_REPO"|"https://github.com/$EXPECTED_REMOTE_REPO.git") ;;
  *) id_bad="$id_bad origin='$r'" ;;
esac
if [ -n "$id_bad" ]; then
  fail identity "unexpected:$id_bad"
else
  pass identity "$n <$e> -> $r"
fi
if command -v gh >/dev/null 2>&1; then
  login=$(GH_PAGER=cat gh api user --jq .login 2>/dev/null || true)
  if [ -z "$login" ]; then
    warn identity-gh "gh present but offline/unauthenticated — login not verified"
  elif [ "$login" = "$EXPECTED_GH_LOGIN" ]; then
    pass identity-gh "gh api user = $login"
  else
    fail identity-gh "gh authenticated as '$login', expected '$EXPECTED_GH_LOGIN'"
  fi
else
  warn identity-gh "gh not installed — skipped"
fi

# ---- 4. no private/ or assets/ path tracked or staged ------------------------
leaked=$(printf '%s\n' "$SCOPE" | grep -E '^(private|assets)/' || true)
if [ -z "$leaked" ]; then
  pass paths "no tracked or staged path under private/ or assets/"
else
  fail paths "$(printf '%s\n' "$leaked" | grep -c .) path(s) under private/ or assets/"
  printf '%s\n' "$leaked" | sed 's/^/    /'
fi

# ---- verdict + log -----------------------------------------------------------
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ -z "$FAILED" ]; then
  echo "PASS overall"
  printf '%s\tPASS\t-\n' "$ts" >>"$LOG_FILE" 2>/dev/null || true
  exit 0
fi
echo "FAIL overall:$FAILED"
printf '%s\tFAIL\t%s\n' "$ts" "$(echo "$FAILED" | tr -s ' ' ',' | sed 's/^,//')" >>"$LOG_FILE" 2>/dev/null || true
exit 1
