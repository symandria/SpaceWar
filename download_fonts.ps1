# Create fonts directory if it doesn't exist
$fontsDir = "Content/raw_fonts"
if (-not (Test-Path $fontsDir)) {
    New-Item -ItemType Directory -Path $fontsDir | Out-Null
}

# Download Orbitron Bold
$orbitronUrl = "https://github.com/theleagueof/orbitron/raw/master/Orbitron%20Bold.ttf"
$orbitronPath = "$fontsDir/Orbitron-Bold.ttf"
if (-not (Test-Path $orbitronPath)) {
    Write-Host "Downloading Orbitron Bold..."
    Invoke-WebRequest -Uri $orbitronUrl -OutFile $orbitronPath
}

# Download Roboto Regular
$robotoUrl = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
$robotoPath = "$fontsDir/Roboto-Regular.ttf"
if (-not (Test-Path $robotoPath)) {
    Write-Host "Downloading Roboto Regular..."
    Invoke-WebRequest -Uri $robotoUrl -OutFile $robotoPath
}

Write-Host "Fonts downloaded successfully!" 