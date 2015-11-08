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

  local ret="$(python ${py_path} -t \
    | $(__fzfcmd) \
    --exact \
    --header='Tip: press ctrl-e to edit this menu' \
    --expect=ctrl-e \
    )"

  if [[ "$ret" =~ '^ctrl-e'  ]]; then
    env MDX_CHAMELEON_MODE=mini nvim ~/.fzf-cmdhub-menu
    ch
  elif [[ "$ret" == '' ]]; then
    return
  else
    local cmd="$(python ${py_path} -c ${ret#*$'\n'})"
    if [ -n "$cmd" ]; then
      printf "\e[35mexecuting: \e[34m$cmd\e[0m\n"
      $cmd
    else
      printf "\e[31mfechted an empty content\e[0m\n"
    fi
  fi
}
