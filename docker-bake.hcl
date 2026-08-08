variable "BUILD_TARGET" {
  default = "dev"
}

variable "ENV" {}
variable "S3_BUCKET" {}
variable "AWS_S3_ACCESS_KEY" {
  default = "minio"
}

variable "AWS_S3_SECRET_KEY" {
  default = "minio1234"
}

variable "TAG" {
  default = "latest"
}

// ローカルの `docker buildx bake` はホストのアーキテクチャ向けだけを作る。
// multi-arch (linux/amd64,linux/arm64) が欲しいときは
//   PLATFORMS=linux/amd64,linux/arm64 docker buildx bake --push
// のように上書きする。CI の multi-arch ビルドは .github/workflows/ci.yml 側で
// アーキテクチャごとのネイティブ runner を使って行う
variable "PLATFORMS" {
  default = ""
}

group "default" {
  targets = ["api", "worker"]
}

// BUILD_TARGETだけを切り替えたいがための継承
target "common" {
  target = "${BUILD_TARGET}"

  // PLATFORMS が空ならホストのアーキテクチャ(= buildx のデフォルト)だけを作る
  platforms = PLATFORMS == "" ? null : split(",", PLATFORMS)

  // oci-mediatypes=true で Open Container Image 準拠、圧縮は gzip ではなく zstd。
  //
  // 出力先は platforms の指定有無で変える必要がある:
  //   - 単一アーキテクチャ: type=docker でローカルの docker イメージとして読み込む
  //   - multi-arch: manifest list はローカルに load できないので registry へ push する
  // 以前は "type=docker,...,force-compression=true, push=true" と
  // 両方を1つの output に書いていたが、type=docker に push=true は効かず
  // (かつ値の前に空白が入っていて) 実際には push されていなかった
  output = PLATFORMS == "" ? [
    "type=docker,oci-mediatypes=true,compression=zstd,compression-level=3,force-compression=true"
  ] : [
    "type=image,oci-mediatypes=true,compression=zstd,compression-level=3,force-compression=true,push=true"
  ]
}

variable "common_args" {
  default = {
    ENV = "${ENV}"
    S3_BUCKET = "${S3_BUCKET}"
    AWS_S3_ACCESS_KEY = "${AWS_S3_ACCESS_KEY}"
    AWS_S3_SECRET_KEY = "${AWS_S3_SECRET_KEY}"
  }
}

target "api" {
  inherits = ["common"]
  context = "."
  tags = [
    "api:latest",
//     "kirimaru/fastapi-practice_prod-runtime:latest"
//     "kirimaru/fastapi-practice_prod-runtime:${TAG}"
  ]
  args = merge(common_args, {
    SERVICE_NAME = "api"
  })
}

target "worker" {
  inherits = ["common"]

  context = "."
  tags = ["worker:latest"]
  args = merge(common_args, {
    SERVICE_NAME = "worker"
  })
}