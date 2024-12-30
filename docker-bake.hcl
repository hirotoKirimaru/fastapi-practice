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

group "default" {
  targets = ["api", "worker"]
}

// BUILD_TARGETだけを切り替えたいがための継承
target "common" {
  target = "${BUILD_TARGET}"
  // push=true とするとbake時にアップロードもできる
  // oci-mediatypes=true だと Open Container Image 準拠になる
  // gzipではなく、zstd を使用
  // これ指定するとダメ？
  platforms = ["linux/amd64"]
  output = ["type=image,oci-mediatypes=true,compression=zstd,compression-level=3,force-compression=true"]
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