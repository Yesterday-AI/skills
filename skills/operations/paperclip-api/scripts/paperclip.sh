#!/usr/bin/env bash
# paperclip.sh — CLI wrapper for the Paperclip AI REST API
# Usage: paperclip.sh <command> [options]
#
# Env vars (required):
#   PAPERCLIP_API_URL      — Base URL (e.g. https://your-instance.up.railway.app)
#
# Auth — provide ONE of:
#   PAPERCLIP_API_TOKEN    — Board API key (pcp_board_*) minted via
#                            `paperclipai auth login`. Recommended — no
#                            rate limit, persistent.
#   PAPERCLIP_EMAIL +      — Email/password fallback. Wrapper signs in per
#   PAPERCLIP_PASSWORD       call → /api/auth/sign-in/email rate-limits at
#                            ~10 sign-ins/min (HTTP 429). Use bearer for
#                            non-trivial scripted use.
#
# Env vars (optional):
#   PAPERCLIP_COMPANY_ID   — Default company ID (can override per command with --company-id)

set -euo pipefail

API_URL="${PAPERCLIP_API_URL:?Set PAPERCLIP_API_URL}"
API_TOKEN="${PAPERCLIP_API_TOKEN:-}"
EMAIL="${PAPERCLIP_EMAIL:-}"
PASSWORD="${PAPERCLIP_PASSWORD:-}"
COMPANY_ID="${PAPERCLIP_COMPANY_ID:-}"
SESSION_COOKIE=""

if [[ -z "$API_TOKEN" && ( -z "$EMAIL" || -z "$PASSWORD" ) ]]; then
  echo "Error: provide PAPERCLIP_API_TOKEN, or BOTH PAPERCLIP_EMAIL and PAPERCLIP_PASSWORD." >&2
  echo "Mint a board token via: paperclipai auth login" >&2
  exit 1
fi

# --- helpers ---

sign_in() {
  # Bearer token path — no sign-in needed
  if [[ -n "$API_TOKEN" ]]; then
    return 0
  fi
  local header_file http_code
  header_file=$(mktemp)
  trap "rm -f '$header_file'" RETURN
  http_code=$(curl -sS -o /dev/null -D "$header_file" -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Origin: ${API_URL}" \
    -d "$(jq -n --arg e "$EMAIL" --arg p "$PASSWORD" '{email: $e, password: $p}')" \
    "${API_URL}/api/auth/sign-in/email") || true
  if [[ "$http_code" -ge 400 ]] && [[ "$http_code" != "302" ]]; then
    echo "Error: sign-in failed (HTTP ${http_code})" >&2
    if [[ "$http_code" == "429" ]]; then
      echo "Hint: cookie sign-in is rate-limited. Mint a board API key" >&2
      echo "      via 'paperclipai auth login' and export PAPERCLIP_API_TOKEN." >&2
    fi
    return 1
  fi
  SESSION_COOKIE=$(grep -i '^set-cookie:' "$header_file" \
    | sed 's/^[Ss]et-[Cc]ookie: *//; s/;.*//' \
    | tr '\n' '; ' | sed 's/; $//')
  if [[ -z "$SESSION_COOKIE" ]]; then
    echo "Error: sign-in succeeded but no session cookie received" >&2
    return 1
  fi
}

api() {
  local method="$1" path="$2"
  shift 2
  if [[ -z "$API_TOKEN" && -z "$SESSION_COOKIE" ]]; then
    sign_in
  fi
  # auth_args emits header lines we feed to curl via xargs-style array
  local auth_header_name auth_header_value
  if [[ -n "$API_TOKEN" ]]; then
    auth_header_name="Authorization"
    auth_header_value="Bearer ${API_TOKEN}"
  else
    auth_header_name="Cookie"
    auth_header_value="${SESSION_COOKIE}"
  fi
  local response http_code
  response=$(curl -sS -w "\n%{http_code}" -X "$method" \
    -H "${auth_header_name}: ${auth_header_value}" \
    -H "Content-Type: application/json" \
    -H "Origin: ${API_URL}" \
    "$@" \
    "${API_URL}${path}") || true
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    echo "Error: HTTP ${http_code}" >&2
    echo "$body" >&2
    return 1
  fi
  echo "$body"
}

# multipart upload (no Content-Type header — curl sets boundary)
api_upload() {
  local method="$1" path="$2"
  shift 2
  if [[ -z "$API_TOKEN" && -z "$SESSION_COOKIE" ]]; then
    sign_in
  fi
  local auth_header_name auth_header_value
  if [[ -n "$API_TOKEN" ]]; then
    auth_header_name="Authorization"
    auth_header_value="Bearer ${API_TOKEN}"
  else
    auth_header_name="Cookie"
    auth_header_value="${SESSION_COOKIE}"
  fi
  local response http_code
  response=$(curl -sS -w "\n%{http_code}" -X "$method" \
    -H "${auth_header_name}: ${auth_header_value}" \
    -H "Origin: ${API_URL}" \
    "$@" \
    "${API_URL}${path}") || true
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  if [[ "$http_code" -ge 400 ]]; then
    echo "Error: HTTP ${http_code}" >&2
    echo "$body" >&2
    return 1
  fi
  echo "$body"
}

require_company() {
  if [[ -z "$COMPANY_ID" ]]; then
    echo "Error: --company-id required or set PAPERCLIP_COMPANY_ID" >&2
    exit 1
  fi
}

require_jq() {
  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
  fi
}

# Parse --data <json> from remaining args into DATA_ARG
parse_data_arg() {
  DATA_ARG=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --data) DATA_ARG="$2"; shift 2;;
      *) shift;;
    esac
  done
  [[ -z "$DATA_ARG" ]] && { echo "Error: --data required (JSON)" >&2; exit 1; }
}

usage() {
  cat <<'EOF'
paperclip.sh — Paperclip AI API Client

COMPANY COMMANDS
  company list                              List all companies
  company get <id>                          Get company details
  company create <name> [description]       Create a new company
  company update <id> [opts]                Update a company
  company archive <id>                      Archive a company
  company delete <id>                       Delete a company
  company export <id>                       Export company (portability)
  company export-preview <id>               Preview export
  company import --data '...'               Import company bundle (Board)
  company import-preview --data '...'       Preview import (Board)
  company safe-import-preview <id> --data   CEO-level safe import preview
  company safe-import <id> --data '...'     CEO-level safe import

AGENT COMMANDS
  agent list                                List agents (requires --company-id)
  agent get <id>                            Get agent details
  agent create <name> <role> [opts]         Create an agent directly
  agent hire <name> <role> [opts]           Hire via governance (Board approval)
  agent update <id> [opts]                  Update agent
  agent delete <id>                         Delete agent
  agent pause <id>                          Pause agent
  agent resume <id>                         Resume agent
  agent terminate <id>                      Terminate agent
  agent wakeup <id> [opts]                  Wake up agent
  agent config <id>                         Get agent configuration
  agent config-revisions <id>               List config revisions
  agent config-rollback <id> <rev-id>       Rollback config revision
  agent instructions-get <id>               Get instructions bundle
  agent instructions-file <id> --path P     Get instructions file content
  agent instructions-set <id> [opts]        Write instructions file
  agent instructions-delete <id> --path P   Delete instructions file
  agent instructions-update <id> [opts]     Update bundle settings
  agent skills <id>                         Get agent skills
  agent skills-sync <id> --skills "a,b"     Sync agent skills
  agent keys <id>                           List agent API keys
  agent keys-create <id> --name "..."       Create agent API key
  agent keys-revoke <id> <key-id>           Revoke agent API key
  agent runtime-state <id>                  Get runtime state
  agent task-sessions <id>                  List task sessions
  agent reset-session <id> [--task-key K]   Reset session
  agent heartbeat <id>                      Invoke heartbeat manually

ADAPTER COMMANDS
  adapter models <type>                     List models for adapter
  adapter detect-model <type>               Detect current model
  adapter test-env <type>                   Test adapter environment

PROJECT COMMANDS
  project list                              List projects
  project get <id>                          Get project details
  project create --name "..." [opts]        Create project
  project update <id> [opts]                Update project
  project delete <id>                       Delete project

WORKSPACE COMMANDS
  workspace list <project-id>               List project workspaces
  workspace create <project-id> [opts]      Create workspace
  workspace update <proj-id> <ws-id> [opts] Update workspace
  workspace delete <proj-id> <ws-id>        Delete workspace
  workspace start <proj-id> <ws-id>         Start workspace runtime
  workspace stop <proj-id> <ws-id>          Stop workspace runtime
  workspace restart <proj-id> <ws-id>       Restart workspace runtime

GOAL COMMANDS
  goal list                                 List goals
  goal get <id>                             Get goal details
  goal create --title "..." [opts]          Create goal
  goal update <id> [opts]                   Update goal
  goal delete <id>                          Delete goal

ISSUE COMMANDS
  issue list [filters]                      List issues (many filters)
  issue get <id>                            Get issue details
  issue create --title "..." [opts]         Create issue
  issue update <id> [opts]                  Update issue
  issue delete <id>                         Delete issue
  issue comment <id> --body "..." [opts]    Add comment
  issue comments <id> [--after/--order/--limit] List comments
  issue comment-get <id> <comment-id>       Get single comment
  issue checkout <id> --agent-id <id>       Atomic checkout
  issue release <id>                        Release checkout
  issue documents <id>                      List documents
  issue document-get <id> <key>             Get document
  issue document-set <id> <key> [opts]      Upsert document
  issue document-revisions <id> <key>       List revisions
  issue document-restore <id> <key> <rev>   Restore revision
  issue document-delete <id> <key>          Delete document
  issue mark-read <id>                      Mark as read
  issue mark-unread <id>                    Mark as unread
  issue inbox-archive <id>                  Archive from inbox
  issue inbox-unarchive <id>                Unarchive from inbox
  issue attachments <id>                    List attachments
  issue attachment-upload <id> --file F     Upload attachment
  issue attachment-content <att-id>         Download attachment
  issue attachment-delete <att-id>          Delete attachment
  issue runs <id>                           List execution runs
  issue live-runs <id>                      List active runs
  issue active-run <id>                     Get current active run
  issue feedback-votes <id>                 List feedback votes
  issue feedback-vote <id> --value up/down  Submit feedback vote
  issue feedback-traces <id>                List feedback traces

FEEDBACK TRACE COMMANDS
  feedback-trace get <id>                   Get trace details
  feedback-trace bundle <id>                Get trace bundle
  feedback-trace list                       List company traces

LABEL COMMANDS
  label list                                List company labels
  label create --name "..." --color "#..."  Create label
  label delete <id>                         Delete label

ROUTINE COMMANDS
  routine list                              List routines
  routine get <id>                          Get routine details
  routine create --title "..." [opts]       Create routine
  routine update <id> [opts]                Update routine
  routine delete <id>                       Delete routine
  routine run <id>                          Manually trigger routine
  routine runs <id>                         List recent runs

TRIGGER COMMANDS
  trigger create <routine-id> [opts]        Create routine trigger
  trigger update <trigger-id> [opts]        Update trigger
  trigger delete <trigger-id>               Delete trigger
  trigger rotate-secret <trigger-id>        Rotate webhook secret

APPROVAL COMMANDS
  approval list [--status pending]          List approvals
  approval get <id>                         Get approval details
  approval approve <id> [--note "..."]      Approve
  approval reject <id> [--note "..."]       Reject
  approval request-revision <id> [--note]   Request revision
  approval resubmit <id>                    Resubmit after revision
  approval comment <id> --body "..."        Comment on approval
  approval issues <id>                      List linked issues

COST & BUDGET COMMANDS
  cost summary [--from/--to]                Company cost summary
  cost by-agent [--from/--to]               By agent
  cost by-agent-model [--from/--to]         By agent + model
  cost by-project [--from/--to]             By project
  cost by-provider [--from/--to]            By provider
  cost by-biller [--from/--to]              By biller
  cost finance [--from/--to]                Finance summary
  cost finance-by-biller [--from/--to]      Finance by biller
  cost finance-by-kind [--from/--to]        Finance by kind
  cost finance-events [--from/--to/--limit] Finance events
  cost window-spend                         Current spending window
  cost quota-windows                        Provider quotas
  cost log-cost-event --data '...'          Log cost event
  cost log-finance-event --data '...'       Log finance event
  budget overview                           Budget overview
  budget update [opts]                      Update company budget
  budget reset                              Reset budget
  budget soft-reset                         Soft reset budget
  budget agent-update <id> [opts]           Update agent budget

SECRET COMMANDS
  secret list                               List secrets
  secret providers                          List secret providers
  secret create --name --value [opts]       Create secret
  secret update <id> [opts]                 Update secret metadata
  secret rotate <id> --value "..."          Rotate secret value
  secret delete <id>                        Delete secret

OTHER COMMANDS
  dashboard                                 Company dashboard
  activity [--agent-id/--entity-type/...]   Activity log
  org                                       Org chart (JSON)
  health                                    Instance health check

OPTIONS (global)
  --company-id <id>                         Override PAPERCLIP_COMPANY_ID
EOF
}

# --- parse global options ---

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --company-id) COMPANY_ID="$2"; shift 2;;
    --help|-h) usage; exit 0;;
    *) POSITIONAL+=("$1"); shift;;
  esac
done
set -- "${POSITIONAL[@]}"

# --- cost date helper ---

parse_cost_opts() {
  COST_QUERY=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --from) COST_QUERY+="from=${2}&"; shift 2;;
      --to) COST_QUERY+="to=${2}&"; shift 2;;
      --limit) COST_QUERY+="limit=${2}&"; shift 2;;
      *) shift;;
    esac
  done
}

# --- commands ---

cmd="${1:-help}"
sub="${2:-}"

case "$cmd" in

  # ======================== COMPANY ========================
  company)
    case "$sub" in
      list)
        api GET "/api/companies"
        ;;
      get)
        api GET "/api/companies/${3:?company-id required}"
        ;;
      create)
        require_jq
        local_name="${3:?company name required}"
        local_desc="${4:-}"
        payload=$(jq -n --arg name "$local_name" --arg desc "$local_desc" \
          '{name: $name} + (if $desc != "" then {description: $desc} else {} end)')
        api POST "/api/companies" -d "$payload"
        ;;
      update)
        require_jq
        company_id="${3:?company-id required}"
        shift 3
        name="" desc="" status="" budget="" require_approval="" brand_color=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            --budget-monthly-cents) budget="$2"; shift 2;;
            --require-board-approval) require_approval="$2"; shift 2;;
            --brand-color) brand_color="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$name" --arg desc "$desc" --arg status "$status" \
          --arg budget "$budget" --arg approval "$require_approval" \
          --arg brandColor "$brand_color" \
          '(if $name != "" then {name: $name} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $status != "" then {status: $status} else {} end) +
           (if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end) +
           (if $approval != "" then {requireBoardApprovalForNewAgents: ($approval == "true")} else {} end) +
           (if $brandColor != "" then {brandColor: $brandColor} else {} end)')
        api PATCH "/api/companies/${company_id}" -d "$payload"
        ;;
      archive)
        api POST "/api/companies/${3:?company-id required}/archive" -d '{}'
        ;;
      delete)
        api DELETE "/api/companies/${3:?company-id required}"
        ;;
      export)
        export_id="${3:-$COMPANY_ID}"
        [[ -z "$export_id" ]] && { echo "Error: company-id required (positional or --company-id)" >&2; exit 1; }
        api POST "/api/companies/${export_id}/export" -d '{}'
        ;;
      export-preview)
        export_id="${3:-$COMPANY_ID}"
        [[ -z "$export_id" ]] && { echo "Error: company-id required (positional or --company-id)" >&2; exit 1; }
        api POST "/api/companies/${export_id}/export/preview" -d '{}'
        ;;
      import)
        shift 2; parse_data_arg "$@"
        api POST "/api/import" -d "$DATA_ARG"
        ;;
      import-preview)
        shift 2; parse_data_arg "$@"
        api POST "/api/import/preview" -d "$DATA_ARG"
        ;;
      safe-import-preview)
        company_id="${3:?company-id required}"
        shift 3; parse_data_arg "$@"
        api POST "/api/companies/${company_id}/imports/preview" -d "$DATA_ARG"
        ;;
      safe-import)
        company_id="${3:?company-id required}"
        shift 3; parse_data_arg "$@"
        api POST "/api/companies/${company_id}/imports/apply" -d "$DATA_ARG"
        ;;
      *) echo "Usage: company list|get|create|update|archive|delete|export|export-preview|import|import-preview|safe-import-preview|safe-import"; exit 1;;
    esac
    ;;

  # ======================== AGENT ========================
  agent)
    case "$sub" in
      list)
        require_company
        api GET "/api/companies/${COMPANY_ID}/agents"
        ;;
      get)
        api GET "/api/agents/${3:?agent-id required}"
        ;;
      create)
        require_company
        require_jq
        local_name="${3:?agent name required}"
        local_role="${4:?agent role required}"
        shift 4
        title="" adapter="claude_local" icon="" capabilities="" budget="" reports_to=""
        adapter_config="" runtime_config=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --adapter) adapter="$2"; shift 2;;
            --icon) icon="$2"; shift 2;;
            --capabilities) capabilities="$2"; shift 2;;
            --budget-monthly-cents) budget="$2"; shift 2;;
            --reports-to) reports_to="$2"; shift 2;;
            --adapter-config) adapter_config="$2"; shift 2;;
            --runtime-config) runtime_config="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$local_name" --arg role "$local_role" \
          --arg title "$title" --arg adapter "$adapter" \
          --arg icon "$icon" --arg capabilities "$capabilities" \
          --arg budget "$budget" --arg reportsTo "$reports_to" \
          --arg adapterConfig "$adapter_config" --arg runtimeConfig "$runtime_config" \
          '{name: $name, role: $role, adapterType: $adapter} +
           (if $title != "" then {title: $title} else {} end) +
           (if $icon != "" then {icon: $icon} else {} end) +
           (if $capabilities != "" then {capabilities: $capabilities} else {} end) +
           (if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end) +
           (if $reportsTo != "" then {reportsTo: $reportsTo} else {} end) +
           (if $adapterConfig != "" then {adapterConfig: ($adapterConfig | fromjson)} else {} end) +
           (if $runtimeConfig != "" then {runtimeConfig: ($runtimeConfig | fromjson)} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/agents" -d "$payload"
        ;;
      hire)
        require_company
        require_jq
        local_name="${3:?agent name required}"
        local_role="${4:?agent role required}"
        shift 4
        title="" adapter="claude_local" icon="" capabilities="" budget="" reports_to=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --adapter) adapter="$2"; shift 2;;
            --icon) icon="$2"; shift 2;;
            --capabilities) capabilities="$2"; shift 2;;
            --budget-monthly-cents) budget="$2"; shift 2;;
            --reports-to) reports_to="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$local_name" --arg role "$local_role" \
          --arg title "$title" --arg adapter "$adapter" \
          --arg icon "$icon" --arg capabilities "$capabilities" \
          --arg budget "$budget" --arg reportsTo "$reports_to" \
          '{name: $name, role: $role, adapterType: $adapter} +
           (if $title != "" then {title: $title} else {} end) +
           (if $icon != "" then {icon: $icon} else {} end) +
           (if $capabilities != "" then {capabilities: $capabilities} else {} end) +
           (if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end) +
           (if $reportsTo != "" then {reportsTo: $reportsTo} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/agent-hires" -d "$payload"
        ;;
      update)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        name="" role="" title="" icon="" capabilities="" adapter_type=""
        budget="" reports_to="" metadata=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --role) role="$2"; shift 2;;
            --title) title="$2"; shift 2;;
            --icon) icon="$2"; shift 2;;
            --capabilities) capabilities="$2"; shift 2;;
            --adapter-type) adapter_type="$2"; shift 2;;
            --budget-monthly-cents) budget="$2"; shift 2;;
            --reports-to) reports_to="$2"; shift 2;;
            --metadata) metadata="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$name" --arg role "$role" --arg title "$title" \
          --arg icon "$icon" --arg capabilities "$capabilities" \
          --arg adapterType "$adapter_type" --arg budget "$budget" \
          --arg reportsTo "$reports_to" --arg metadata "$metadata" \
          '(if $name != "" then {name: $name} else {} end) +
           (if $role != "" then {role: $role} else {} end) +
           (if $title != "" then {title: $title} else {} end) +
           (if $icon != "" then {icon: $icon} else {} end) +
           (if $capabilities != "" then {capabilities: $capabilities} else {} end) +
           (if $adapterType != "" then {adapterType: $adapterType} else {} end) +
           (if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end) +
           (if $reportsTo != "" then {reportsTo: $reportsTo} else {} end) +
           (if $metadata != "" then {metadata: ($metadata | fromjson)} else {} end)')
        api PATCH "/api/agents/${agent_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/agents/${3:?agent-id required}"
        ;;
      pause)
        api POST "/api/agents/${3:?agent-id required}/pause" -d '{}'
        ;;
      resume)
        api POST "/api/agents/${3:?agent-id required}/resume" -d '{}'
        ;;
      terminate)
        api POST "/api/agents/${3:?agent-id required}/terminate" -d '{}'
        ;;
      wakeup)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        source="" trigger_detail="" reason=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --source) source="$2"; shift 2;;
            --trigger-detail) trigger_detail="$2"; shift 2;;
            --reason) reason="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg source "$source" --arg triggerDetail "$trigger_detail" \
          --arg reason "$reason" \
          '(if $source != "" then {source: $source} else {} end) +
           (if $triggerDetail != "" then {triggerDetail: $triggerDetail} else {} end) +
           (if $reason != "" then {reason: $reason} else {} end)')
        api POST "/api/agents/${agent_id}/wakeup" -d "$payload"
        ;;
      config)
        api GET "/api/agents/${3:?agent-id required}/configuration"
        ;;
      config-revisions)
        api GET "/api/agents/${3:?agent-id required}/config-revisions"
        ;;
      config-rollback)
        agent_id="${3:?agent-id required}"
        revision_id="${4:?revision-id required}"
        api POST "/api/agents/${agent_id}/config-revisions/${revision_id}/rollback" -d '{}'
        ;;
      instructions-get)
        api GET "/api/agents/${3:?agent-id required}/instructions-bundle"
        ;;
      instructions-file)
        agent_id="${3:?agent-id required}"
        shift 3
        file_path=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --path) file_path="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$file_path" ]] && { echo "Error: --path required" >&2; exit 1; }
        encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$file_path', safe=''))" 2>/dev/null || echo "$file_path")
        api GET "/api/agents/${agent_id}/instructions-bundle/file?path=${encoded_path}"
        ;;
      instructions-set)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        file_path="" content=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --path) file_path="$2"; shift 2;;
            --content) content="$2"; shift 2;;
            --file) content="$(cat "$2")"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$file_path" ]] && file_path="AGENTS.md"
        [[ -z "$content" ]] && { echo "Error: --content or --file required" >&2; exit 1; }
        payload=$(jq -n --arg path "$file_path" --arg content "$content" \
          '{path: $path, content: $content}')
        api PUT "/api/agents/${agent_id}/instructions-bundle/file" -d "$payload"
        ;;
      instructions-delete)
        agent_id="${3:?agent-id required}"
        shift 3
        file_path=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --path) file_path="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$file_path" ]] && { echo "Error: --path required" >&2; exit 1; }
        encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$file_path', safe=''))" 2>/dev/null || echo "$file_path")
        api DELETE "/api/agents/${agent_id}/instructions-bundle/file?path=${encoded_path}"
        ;;
      instructions-update)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        mode="" root_path="" entry_file=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --mode) mode="$2"; shift 2;;
            --root-path) root_path="$2"; shift 2;;
            --entry-file) entry_file="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg mode "$mode" --arg rootPath "$root_path" --arg entryFile "$entry_file" \
          '(if $mode != "" then {mode: $mode} else {} end) +
           (if $rootPath != "" then {rootPath: $rootPath} else {} end) +
           (if $entryFile != "" then {entryFile: $entryFile} else {} end)')
        api PATCH "/api/agents/${agent_id}/instructions-bundle" -d "$payload"
        ;;
      skills)
        api GET "/api/agents/${3:?agent-id required}/skills"
        ;;
      skills-sync)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        skills=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --skills) skills="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$skills" ]] && { echo "Error: --skills required (comma-separated)" >&2; exit 1; }
        # Convert comma-separated to JSON array
        payload=$(echo "$skills" | tr ',' '\n' | jq -R . | jq -s '{desiredSkills: .}')
        api POST "/api/agents/${agent_id}/skills/sync" -d "$payload"
        ;;
      keys)
        api GET "/api/agents/${3:?agent-id required}/keys"
        ;;
      keys-create)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        key_name=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) key_name="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$key_name" ]] && { echo "Error: --name required" >&2; exit 1; }
        payload=$(jq -n --arg name "$key_name" '{name: $name}')
        api POST "/api/agents/${agent_id}/keys" -d "$payload"
        ;;
      keys-revoke)
        agent_id="${3:?agent-id required}"
        key_id="${4:?key-id required}"
        api DELETE "/api/agents/${agent_id}/keys/${key_id}"
        ;;
      runtime-state)
        api GET "/api/agents/${3:?agent-id required}/runtime-state"
        ;;
      task-sessions)
        api GET "/api/agents/${3:?agent-id required}/task-sessions"
        ;;
      reset-session)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        task_key=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --task-key) task_key="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg taskKey "$task_key" \
          'if $taskKey != "" then {taskKey: $taskKey} else {taskKey: null} end')
        api POST "/api/agents/${agent_id}/runtime-state/reset-session" -d "$payload"
        ;;
      heartbeat)
        api POST "/api/agents/${3:?agent-id required}/heartbeat/invoke" -d '{}'
        ;;
      *) echo "Usage: agent list|get|create|hire|update|delete|pause|resume|terminate|wakeup|config|config-revisions|config-rollback|instructions-get|instructions-file|instructions-set|instructions-delete|instructions-update|skills|skills-sync|keys|keys-create|keys-revoke|runtime-state|task-sessions|reset-session|heartbeat"; exit 1;;
    esac
    ;;

  # ======================== ADAPTER ========================
  adapter)
    require_company
    case "$sub" in
      models)
        adapter_type="${3:?adapter-type required}"
        api GET "/api/companies/${COMPANY_ID}/adapters/${adapter_type}/models"
        ;;
      detect-model)
        adapter_type="${3:?adapter-type required}"
        api GET "/api/companies/${COMPANY_ID}/adapters/${adapter_type}/detect-model"
        ;;
      test-env)
        require_jq
        adapter_type="${3:?adapter-type required}"
        shift 3
        adapter_config="{}"
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --adapter-config) adapter_config="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --argjson config "$adapter_config" '{adapterConfig: $config}')
        api POST "/api/companies/${COMPANY_ID}/adapters/${adapter_type}/test-environment" -d "$payload"
        ;;
      *) echo "Usage: adapter models|detect-model|test-env"; exit 1;;
    esac
    ;;

  # ======================== PROJECT ========================
  project)
    case "$sub" in
      list)
        require_company
        api GET "/api/companies/${COMPANY_ID}/projects"
        ;;
      get)
        api GET "/api/projects/${3:?project-id required}"
        ;;
      create)
        require_company
        require_jq
        shift 2
        name="" desc="" goal_id="" goal_ids="" lead_id="" target_date="" color="" status=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --goal-id) goal_id="$2"; shift 2;;
            --goal-ids) goal_ids="$2"; shift 2;;
            --lead-agent-id) lead_id="$2"; shift 2;;
            --target-date) target_date="$2"; shift 2;;
            --color) color="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$name" ]] && { echo "Error: --name required" >&2; exit 1; }
        # Convert comma-separated goal_ids to JSON array
        goal_ids_json="null"
        if [[ -n "$goal_ids" ]]; then
          goal_ids_json=$(echo "$goal_ids" | tr ',' '\n' | jq -R . | jq -s .)
        fi
        payload=$(jq -n \
          --arg name "$name" --arg desc "$desc" \
          --arg goalId "$goal_id" --argjson goalIds "$goal_ids_json" \
          --arg leadId "$lead_id" --arg targetDate "$target_date" \
          --arg color "$color" --arg status "$status" \
          '{name: $name} +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $goalIds != null then {goalIds: $goalIds} else
             (if $goalId != "" then {goalId: $goalId} else {} end)
           end) +
           (if $leadId != "" then {leadAgentId: $leadId} else {} end) +
           (if $targetDate != "" then {targetDate: $targetDate} else {} end) +
           (if $color != "" then {color: $color} else {} end) +
           (if $status != "" then {status: $status} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/projects" -d "$payload"
        ;;
      update)
        require_jq
        project_id="${3:?project-id required}"
        shift 3
        name="" desc="" status="" lead_id="" target_date="" color=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            --lead-agent-id) lead_id="$2"; shift 2;;
            --target-date) target_date="$2"; shift 2;;
            --color) color="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$name" --arg desc "$desc" \
          --arg status "$status" --arg leadId "$lead_id" \
          --arg targetDate "$target_date" --arg color "$color" \
          '(if $name != "" then {name: $name} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $status != "" then {status: $status} else {} end) +
           (if $leadId != "" then {leadAgentId: $leadId} else {} end) +
           (if $targetDate != "" then {targetDate: $targetDate} else {} end) +
           (if $color != "" then {color: $color} else {} end)')
        api PATCH "/api/projects/${project_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/projects/${3:?project-id required}"
        ;;
      *) echo "Usage: project list|get|create|update|delete"; exit 1;;
    esac
    ;;

  # ======================== WORKSPACE ========================
  workspace)
    case "$sub" in
      list)
        api GET "/api/projects/${3:?project-id required}/workspaces"
        ;;
      create)
        require_jq
        project_id="${3:?project-id required}"
        shift 3
        name="" source_type="" cwd="" repo_url="" repo_ref="" setup_cmd="" cleanup_cmd=""
        remote_provider="" remote_ref=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --source-type) source_type="$2"; shift 2;;
            --cwd) cwd="$2"; shift 2;;
            --repo-url) repo_url="$2"; shift 2;;
            --repo-ref) repo_ref="$2"; shift 2;;
            --setup-command) setup_cmd="$2"; shift 2;;
            --cleanup-command) cleanup_cmd="$2"; shift 2;;
            --remote-provider) remote_provider="$2"; shift 2;;
            --remote-workspace-ref) remote_ref="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$name" ]] && { echo "Error: --name required" >&2; exit 1; }
        [[ -z "$source_type" ]] && { echo "Error: --source-type required" >&2; exit 1; }
        payload=$(jq -n \
          --arg name "$name" --arg sourceType "$source_type" \
          --arg cwd "$cwd" --arg repoUrl "$repo_url" --arg repoRef "$repo_ref" \
          --arg setupCmd "$setup_cmd" --arg cleanupCmd "$cleanup_cmd" \
          --arg remoteProvider "$remote_provider" --arg remoteRef "$remote_ref" \
          '{name: $name, sourceType: $sourceType} +
           (if $cwd != "" then {cwd: $cwd} else {} end) +
           (if $repoUrl != "" then {repoUrl: $repoUrl} else {} end) +
           (if $repoRef != "" then {repoRef: $repoRef} else {} end) +
           (if $setupCmd != "" then {setupCommand: $setupCmd} else {} end) +
           (if $cleanupCmd != "" then {cleanupCommand: $cleanupCmd} else {} end) +
           (if $remoteProvider != "" then {remoteProvider: $remoteProvider} else {} end) +
           (if $remoteRef != "" then {remoteWorkspaceRef: $remoteRef} else {} end)')
        api POST "/api/projects/${project_id}/workspaces" -d "$payload"
        ;;
      update)
        require_jq
        project_id="${3:?project-id required}"
        workspace_id="${4:?workspace-id required}"
        shift 4
        name="" source_type="" cwd="" repo_url="" repo_ref="" setup_cmd="" cleanup_cmd=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --source-type) source_type="$2"; shift 2;;
            --cwd) cwd="$2"; shift 2;;
            --repo-url) repo_url="$2"; shift 2;;
            --repo-ref) repo_ref="$2"; shift 2;;
            --setup-command) setup_cmd="$2"; shift 2;;
            --cleanup-command) cleanup_cmd="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg name "$name" --arg sourceType "$source_type" \
          --arg cwd "$cwd" --arg repoUrl "$repo_url" --arg repoRef "$repo_ref" \
          --arg setupCmd "$setup_cmd" --arg cleanupCmd "$cleanup_cmd" \
          '(if $name != "" then {name: $name} else {} end) +
           (if $sourceType != "" then {sourceType: $sourceType} else {} end) +
           (if $cwd != "" then {cwd: $cwd} else {} end) +
           (if $repoUrl != "" then {repoUrl: $repoUrl} else {} end) +
           (if $repoRef != "" then {repoRef: $repoRef} else {} end) +
           (if $setupCmd != "" then {setupCommand: $setupCmd} else {} end) +
           (if $cleanupCmd != "" then {cleanupCommand: $cleanupCmd} else {} end)')
        api PATCH "/api/projects/${project_id}/workspaces/${workspace_id}" -d "$payload"
        ;;
      delete)
        project_id="${3:?project-id required}"
        workspace_id="${4:?workspace-id required}"
        api DELETE "/api/projects/${project_id}/workspaces/${workspace_id}"
        ;;
      start)
        project_id="${3:?project-id required}"
        workspace_id="${4:?workspace-id required}"
        api POST "/api/projects/${project_id}/workspaces/${workspace_id}/runtime-services/start" -d '{}'
        ;;
      stop)
        project_id="${3:?project-id required}"
        workspace_id="${4:?workspace-id required}"
        api POST "/api/projects/${project_id}/workspaces/${workspace_id}/runtime-services/stop" -d '{}'
        ;;
      restart)
        project_id="${3:?project-id required}"
        workspace_id="${4:?workspace-id required}"
        api POST "/api/projects/${project_id}/workspaces/${workspace_id}/runtime-services/restart" -d '{}'
        ;;
      *) echo "Usage: workspace list|create|update|delete|start|stop|restart"; exit 1;;
    esac
    ;;

  # ======================== GOAL ========================
  goal)
    case "$sub" in
      list)
        require_company
        api GET "/api/companies/${COMPANY_ID}/goals"
        ;;
      get)
        api GET "/api/goals/${3:?goal-id required}"
        ;;
      create)
        require_company
        require_jq
        shift 2
        title="" desc="" level="" parent_id="" owner_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --level) level="$2"; shift 2;;
            --parent-id) parent_id="$2"; shift 2;;
            --owner-agent-id) owner_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$title" ]] && { echo "Error: --title required" >&2; exit 1; }
        payload=$(jq -n \
          --arg title "$title" --arg desc "$desc" \
          --arg level "$level" --arg parentId "$parent_id" \
          --arg ownerId "$owner_id" \
          '{title: $title} +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $level != "" then {level: $level} else {} end) +
           (if $parentId != "" then {parentId: $parentId} else {} end) +
           (if $ownerId != "" then {ownerAgentId: $ownerId} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/goals" -d "$payload"
        ;;
      update)
        require_jq
        goal_id="${3:?goal-id required}"
        shift 3
        title="" desc="" status="" parent_id="" owner_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            --parent-id) parent_id="$2"; shift 2;;
            --owner-agent-id) owner_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg title "$title" --arg desc "$desc" --arg status "$status" \
          --arg parentId "$parent_id" --arg ownerId "$owner_id" \
          '(if $title != "" then {title: $title} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $status != "" then {status: $status} else {} end) +
           (if $parentId != "" then {parentId: $parentId} else {} end) +
           (if $ownerId != "" then {ownerAgentId: $ownerId} else {} end)')
        api PATCH "/api/goals/${goal_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/goals/${3:?goal-id required}"
        ;;
      *) echo "Usage: goal list|get|create|update|delete"; exit 1;;
    esac
    ;;

  # ======================== ISSUE ========================
  issue)
    case "$sub" in
      list)
        require_company
        shift 2
        query=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --status) query+="status=${2}&"; shift 2;;
            --assignee-agent-id) query+="assigneeAgentId=${2}&"; shift 2;;
            --assignee-user-id) query+="assigneeUserId=${2}&"; shift 2;;
            --participant-agent-id) query+="participantAgentId=${2}&"; shift 2;;
            --project-id) query+="projectId=${2}&"; shift 2;;
            --label-id) query+="labelId=${2}&"; shift 2;;
            --origin-kind) query+="originKind=${2}&"; shift 2;;
            --origin-id) query+="originId=${2}&"; shift 2;;
            --q) query+="q=${2}&"; shift 2;;
            --include-routine-executions) query+="includeRoutineExecutions=true&"; shift;;
            --execution-workspace-id) query+="executionWorkspaceId=${2}&"; shift 2;;
            *) shift;;
          esac
        done
        api GET "/api/companies/${COMPANY_ID}/issues?${query}"
        ;;
      get)
        api GET "/api/issues/${3:?issue-id required}"
        ;;
      create)
        require_company
        require_jq
        shift 2
        title="" desc="" priority="" assignee="" assignee_user="" parent=""
        project_id="" goal_id="" label_ids="" billing_code=""
        execution_workspace_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --priority) priority="$2"; shift 2;;
            --assignee-agent-id) assignee="$2"; shift 2;;
            --assignee-user-id) assignee_user="$2"; shift 2;;
            --parent-id) parent="$2"; shift 2;;
            --project-id) project_id="$2"; shift 2;;
            --goal-id) goal_id="$2"; shift 2;;
            --label-ids) label_ids="$2"; shift 2;;
            --billing-code) billing_code="$2"; shift 2;;
            --execution-workspace-id) execution_workspace_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$title" ]] && { echo "Error: --title required" >&2; exit 1; }
        label_ids_json="null"
        if [[ -n "$label_ids" ]]; then
          label_ids_json=$(echo "$label_ids" | tr ',' '\n' | jq -R . | jq -s .)
        fi
        payload=$(jq -n \
          --arg title "$title" --arg desc "$desc" \
          --arg priority "$priority" --arg assignee "$assignee" \
          --arg assigneeUser "$assignee_user" \
          --arg parent "$parent" --arg projectId "$project_id" \
          --arg goalId "$goal_id" --argjson labelIds "$label_ids_json" \
          --arg billingCode "$billing_code" \
          --arg execWsId "$execution_workspace_id" \
          '{title: $title} +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $priority != "" then {priority: $priority} else {} end) +
           (if $assignee != "" then {assigneeAgentId: $assignee} else {} end) +
           (if $assigneeUser != "" then {assigneeUserId: $assigneeUser} else {} end) +
           (if $parent != "" then {parentId: $parent} else {} end) +
           (if $projectId != "" then {projectId: $projectId} else {} end) +
           (if $goalId != "" then {goalId: $goalId} else {} end) +
           (if $labelIds != null then {labelIds: $labelIds} else {} end) +
           (if $billingCode != "" then {billingCode: $billingCode} else {} end) +
           (if $execWsId != "" then {executionWorkspaceId: $execWsId} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/issues" -d "$payload"
        ;;
      update)
        require_jq
        issue_id="${3:?issue-id required}"
        shift 3
        status="" title="" desc="" priority="" assignee="" assignee_user=""
        project_id="" goal_id="" parent_id="" label_ids="" billing_code=""
        execution_workspace_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --status) status="$2"; shift 2;;
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --priority) priority="$2"; shift 2;;
            --assignee-agent-id) assignee="$2"; shift 2;;
            --assignee-user-id) assignee_user="$2"; shift 2;;
            --project-id) project_id="$2"; shift 2;;
            --goal-id) goal_id="$2"; shift 2;;
            --parent-id) parent_id="$2"; shift 2;;
            --label-ids) label_ids="$2"; shift 2;;
            --billing-code) billing_code="$2"; shift 2;;
            --execution-workspace-id) execution_workspace_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        label_ids_json="null"
        if [[ -n "$label_ids" ]]; then
          label_ids_json=$(echo "$label_ids" | tr ',' '\n' | jq -R . | jq -s .)
        fi
        payload=$(jq -n \
          --arg status "$status" --arg title "$title" \
          --arg desc "$desc" --arg priority "$priority" \
          --arg assignee "$assignee" --arg assigneeUser "$assignee_user" \
          --arg projectId "$project_id" --arg goalId "$goal_id" \
          --arg parentId "$parent_id" --argjson labelIds "$label_ids_json" \
          --arg billingCode "$billing_code" \
          --arg execWsId "$execution_workspace_id" \
          '(if $status != "" then {status: $status} else {} end) +
           (if $title != "" then {title: $title} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $priority != "" then {priority: $priority} else {} end) +
           (if $assignee != "" then {assigneeAgentId: $assignee} else {} end) +
           (if $assigneeUser != "" then {assigneeUserId: $assigneeUser} else {} end) +
           (if $projectId != "" then {projectId: $projectId} else {} end) +
           (if $goalId != "" then {goalId: $goalId} else {} end) +
           (if $parentId != "" then {parentId: $parentId} else {} end) +
           (if $labelIds != null then {labelIds: $labelIds} else {} end) +
           (if $billingCode != "" then {billingCode: $billingCode} else {} end) +
           (if $execWsId != "" then {executionWorkspaceId: $execWsId} else {} end)')
        api PATCH "/api/issues/${issue_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/issues/${3:?issue-id required}"
        ;;
      comment)
        require_jq
        issue_id="${3:?issue-id required}"
        shift 3
        body="" reopen="" interrupt=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --body) body="$2"; shift 2;;
            --reopen) reopen="true"; shift;;
            --interrupt) interrupt="true"; shift;;
            *) shift;;
          esac
        done
        [[ -z "$body" ]] && { echo "Error: --body required" >&2; exit 1; }
        payload=$(jq -n --arg body "$body" --arg reopen "$reopen" --arg interrupt "$interrupt" \
          '{body: $body} +
           (if $reopen == "true" then {reopen: true} else {} end) +
           (if $interrupt == "true" then {interrupt: true} else {} end)')
        api POST "/api/issues/${issue_id}/comments" -d "$payload"
        ;;
      comments)
        issue_id="${3:?issue-id required}"
        shift 3
        query=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --after) query+="after=${2}&"; shift 2;;
            --order) query+="order=${2}&"; shift 2;;
            --limit) query+="limit=${2}&"; shift 2;;
            *) shift;;
          esac
        done
        api GET "/api/issues/${issue_id}/comments?${query}"
        ;;
      comment-get)
        issue_id="${3:?issue-id required}"
        comment_id="${4:?comment-id required}"
        api GET "/api/issues/${issue_id}/comments/${comment_id}"
        ;;
      checkout)
        require_jq
        issue_id="${3:?issue-id required}"
        shift 3
        agent_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --agent-id) agent_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$agent_id" ]] && { echo "Error: --agent-id required" >&2; exit 1; }
        payload=$(jq -n --arg agentId "$agent_id" '{agentId: $agentId}')
        api POST "/api/issues/${issue_id}/checkout" -d "$payload"
        ;;
      release)
        api POST "/api/issues/${3:?issue-id required}/release" -d '{}'
        ;;
      documents)
        api GET "/api/issues/${3:?issue-id required}/documents"
        ;;
      document-get)
        issue_id="${3:?issue-id required}"
        key="${4:?document key required}"
        api GET "/api/issues/${issue_id}/documents/${key}"
        ;;
      document-set)
        require_jq
        issue_id="${3:?issue-id required}"
        key="${4:?document key required}"
        shift 4
        title="" doc_body=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --body) doc_body="$2"; shift 2;;
            --file) doc_body="$(cat "$2")"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$doc_body" ]] && { echo "Error: --body or --file required" >&2; exit 1; }
        payload=$(jq -n --arg title "$title" --arg body "$doc_body" \
          '{body: $body, format: "markdown"} +
           (if $title != "" then {title: $title} else {} end)')
        api PUT "/api/issues/${issue_id}/documents/${key}" -d "$payload"
        ;;
      document-revisions)
        issue_id="${3:?issue-id required}"
        key="${4:?document key required}"
        api GET "/api/issues/${issue_id}/documents/${key}/revisions"
        ;;
      document-restore)
        issue_id="${3:?issue-id required}"
        key="${4:?document key required}"
        revision_id="${5:?revision-id required}"
        api POST "/api/issues/${issue_id}/documents/${key}/revisions/${revision_id}/restore" -d '{}'
        ;;
      document-delete)
        issue_id="${3:?issue-id required}"
        key="${4:?document key required}"
        api DELETE "/api/issues/${issue_id}/documents/${key}"
        ;;
      mark-read)
        api POST "/api/issues/${3:?issue-id required}/read" -d '{}'
        ;;
      mark-unread)
        api DELETE "/api/issues/${3:?issue-id required}/read"
        ;;
      inbox-archive)
        api POST "/api/issues/${3:?issue-id required}/inbox-archive" -d '{}'
        ;;
      inbox-unarchive)
        api DELETE "/api/issues/${3:?issue-id required}/inbox-archive"
        ;;
      attachments)
        api GET "/api/issues/${3:?issue-id required}/attachments"
        ;;
      attachment-upload)
        require_company
        issue_id="${3:?issue-id required}"
        shift 3
        file_path="" comment_id=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --file) file_path="$2"; shift 2;;
            --comment-id) comment_id="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$file_path" ]] && { echo "Error: --file required" >&2; exit 1; }
        [[ ! -f "$file_path" ]] && { echo "Error: file not found: $file_path" >&2; exit 1; }
        extra_args=(-F "file=@${file_path}")
        [[ -n "$comment_id" ]] && extra_args+=(-F "issueCommentId=${comment_id}")
        api_upload POST "/api/companies/${COMPANY_ID}/issues/${issue_id}/attachments" "${extra_args[@]}"
        ;;
      attachment-content)
        attachment_id="${3:?attachment-id required}"
        # Binary download — stream to stdout, fail on HTTP errors
        if [[ -z "$SESSION_COOKIE" ]]; then sign_in; fi
        curl -sSf -H "Cookie: ${SESSION_COOKIE}" -H "Origin: ${API_URL}" \
          "${API_URL}/api/attachments/${attachment_id}/content"
        ;;
      attachment-delete)
        api DELETE "/api/attachments/${3:?attachment-id required}"
        ;;
      runs)
        api GET "/api/issues/${3:?issue-id required}/runs"
        ;;
      live-runs)
        api GET "/api/issues/${3:?issue-id required}/live-runs"
        ;;
      active-run)
        api GET "/api/issues/${3:?issue-id required}/active-run"
        ;;
      feedback-votes)
        api GET "/api/issues/${3:?issue-id required}/feedback-votes"
        ;;
      feedback-vote)
        require_jq
        issue_id="${3:?issue-id required}"
        shift 3
        value="" fb_comment=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --value) value="$2"; shift 2;;
            --comment) fb_comment="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$value" ]] && { echo "Error: --value required (up|down)" >&2; exit 1; }
        payload=$(jq -n --arg value "$value" --arg comment "$fb_comment" \
          '{value: $value} +
           (if $comment != "" then {comment: $comment} else {} end)')
        api POST "/api/issues/${issue_id}/feedback-votes" -d "$payload"
        ;;
      feedback-traces)
        api GET "/api/issues/${3:?issue-id required}/feedback-traces"
        ;;
      *) echo "Usage: issue list|get|create|update|delete|comment|comment-get|comments|checkout|release|documents|document-get|document-set|document-revisions|document-restore|document-delete|mark-read|mark-unread|inbox-archive|inbox-unarchive|attachments|attachment-upload|attachment-content|attachment-delete|runs|live-runs|active-run|feedback-votes|feedback-vote|feedback-traces"; exit 1;;
    esac
    ;;

  # ======================== FEEDBACK TRACE ========================
  feedback-trace)
    case "$sub" in
      get)
        api GET "/api/feedback-traces/${3:?trace-id required}"
        ;;
      bundle)
        api GET "/api/feedback-traces/${3:?trace-id required}/bundle"
        ;;
      list)
        require_company
        shift 2
        query=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --status) query+="status=${2}&"; shift 2;;
            --target-type) query+="targetType=${2}&"; shift 2;;
            --vote-value) query+="voteValue=${2}&"; shift 2;;
            *) shift;;
          esac
        done
        api GET "/api/companies/${COMPANY_ID}/feedback-traces?${query}"
        ;;
      *) echo "Usage: feedback-trace get|bundle|list"; exit 1;;
    esac
    ;;

  # ======================== LABEL ========================
  label)
    case "$sub" in
      list)
        require_company
        api GET "/api/companies/${COMPANY_ID}/labels"
        ;;
      create)
        require_company
        require_jq
        shift 2
        name="" color=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --color) color="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$name" ]] && { echo "Error: --name required" >&2; exit 1; }
        [[ -z "$color" ]] && { echo "Error: --color required" >&2; exit 1; }
        payload=$(jq -n --arg name "$name" --arg color "$color" \
          '{name: $name, color: $color}')
        api POST "/api/companies/${COMPANY_ID}/labels" -d "$payload"
        ;;
      delete)
        api DELETE "/api/labels/${3:?label-id required}"
        ;;
      *) echo "Usage: label list|create|delete"; exit 1;;
    esac
    ;;

  # ======================== ROUTINE ========================
  routine)
    case "$sub" in
      list)
        require_company
        api GET "/api/companies/${COMPANY_ID}/routines"
        ;;
      get)
        api GET "/api/routines/${3:?routine-id required}"
        ;;
      create)
        require_company
        require_jq
        shift 2
        title="" desc="" project_id="" goal_id="" parent_issue_id=""
        assignee="" priority="" status="" concurrency="" catch_up="" variables=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --project-id) project_id="$2"; shift 2;;
            --goal-id) goal_id="$2"; shift 2;;
            --parent-issue-id) parent_issue_id="$2"; shift 2;;
            --assignee-agent-id) assignee="$2"; shift 2;;
            --priority) priority="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            --concurrency-policy) concurrency="$2"; shift 2;;
            --catch-up-policy) catch_up="$2"; shift 2;;
            --variables) variables="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$title" ]] && { echo "Error: --title required" >&2; exit 1; }
        [[ -z "$project_id" ]] && { echo "Error: --project-id required" >&2; exit 1; }
        [[ -z "$assignee" ]] && { echo "Error: --assignee-agent-id required" >&2; exit 1; }
        variables_json="null"
        if [[ -n "$variables" ]]; then
          variables_json="$variables"
        fi
        payload=$(jq -n \
          --arg title "$title" --arg desc "$desc" \
          --arg projectId "$project_id" --arg goalId "$goal_id" \
          --arg parentIssueId "$parent_issue_id" \
          --arg assignee "$assignee" --arg priority "$priority" \
          --arg status "$status" --arg concurrency "$concurrency" \
          --arg catchUp "$catch_up" --argjson variables "$variables_json" \
          '{title: $title, projectId: $projectId, assigneeAgentId: $assignee} +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $goalId != "" then {goalId: $goalId} else {} end) +
           (if $parentIssueId != "" then {parentIssueId: $parentIssueId} else {} end) +
           (if $priority != "" then {priority: $priority} else {} end) +
           (if $status != "" then {status: $status} else {} end) +
           (if $concurrency != "" then {concurrencyPolicy: $concurrency} else {} end) +
           (if $catchUp != "" then {catchUpPolicy: $catchUp} else {} end) +
           (if $variables != null then {variables: $variables} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/routines" -d "$payload"
        ;;
      update)
        require_jq
        routine_id="${3:?routine-id required}"
        shift 3
        title="" desc="" assignee="" priority="" status="" concurrency="" catch_up="" variables=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --title) title="$2"; shift 2;;
            --description) desc="$2"; shift 2;;
            --assignee-agent-id) assignee="$2"; shift 2;;
            --priority) priority="$2"; shift 2;;
            --status) status="$2"; shift 2;;
            --concurrency-policy) concurrency="$2"; shift 2;;
            --catch-up-policy) catch_up="$2"; shift 2;;
            --variables) variables="$2"; shift 2;;
            *) shift;;
          esac
        done
        variables_json="null"
        if [[ -n "$variables" ]]; then
          variables_json="$variables"
        fi
        payload=$(jq -n \
          --arg title "$title" --arg desc "$desc" \
          --arg assignee "$assignee" --arg priority "$priority" \
          --arg status "$status" --arg concurrency "$concurrency" \
          --arg catchUp "$catch_up" --argjson variables "$variables_json" \
          '(if $title != "" then {title: $title} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $assignee != "" then {assigneeAgentId: $assignee} else {} end) +
           (if $priority != "" then {priority: $priority} else {} end) +
           (if $status != "" then {status: $status} else {} end) +
           (if $concurrency != "" then {concurrencyPolicy: $concurrency} else {} end) +
           (if $catchUp != "" then {catchUpPolicy: $catchUp} else {} end) +
           (if $variables != null then {variables: $variables} else {} end)')
        api PATCH "/api/routines/${routine_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/routines/${3:?routine-id required}"
        ;;
      run)
        api POST "/api/routines/${3:?routine-id required}/run" -d '{}'
        ;;
      runs)
        api GET "/api/routines/${3:?routine-id required}/runs?limit=50"
        ;;
      *) echo "Usage: routine list|get|create|update|delete|run|runs"; exit 1;;
    esac
    ;;

  # ======================== TRIGGER ========================
  trigger)
    case "$sub" in
      create)
        require_jq
        routine_id="${3:?routine-id required}"
        shift 3
        kind="" label="" enabled="" cron="" timezone="" signing_mode="" replay_window=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --kind) kind="$2"; shift 2;;
            --label) label="$2"; shift 2;;
            --enabled) enabled="$2"; shift 2;;
            --cron) cron="$2"; shift 2;;
            --timezone) timezone="$2"; shift 2;;
            --signing-mode) signing_mode="$2"; shift 2;;
            --replay-window-sec) replay_window="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$kind" ]] && { echo "Error: --kind required (schedule|webhook|api)" >&2; exit 1; }
        payload=$(jq -n \
          --arg kind "$kind" --arg label "$label" --arg enabled "$enabled" \
          --arg cron "$cron" --arg timezone "$timezone" \
          --arg signingMode "$signing_mode" --arg replayWindow "$replay_window" \
          '{kind: $kind} +
           (if $label != "" then {label: $label} else {} end) +
           (if $enabled != "" then {enabled: ($enabled == "true")} else {} end) +
           (if $cron != "" then {cronExpression: $cron} else {} end) +
           (if $timezone != "" then {timezone: $timezone} else {} end) +
           (if $signingMode != "" then {signingMode: $signingMode} else {} end) +
           (if $replayWindow != "" then {replayWindowSec: ($replayWindow | tonumber)} else {} end)')
        api POST "/api/routines/${routine_id}/triggers" -d "$payload"
        ;;
      update)
        require_jq
        trigger_id="${3:?trigger-id required}"
        shift 3
        label="" enabled="" cron="" timezone="" signing_mode="" replay_window=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --label) label="$2"; shift 2;;
            --enabled) enabled="$2"; shift 2;;
            --cron) cron="$2"; shift 2;;
            --timezone) timezone="$2"; shift 2;;
            --signing-mode) signing_mode="$2"; shift 2;;
            --replay-window-sec) replay_window="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n \
          --arg label "$label" --arg enabled "$enabled" \
          --arg cron "$cron" --arg timezone "$timezone" \
          --arg signingMode "$signing_mode" --arg replayWindow "$replay_window" \
          '(if $label != "" then {label: $label} else {} end) +
           (if $enabled != "" then {enabled: ($enabled == "true")} else {} end) +
           (if $cron != "" then {cronExpression: $cron} else {} end) +
           (if $timezone != "" then {timezone: $timezone} else {} end) +
           (if $signingMode != "" then {signingMode: $signingMode} else {} end) +
           (if $replayWindow != "" then {replayWindowSec: ($replayWindow | tonumber)} else {} end)')
        api PATCH "/api/routine-triggers/${trigger_id}" -d "$payload"
        ;;
      delete)
        api DELETE "/api/routine-triggers/${3:?trigger-id required}"
        ;;
      rotate-secret)
        api POST "/api/routine-triggers/${3:?trigger-id required}/rotate-secret" -d '{}'
        ;;
      *) echo "Usage: trigger create|update|delete|rotate-secret"; exit 1;;
    esac
    ;;

  # ======================== APPROVAL ========================
  approval)
    case "$sub" in
      list)
        require_company
        shift 2
        query=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --status) query+="status=${2}&"; shift 2;;
            *) shift;;
          esac
        done
        api GET "/api/companies/${COMPANY_ID}/approvals?${query}"
        ;;
      get)
        api GET "/api/approvals/${3:?approval-id required}"
        ;;
      approve)
        require_jq
        approval_id="${3:?approval-id required}"
        shift 3
        note=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --note) note="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg note "$note" \
          'if $note != "" then {decisionNote: $note} else {} end')
        api POST "/api/approvals/${approval_id}/approve" -d "$payload"
        ;;
      reject)
        require_jq
        approval_id="${3:?approval-id required}"
        shift 3
        note=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --note) note="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg note "$note" \
          'if $note != "" then {decisionNote: $note} else {} end')
        api POST "/api/approvals/${approval_id}/reject" -d "$payload"
        ;;
      request-revision)
        require_jq
        approval_id="${3:?approval-id required}"
        shift 3
        note=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --note) note="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg note "$note" \
          'if $note != "" then {decisionNote: $note} else {} end')
        api POST "/api/approvals/${approval_id}/request-revision" -d "$payload"
        ;;
      resubmit)
        api POST "/api/approvals/${3:?approval-id required}/resubmit" -d '{}'
        ;;
      comment)
        require_jq
        approval_id="${3:?approval-id required}"
        shift 3
        body=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --body) body="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$body" ]] && { echo "Error: --body required" >&2; exit 1; }
        payload=$(jq -n --arg body "$body" '{body: $body}')
        api POST "/api/approvals/${approval_id}/comments" -d "$payload"
        ;;
      issues)
        api GET "/api/approvals/${3:?approval-id required}/issues"
        ;;
      *) echo "Usage: approval list|get|approve|reject|request-revision|resubmit|comment|issues"; exit 1;;
    esac
    ;;

  # ======================== COST & BUDGET ========================
  cost)
    require_company
    case "$sub" in
      summary)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/summary?${COST_QUERY}"
        ;;
      by-agent)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/by-agent?${COST_QUERY}"
        ;;
      by-agent-model)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/by-agent-model?${COST_QUERY}"
        ;;
      by-project)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/by-project?${COST_QUERY}"
        ;;
      by-provider)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/by-provider?${COST_QUERY}"
        ;;
      by-biller)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/by-biller?${COST_QUERY}"
        ;;
      finance)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/finance-summary?${COST_QUERY}"
        ;;
      finance-by-biller)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/finance-by-biller?${COST_QUERY}"
        ;;
      finance-by-kind)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/finance-by-kind?${COST_QUERY}"
        ;;
      finance-events)
        shift 2; parse_cost_opts "$@"
        api GET "/api/companies/${COMPANY_ID}/costs/finance-events?${COST_QUERY}"
        ;;
      window-spend)
        api GET "/api/companies/${COMPANY_ID}/costs/window-spend"
        ;;
      quota-windows)
        api GET "/api/companies/${COMPANY_ID}/costs/quota-windows"
        ;;
      log-cost-event)
        shift 2; parse_data_arg "$@"
        api POST "/api/companies/${COMPANY_ID}/cost-events" -d "$DATA_ARG"
        ;;
      log-finance-event)
        shift 2; parse_data_arg "$@"
        api POST "/api/companies/${COMPANY_ID}/finance-events" -d "$DATA_ARG"
        ;;
      *) echo "Usage: cost summary|by-agent|by-agent-model|by-project|by-provider|by-biller|finance|finance-by-biller|finance-by-kind|finance-events|window-spend|quota-windows|log-cost-event|log-finance-event"; exit 1;;
    esac
    ;;

  budget)
    case "$sub" in
      overview)
        require_company
        api GET "/api/companies/${COMPANY_ID}/budgets/overview"
        ;;
      update)
        require_company
        require_jq
        shift 2
        budget=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --budget-monthly-cents) budget="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg budget "$budget" \
          '(if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end)')
        api PATCH "/api/companies/${COMPANY_ID}/budgets" -d "$payload"
        ;;
      reset)
        require_company
        api POST "/api/companies/${COMPANY_ID}/budgets/reset" -d '{}'
        ;;
      soft-reset)
        require_company
        api POST "/api/companies/${COMPANY_ID}/budgets/soft-reset" -d '{}'
        ;;
      agent-update)
        require_jq
        agent_id="${3:?agent-id required}"
        shift 3
        budget=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --budget-monthly-cents) budget="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg budget "$budget" \
          '(if $budget != "" then {budgetMonthlyCents: ($budget | tonumber)} else {} end)')
        api PATCH "/api/agents/${agent_id}/budgets" -d "$payload"
        ;;
      *) echo "Usage: budget overview|update|reset|soft-reset|agent-update"; exit 1;;
    esac
    ;;

  # ======================== SECRET ========================
  secret)
    require_company
    case "$sub" in
      list)
        api GET "/api/companies/${COMPANY_ID}/secrets"
        ;;
      providers)
        api GET "/api/companies/${COMPANY_ID}/secret-providers"
        ;;
      create)
        require_jq
        shift 2
        name="" value="" provider="" description="" external_ref=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --value) value="$2"; shift 2;;
            --provider) provider="$2"; shift 2;;
            --description) description="$2"; shift 2;;
            --external-ref) external_ref="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$name" ]] && { echo "Error: --name required" >&2; exit 1; }
        [[ -z "$value" ]] && { echo "Error: --value required" >&2; exit 1; }
        payload=$(jq -n --arg name "$name" --arg value "$value" \
          --arg provider "$provider" --arg desc "$description" \
          --arg extRef "$external_ref" \
          '{name: $name, value: $value} +
           (if $provider != "" then {provider: $provider} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $extRef != "" then {externalRef: $extRef} else {} end)')
        api POST "/api/companies/${COMPANY_ID}/secrets" -d "$payload"
        ;;
      update)
        require_jq
        secret_id="${3:?secret-id required}"
        shift 3
        name="" description="" external_ref=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --name) name="$2"; shift 2;;
            --description) description="$2"; shift 2;;
            --external-ref) external_ref="$2"; shift 2;;
            *) shift;;
          esac
        done
        payload=$(jq -n --arg name "$name" --arg desc "$description" \
          --arg extRef "$external_ref" \
          '(if $name != "" then {name: $name} else {} end) +
           (if $desc != "" then {description: $desc} else {} end) +
           (if $extRef != "" then {externalRef: $extRef} else {} end)')
        api PATCH "/api/secrets/${secret_id}" -d "$payload"
        ;;
      rotate)
        require_jq
        secret_id="${3:?secret-id required}"
        shift 3
        value="" external_ref=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --value) value="$2"; shift 2;;
            --external-ref) external_ref="$2"; shift 2;;
            *) shift;;
          esac
        done
        [[ -z "$value" ]] && { echo "Error: --value required" >&2; exit 1; }
        payload=$(jq -n --arg value "$value" --arg extRef "$external_ref" \
          '{value: $value} +
           (if $extRef != "" then {externalRef: $extRef} else {} end)')
        api POST "/api/secrets/${secret_id}/rotate" -d "$payload"
        ;;
      delete)
        api DELETE "/api/secrets/${3:?secret-id required}"
        ;;
      *) echo "Usage: secret list|providers|create|update|rotate|delete"; exit 1;;
    esac
    ;;

  # ======================== DASHBOARD ========================
  dashboard)
    require_company
    api GET "/api/companies/${COMPANY_ID}/dashboard"
    ;;

  # ======================== ACTIVITY ========================
  activity)
    require_company
    shift 1
    query=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --agent-id) query+="agentId=${2}&"; shift 2;;
        --entity-type) query+="entityType=${2}&"; shift 2;;
        --entity-id) query+="entityId=${2}&"; shift 2;;
        --action) query+="action=${2}&"; shift 2;;
        *) shift;;
      esac
    done
    api GET "/api/companies/${COMPANY_ID}/activity?${query}"
    ;;

  # ======================== ORG CHART ========================
  org)
    require_company
    api GET "/api/companies/${COMPANY_ID}/org"
    ;;

  # ======================== HEALTH ========================
  health)
    api GET "/api/health"
    ;;

  # ======================== HELP ========================
  help|--help|-h)
    usage
    ;;

  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
