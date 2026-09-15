$ErrorActionPreference = 'Stop'

Write-Host "Setting up QNX SDP 8.0 Environment..."
# Define path to QNX environment script
$QnxEnvScript = "C:\Users\dhars\qnx800\qnxsdp-env.bat"

if (!(Test-Path $QnxEnvScript)) {
    Write-Error "QNX SDP environment script not found at $QnxEnvScript. Please ensure QNX SDP 8.0 is installed."
    exit 1
}

# In PowerShell, running a batch script that sets environment variables doesn't persist to the PS session.
# We need to extract them or run the build command *inside* cmd.exe with the script.

Write-Host "Initiating QNX aarch64 build for RAVEN..."

$BuildCommand = @"
call "$QnxEnvScript"
cd /d "$PSScriptRoot\..\qnx"
make clean
make
"@

# Execute via cmd.exe
cmd.exe /c $BuildCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "QNX Build completed successfully! (AArch64 / ARMv8)" -ForegroundColor Green
    Write-Host "Binary is located at qnx/bin/sensor_bridge"
} else {
    Write-Host "QNX Build failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
