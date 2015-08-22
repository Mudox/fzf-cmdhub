#!/bin/bash

ch() {
  if [ -z "$(which fzf)" ]; then
    printf "\e[31m* need [fzf], please install it first *\e[0m\n"
    return
  fi

  local selected_title=$(fzf-cmdhub-py -t | fzf)
  if [ -n "$selected_title" ]; then
    local cmd=$(fzf-cmdhub-py -c "${selected_title}")
    if [ -n "$cmd" ]; then
      eval "$cmd"
    fi
  fi
}

FZF_CMDHUB_SH_PATH=$0

ct() {
  echo "$FZF_CMDHUB_SH_PATH"
}
