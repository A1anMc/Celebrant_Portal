#!/bin/bash

# Function to check if an application is installed
check_app() {
    if [ -d "/Applications/$1.app" ]; then
        return 0
    else
        return 1
    fi
}

# List of files to open
FILES=(
    "README.md"
    "SHARING.md"
    "docs/01-project-foundation.md"
    "docs/02-audience-market.md"
    "docs/03-strategic-planning.md"
    "docs/04-visualizations.md"
)

# Check for installed Markdown editors
if check_app "Visual Studio Code"; then
    echo "Opening files in Visual Studio Code..."
    open -a "Visual Studio Code" "${FILES[@]}"
elif check_app "Typora"; then
    echo "Opening files in Typora..."
    open -a "Typora" "${FILES[@]}"
elif check_app "Obsidian"; then
    echo "Opening files in Obsidian..."
    open -a "Obsidian" "${FILES[@]}"
else
    # If no specific Markdown editor is found, use the default text editor
    echo "Opening files in default text editor..."
    open "${FILES[@]}"
fi

echo "All documentation files have been opened!" 