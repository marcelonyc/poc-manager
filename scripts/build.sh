#!/usr/bin/env bash
set -euo pipefail

source ~/.secrets

usage() {
  cat <<EOF
Usage: $0 <version> [--registry <registry>] [--push]

Build and optionally push all poc-manager Docker images.

Arguments:
  <version>       Semver tag for the images (e.g. 1.0.0)

Options:
  --registry <r>  Docker registry prefix (e.g. ghcr.io/marcelonyc/)
                  Must include trailing slash.
  --push          Push images to the registry after building.
  -h, --help      Show this help message.

Examples:
  $0 1.2.0
  $0 1.2.0 --registry ghcr.io/marcelonyc/ --push
EOF
  exit 1
}

# ── Parse arguments ──
VERSION=""
REGISTRY=""
PUSH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry) REGISTRY="$2"; shift 2 ;;
    --push)     PUSH=true; shift ;;
    -h|--help)  usage ;;
    *)
      if [[ -z "$VERSION" ]]; then
        VERSION="$1"; shift
      else
        echo "Error: unexpected argument '$1'" >&2; usage
      fi
      ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  echo "Error: version is required" >&2
  usage
fi

# Validate semver format (major.minor.patch with optional pre-release)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
  echo "Error: '$VERSION' is not a valid semver (expected X.Y.Z)" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Private registry settings (from environment) ──
NPMRC_PATH="${NPMRC_PATH:-$HOME/.npmrc}"

IMAGES=(
  "poc-manager-backend:backend"
  "poc-manager-frontend:frontend"
  "poc-manager-nginx:nginx"
)

echo "==> Building images with version ${VERSION}"
[[ -n "$REGISTRY" ]] && echo "    Registry: ${REGISTRY}"

for entry in "${IMAGES[@]}"; do
  IMAGE_NAME="${entry%%:*}"
  BUILD_DIR="${entry##*:}"
  FULL_TAG="${REGISTRY}${IMAGE_NAME}:${VERSION}"
  LATEST_TAG="${REGISTRY}${IMAGE_NAME}:latest"

  BUILD_ARGS=(
    --build-arg "VERSION=${VERSION}"
    -t "${FULL_TAG}"
    -t "${LATEST_TAG}"
    -f "${PROJECT_ROOT}/${BUILD_DIR}/Dockerfile"
  )

  # Pass pip private registry args for backend builds
  if [[ "$BUILD_DIR" == "backend" ]]; then
    [[ -n "${PIP_INDEX_URL:-}" ]]    && BUILD_ARGS+=(--build-arg "PIP_INDEX_URL=${PIP_INDEX_URL}")
    [[ -n "${PIP_TRUSTED_HOST:-}" ]] && BUILD_ARGS+=(--build-arg "PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}")
  fi

  # Mount npmrc secret for frontend builds
  if [[ "$BUILD_DIR" == "frontend" && -f "$NPMRC_PATH" ]]; then
    BUILD_ARGS+=(--secret "id=npmrc,src=${NPMRC_PATH}")
  fi

  echo ""
  echo "--- Building ${FULL_TAG} from ${BUILD_DIR}/ ---"
  docker build "${BUILD_ARGS[@]}" "${PROJECT_ROOT}/${BUILD_DIR}"
done

echo ""
echo "==> All images built successfully:"
for entry in "${IMAGES[@]}"; do
  IMAGE_NAME="${entry%%:*}"
  echo "    ${REGISTRY}${IMAGE_NAME}:${VERSION}"
  echo "    ${REGISTRY}${IMAGE_NAME}:latest"
done



if [[ "$PUSH" == true ]]; then
  echo ""
  echo "==> Logging in to registry ${REGISTRY:-Docker Hub}..."
  echo "${GH_TOKEN}" | docker login ghcr.io -u ${GH_USER} --password-stdin
  if [ $? -ne 0 ]; then
    echo "Error: GHCR login failed" >&2
    exit 1
  fi
  echo ""
  echo "==> Pushing images to registry..."
  for entry in "${IMAGES[@]}"; do
    IMAGE_NAME="${entry%%:*}"
    FULL_TAG="${REGISTRY}${IMAGE_NAME}:${VERSION}"
    LATEST_TAG="${REGISTRY}${IMAGE_NAME}:latest"
    echo "    Pushing ${FULL_TAG}"
    docker push "${FULL_TAG}"
    echo "    Pushing ${LATEST_TAG}"
    docker push "${LATEST_TAG}"
  done
  echo ""
  echo "==> All images pushed successfully."
fi
