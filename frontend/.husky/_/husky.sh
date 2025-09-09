#!/bin/sh

# Установи правильный путь к node_modules
cd "$(dirname "$0")/../../"

# Запусти husky
exec node_modules/.bin/husky