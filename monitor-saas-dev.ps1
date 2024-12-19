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
#Set-PersistentEnvVariable "ACCOUNT_TOASTER" "0fea8f1b-0f0f-4998-938a-37a62db59481"

# Check if TOKEN is already set
if (-not $env:TOKEN) {
    $TOKEN = (& python oidc_pkce.py -u $env:BASE_URL).Trim()
    Set-PersistentEnvVariable "TOKEN" $TOKEN
    Write-Output "TOKEN set to: $env:TOKEN"
} else {
    Write-Output "TOKEN already set: $env:TOKEN"
}

& python examples/generic_api/project_setup.py `
    --urls $env:BASE_URL `
    --token $env:TOKEN `
    --accounts $env:ACCOUNT_BURST `
    --verbose=true

& python examples/generic_api/project_setup.py `
    --urls $env:BASE_URL `
    --token $env:TOKEN `
    --accounts $env:ACCOUNT_BURST `
    --verbose=true `
    --monitor True `
    --remove=old

# --limited_monitor True

# --remove=old
# --filter=linear 
# --signing_key="D:/ansysDev/signing.key"
# --project "New New Tests"

Read-Host "Press Enter to continue..."
