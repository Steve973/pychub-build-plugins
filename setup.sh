#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

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

maybe_delete_venv() {
  if [ -d "${SCRIPT_DIR}/.venv" ]; then
    rm -rf "${SCRIPT_DIR}/.venv" && print_status "Removing and re-creating project .venv" ok
  fi
}

clean_pycache() {
  local find_args
  find_args=(
    "${SCRIPT_DIR}"
    -ignore_readdir_race
    -type d
    -name "__pycache__"
    -exec rm -rf {} +
  )
  find "${find_args[@]}" && print_status "Removed pycache dirs" ok
}

clean_lock_files() {
  local find_args
  find_args=(
    "${SCRIPT_DIR}"
    -ignore_readdir_race
    -type f
    -name "poetry.lock"
    -exec rm -f {} +
  )
  find "${find_args[@]}" && print_status "Removed poetry lock files" ok
}

init_venv() {
  poetry config virtualenvs.in-project true --local
  poetry install --no-root --with dev
  source "${SCRIPT_DIR}/.venv/bin/activate" && print_status "Activated virtual environment" ok
}

install_monoranger_plugin() {
  if poetry self add poetry-monoranger-plugin >/dev/null 2>&1; then
    print_status "Enabled poetry-monoranger-plugin" ok
  else
    print_status "Could not enable poetry-monoranger-plugin" fail
    exit 1
  fi
}

install_project() {
  if poetry install --no-root --with dev; then
    print_status "Installed all project dependencies" ok
  else
    print_status "poetry install failed" fail
    exit 1
  fi
}

print_status "Setting up the development environment..." info

maybe_delete_venv
clean_pycache
clean_lock_files
init_venv
install_monoranger_plugin
install_project

print_status "Project setup complete. You can now open your IDE." ok