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

# Remove symlinked service and timer files from the systemd user directory
remove-user-systemd:
    rm -f ~/.config/systemd/user/basedcount_bot_backup.service
    rm -f ~/.config/systemd/user/basedcount_bot_backup.timer
    rm -f ~/.config/systemd/user/basedcount_bot.service
    systemctl --user daemon-reload
    ls -alF ~/.config/systemd/user

# Check the status of the main service and backup timer
status:
    systemctl --user status basedcount_bot.service basedcount_bot_backup.timer

# Reload daemon, enable the main service and backup timer, and start them
start-all-services:
    systemctl --user daemon-reload
    systemctl --user enable --now basedcount_bot.service
    systemctl --user enable --now basedcount_bot_backup.timer

# Stop the main service and backup timer
stop-all-services:
    systemctl --user stop basedcount_bot.service
    systemctl --user stop basedcount_bot_backup.timer

# Restart the main service and backup timer
restart-all-services:
    systemctl --user restart basedcount_bot.service
    systemctl --user restart basedcount_bot_backup.timer

# Stop and disable the main service and backup timer from starting on boot
disable-all-services:
    systemctl --user disable --now basedcount_bot.service
    systemctl --user disable --now basedcount_bot_backup.timer
