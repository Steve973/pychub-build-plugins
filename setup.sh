#!/bin/bash
set -e

print_status() {
  local msg="$1"
  local status="$2"
  local color_reset
  local color_blue
  local color_green
  local color_red
  local color_yellow

  if tty -s; then
    color_reset="$(tput sgr0)"
    color_blue="$(tput setaf 4)"
    color_green="$(tput setaf 2)"
    color_red="$(tput setaf 1)"
    color_yellow="$(tput setaf 3)"

    printf "%-50s" "$msg"

    case "$status" in
      fail) printf "[ %sFAIL%s ]\n" "${color_red}" "${color_reset}" ;;
      info) printf "[ %sINFO%s ]\n" "${color_blue}" "${color_reset}" ;;
      ok)   printf "[ %sOK%s   ]\n" "${color_green}" "${color_reset}" ;;
      warn) printf "[ %sWARN%s ]\n" "${color_yellow}" "${color_reset}" ;;
      *)    printf "[ %s....%s ]\n" "${color_yellow}" "${color_reset}" ;;
    esac
  else
    printf "[ %s ] %s\n" "$status" "$msg"
  fi
}

print_status "Setting up pychubby-dev environment..." info

# Step 1: Create .venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv && print_status "Created virtual environment" ok
else
  print_status ".venv already exists" warn
fi

# Step 2: Activate it
# shellcheck disable=SC1091
source .venv/bin/activate && print_status "Activated virtual environment" ok

# Step 3: Ensure pip is upgraded before using it
python3 -m pip install --upgrade pip poetry build pytest pychub >/dev/null 2>&1 && print_status "Upgraded pip and poetry" ok

# Step 4: Add monoranger plugin (skip if already installed)
if ! poetry self show plugins | grep -q "poetry-monoranger-plugin"; then
  if poetry self add poetry-monoranger-plugin >/dev/null 2>&1; then
    print_status "Enabled poetry-monoranger-plugin" ok
  else
    print_status "Could not enable poetry-monoranger-plugin" fail
    exit 1
  fi
else
  print_status "poetry-monoranger-plugin already enabled" warn
fi

# Step 5: Install workspace dependencies
if poetry install; then
  print_status "Installed all project dependencies" ok
else
  print_status "poetry install failed" fail
  exit 1
fi

print_status "Project setup complete. You can now open your IDE." ok