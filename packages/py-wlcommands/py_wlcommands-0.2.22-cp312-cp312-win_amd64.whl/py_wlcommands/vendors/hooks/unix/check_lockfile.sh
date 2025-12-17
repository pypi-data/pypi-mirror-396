#!/bin/sh

# Check uv.lock consistency and update if needed

# Check if pyproject.toml exists
if [ ! -f pyproject.toml ]; then
    echo "No pyproject.toml found, skipping uv.lock check"
    exit 0
fi

# Generate new lockfile
if uv pip compile pyproject.toml --quiet --output-file=uv.lock.new; then
    # Check if uv.lock.new was actually created
    if [ -f uv.lock.new ]; then
        if [ -f uv.lock ]; then
            if ! diff -q uv.lock.new uv.lock > /dev/null; then
                echo "Updated uv.lock file"
                mv uv.lock.new uv.lock
            else
                echo "uv.lock file is already consistent"
                rm uv.lock.new
            fi
        else
            echo "Created uv.lock file"
            mv uv.lock.new uv.lock
        fi
    else
        echo "Error: uv.lock.new was not created by uv pip compile"
        exit 1
    fi
else
    echo "Error: uv pip compile failed" >&2
    rm -f uv.lock.new
    exit 1
fi
