@echo off

REM Check uv.lock consistency and update if needed

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo No pyproject.toml found, skipping uv.lock check
    exit /b 0
)

REM Generate new lockfile
uv pip compile pyproject.toml --quiet --output-file=uv.lock.new

REM Check if uv pip compile succeeded
if errorlevel 1 (
    echo Error: uv pip compile failed
    if exist "uv.lock.new" del "uv.lock.new"
    exit /b 1
)

REM Check if uv.lock.new was actually created
if exist "uv.lock.new" (
    if exist "uv.lock" (
        REM Compare files
        fc /b "uv.lock.new" "uv.lock" > nul
        if errorlevel 1 (
            echo Updated uv.lock file
            move /y "uv.lock.new" "uv.lock" > nul
        ) else (
            echo uv.lock file is already consistent
            del "uv.lock.new"
        )
    ) else (
        echo Created uv.lock file
        move /y "uv.lock.new" "uv.lock" > nul
    )
) else (
    echo Error: uv.lock.new was not created by uv pip compile
    exit /b 1
)
