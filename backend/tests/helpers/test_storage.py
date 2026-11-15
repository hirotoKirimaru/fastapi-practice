# def create_minio_container():
#     minio = MinioContainer(access_key="minio", secret_key="minio1234")
# minio.with_command(
#     "mkdir -p /data/data-exchange.local /data/tmp.local && /usr/bin/minio server --address :9000 --console-address :9001 /data")
# minio.with_exposed_ports(9000)
# minio.start()
# try:
#     yield minio
# finally:
#     minio.stop()
