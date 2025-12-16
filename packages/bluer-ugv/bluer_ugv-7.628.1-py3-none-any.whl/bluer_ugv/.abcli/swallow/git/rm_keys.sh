#! /usr/bin/git bash

function bluer_ugv_swallow_git_rm_keys() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 1)

    if [[ "$abcli_is_rpi" == false ]]; then
        bluer_ai_log_error "only works on rpi."
        return 1
    fi

    sudo rm -v ~/.ssh/$BLUER_AI_GIT_SSH_KEY_NAME

    sudo rm -v ~/.ssh/$BLUER_AI_GIT_SSH_KEY_NAME.pub

    local repo_name
    for repo_name in bluer-ai $(bluer_ai_plugins list_of_external \
        --delim space \
        --log 0 \
        --repo_names 1); do
        bluer_ai_git \
            $repo_name \
            set_remote \
            dryrun=$do_dryrun,https
        [[ $? -ne 0 ]] && return 1
    done
}
