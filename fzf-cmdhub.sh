#!/usr/bin/env bash

FZF_CMDHUB_SH_PATH=$(dirname "$0")

ch() {
  # check if the `fzf` is installed
  if ! which fzf &>/dev/null; then
    printf "\e[31m* need [fzf], please install it first *\e[0m\n"
    return
  fi

  local py_path
  py_path="${FZF_CMDHUB_SH_PATH}/fzf-cmdhub.py"

  # TODO!: refactor the ctrl-e behavior to edit the selected item whatever it is.
  local ret
  ret=$(python "${py_path}" -t                                                             \
    | fzf                                                                                  \
    --height=30% --min-height=20                                                           \
    --border --margin=1                                                                    \
    --header='Tip: ctrl-e to edit the file behind current item; ctrl-t to create new item' \
    --expect=ctrl-e,ctrl-t                                                                 \
    )

  local info where selected_line

  if [[ "$ret" =~ '^ctrl-e'  ]]; then
    selected_line=$(echo "$ret" | sed -n '2p')
    info=$(python "${py_path}" -i "$selected_line")
    where=$(echo "$info" | sed -n '2p')

    if [[ "$where" = '<menu>' ]]; then
      eval "${FZF_CMDHUB_EDITOR:-vim} ~/.fzf-cmdhub-menu"
    else
      eval "${FZF_CMDHUB_EDITOR:-vim} \"$where\""
    fi
    ch
  elif [[ "$ret" =~ '^ctrl-t' ]]; then
    selected_line=$(echo "$ret" | sed -n '2p')
    info=$(python "${py_path}" -i "$selected_line")
    where=$(echo "$info" | sed -n '2p')

    eval "${FZF_CMDHUB_EDITOR:-vim}                \
      -c 'cd ~/.fzf-cmdhub-jobs/'                  \
      -c 'let fname = input(\"new file name: \") ' \
      -c 'exe \"e \" . fnameescape(fname)'           \
      -c 'unlet fname'"
    ch
  elif [[ "$ret" == '' ]]; then
    # user canceled
    return
  else
    info=$(python "${py_path}" -i "${ret#*$'\n'}")
    cmd=$(echo "$info" | sed -n '1p')
    where=$(echo "$info" | sed -n '2p')
    if [[ -n "$info" ]]; then
      printf "\e[35mexecuting: \e[34m%s\e[0m\n" "$cmd"
      eval "$cmd"
    else
      printf "\e[31mfechted an empty content\e[0m\n"
    fi
  fi
}
