# Get the path to MGCB
$mgcbPath = "mgcb"

# Check if MGCB is installed
if (-not (Get-Command $mgcbPath -ErrorAction SilentlyContinue)) {
    Write-Host "Installing MGCB..."
    dotnet tool install -g dotnet-mgcb
}

# Build the content
Write-Host "Building content..."
mgcb /rebuild /outputDir:"bin/Windows/net6.0/Content" "Content/Content.mgcb" 