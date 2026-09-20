# Justfile for managing basedcount_bot systemd user services

# Interactively choose a recipe to run (default when running 'just' with no args).
default:
    @just --choose

# List all available recipes.
ls:
    @just --list

# Format this Justfile itself.
just-fmt:
    just --fmt --unstable

# Create user systemd directory and symlink service and timer files
symlink-to-user-systemd:
    mkdir -p ~/.config/systemd/user
    ln -sfr systemd_services/basedcount_bot_backup.service ~/.config/systemd/user
    ln -sfr systemd_services/basedcount_bot_backup.timer ~/.config/systemd/user
    ln -sfr systemd_services/basedcount_bot.service ~/.config/systemd/user
    systemctl --user daemon-reload
    ls -alF ~/.config/systemd/user

# Reload daemon, enable, and start all services and timers
start-all-services:
    systemctl --user daemon-reload
    systemctl --user enable --now basedcount_bot.service
    systemctl --user enable --now basedcount_bot_backup.timer
    systemctl --user enable --now basedcount_bot_backup.service
    systemctl --user status basedcount_bot.service basedcount_bot_backup.timer

# Stop all running services and timers
stop-all-services:
    systemctl --user stop basedcount_bot.service
    systemctl --user stop basedcount_bot_backup.timer
    systemctl --user stop basedcount_bot_backup.service

# Stop and disable all services and timers from starting on boot
disable-all-services:
    systemctl --user disable --now basedcount_bot.service
    systemctl --user disable --now basedcount_bot_backup.timer
    systemctl --user disable --now basedcount_bot_backup.service
