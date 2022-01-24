$builders = docker buildx ls | Select-String raspberry
if(-not $builders) {
  docker buildx create --name raspberry
}

docker buildx use raspberry
docker buildx inspect raspberry --bootstrap

Write-Host "Login to the container repository"
$accessToken = (az acr login --name humanprinter --expose-token | ConvertFrom-Json).accessToken
docker login humanprinter.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p $accessToken

Write-Host "Building and pushing the image"
$tag = Get-Date -Format "yyyyMMdd"
docker buildx build --platform linux/arm64,linux/arm/v7,linux/arm/v6 -t humanprinter.azurecr.io/dsmr-to-mqtt:$tag -t humanprinter.azurecr.io/dsmr-to-mqtt:latest --push .
