FZF_CMDHUB_SH_PATH="$(dirname $0)"

__fzfcmd() {
  [ ${FZF_TMUX:-1} -eq 1 ] && echo "fzf-tmux -d${FZF_TMUX_HEIGHT:-40%}" \
    || echo "fzf"
}

ch() {
  # check if the `fzf` is installed
  if ! which fzf &>/dev/null; then
    printf "\e[31m* need [fzf], please install it first *\e[0m\n"
    return
  fi

  local py_path="${FZF_CMDHUB_SH_PATH}/fzf-cmdhub.py"

  local selected_title="$(python ${py_path} -t \
    | fzf -e --bind='ctrl-e:execute(env MDX_CHAMELEON_MODE=mini nvim ~/.fzf-cmdhub-menu)')"

  if [ -n "$selected_title" ]; then
    local cmd="$(python ${py_path} -c ${selected_title})"
    if [ -n "$cmd" ]; then
      eval "$cmd"
    else
      echo "* fetched an empty content *"
    fi
  fi
}
