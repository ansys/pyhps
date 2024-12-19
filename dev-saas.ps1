param(
    [int]$NumJobs = 1
)

# Function to persist environment variables across sessions
function Set-PersistentEnvVariable {
    param (
        [string]$name,
        [string]$value
    )
    [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::User)
    Set-Item -Path "Env:$name" -Value $value  # Update the current session
}

# Set and persist BASE URLs and ACCOUNT variables
#Set-PersistentEnvVariable "BASE_PROD_URL" "https://hps.ansys.com/hps"
Set-PersistentEnvVariable "BASE_URL" "https://dev-jms.awsansys11np.onscale.com/hps"
Set-PersistentEnvVariable "ACCOUNT_BURST" "30b226d7-aa1b-4001-b763-f88525abde4d"
Set-PersistentEnvVariable "ACCOUNT_BURST_2" "72670e8c-43fe-4ec3-bcf8-20be821d91c1"
Set-PersistentEnvVariable "ACCOUNT_TOASTER" "0fea8f1b-0f0f-4998-938a-37a62db59481"
Set-PersistentEnvVariable "ACCOUNT_PROD" "e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f"

 Write-Output "HPS URL: $env:BASE_URL"

# Check if TOKEN is already set
if (-not $env:TOKEN) {
    $TOKEN = (& python oidc_pkce.py -u $env:BASE_URL).Trim()
    Set-PersistentEnvVariable "TOKEN" $TOKEN
    Write-Output "TOKEN set to: $env:TOKEN"
} else {
    Write-Output "TOKEN already set: $env:TOKEN"
}

# Example of running a Python script using the persistent environment variables
# & python examples/mapdl_tyre_performance/project_setup.py `
& python examples/mapdl_motorbike_frame/project_setup.py `
    --name "Burst Account tests jon" `
    -v "2025 R1" `
    --use-exec-script True `
    --url $env:BASE_URL `
    --num-jobs=$NumJobs `
    --account $env:ACCOUNT_BURST `
    --token $env:TOKEN `
    --queue "fluids-64core-256gb" `
    --crsid "02yZVjGPt7oxL4HH2uQdNG"

# Pause equivalent in PowerShell
Read-Host "Press Enter to continue..."
