#!/bin/bash

if [[ -n "$ANTHROPIC_API_KEY" ]] && git diff --cached --quiet --exit-code 2>/dev/null; then
  echo "No staged changes to commit"
  exit 1
elif [[ -n "$ANTHROPIC_API_KEY" ]]; then
  msg=$(git diff --cached | curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n --arg diff "$(cat)" '{
      model: "claude-sonnet-4-20250514",
      max_tokens: 256,
      messages: [{role: "user", content: "Write a concise git commit message for this diff. Just the message, no quotes, no explanation:\n\n\($diff)"}]
    }')" | jq -r '.content[0].text')
  
  echo "Commit message: $msg"
  read -p "Use this message? [Y/n/e(dit)] " choice
  case "$choice" in
    n|N) git commit ;;
    e|E) git commit -m "$msg" --edit ;;
    *) git commit -m "$msg" ;;
  esac
else
  git commit "$@"
fi
