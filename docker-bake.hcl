variable "BUILD_TARGET" {
  default = "development"
}

variable "ENV" {}
variable "S3_BUCKET" {}
variable "AWS_S3_ACCESS_KEY" {
  default = "minio"
}

variable "AWS_S3_SECRET_KEY" {
  default = "minio1234"
}

group "default" {
  targets = ["api"]
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
  context = "."
  target = "${BUILD_TARGET}"
  tags = ["api:latest"]
  args = merge(common_args, {
    SERVICE_NAME = "api"
  })
}

target "worker" {
  context = "."
  target = "${BUILD_TARGET}"
  tags = ["api:latest"]
  args = merge(common_args, {
    SERVICE_NAME = "worker"
  })
}