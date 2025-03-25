# Get the path to MGCB
$mgcbPath = "mgcb"

# Check if MGCB is installed
if (-not (Get-Command $mgcbPath -ErrorAction SilentlyContinue)) {
    Write-Host "Installing MGCB..."
    dotnet tool install -g dotnet-mgcb
}

# Function to get the appropriate content processor for a file type
function Get-ContentProcessor($extension) {
    switch ($extension.ToLower()) {
        ".png" { 
            return @{
                importer = "TextureImporter"
                processor = "TextureProcessor"
                params = @{
                    "ColorKeyColor" = "255,0,255,255"
                    "ColorKeyEnabled" = "True"
                    "GenerateMipmaps" = "False"
                    "PremultiplyAlpha" = "True"
                    "ResizeToPowerOfTwo" = "False"
                    "MakeSquare" = "False"
                    "TextureFormat" = "Color"
                }
            }
        }
        ".spritefont" {
            return @{
                importer = "FontDescriptionImporter"
                processor = "FontDescriptionProcessor"
                params = @{
                    "PremultiplyAlpha" = "True"
                    "TextureFormat" = "Compressed"
                }
            }
        }
        ".ttf" {
            return @{
                copy = $true
            }
        }
        default {
            return $null
        }
    }
}

# Create the base MGCB content
$mgcbContent = @"
#----------------------------- Global Properties ----------------------------#

/outputDir:bin/$(Platform)
/intermediateDir:obj/$(Platform)
/platform:Windows
/config:
/profile:Reach
/compress:False

#-------------------------------- References --------------------------------#

#---------------------------------- Content ---------------------------------#

"@

# Get all content files recursively
$contentFiles = Get-ChildItem -Path "Content" -Recurse -File | Where-Object { 
    $_.Extension -in ".png", ".spritefont", ".ttf"
}

# Process each file
foreach ($file in $contentFiles) {
    $relativePath = $file.FullName.Replace($PWD.Path + "\Content\", "").Replace("\", "/")
    $processor = Get-ContentProcessor $file.Extension

    if ($processor) {
        $mgcbContent += "`n#begin $relativePath`n"
        
        if ($processor.copy) {
            $mgcbContent += "/copy:$relativePath`n"
        }
        else {
            $mgcbContent += "/importer:$($processor.importer)`n"
            $mgcbContent += "/processor:$($processor.processor)`n"
            foreach ($param in $processor.params.GetEnumerator()) {
                $mgcbContent += "/processorParam:$($param.Key)=$($param.Value)`n"
            }
            $mgcbContent += "/build:$relativePath`n"
        }
    }
}

# Write the MGCB file
$mgcbContent | Out-File -FilePath "Content/Content.mgcb" -Encoding UTF8

# Build the content
Write-Host "Building content..."
mgcb /rebuild /outputDir:"SpaceWar.Core/bin/Debug/net8.0/Content" "Content/Content.mgcb"

# Copy content to the build directory
Write-Host "Copying content to build directory..."
$contentDir = "SpaceWar.Core/bin/Debug/net8.0/Content"
if (-not (Test-Path $contentDir)) {
    New-Item -ItemType Directory -Force -Path $contentDir
}
Copy-Item -Path "Content/*" -Destination $contentDir -Recurse -Force 