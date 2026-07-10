param(
    [switch]$Integration
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

.\.venv\Scripts\pytest.exe --cov=app --cov-report=term-missing

if ($Integration) {
    $env:RUN_INTEGRATION_TESTS = "true"
    try {
        .\.venv\Scripts\pytest.exe tests\test_web_search_integration.py -q
    }
    finally {
        Remove-Item Env:\RUN_INTEGRATION_TESTS -ErrorAction SilentlyContinue
    }
}
