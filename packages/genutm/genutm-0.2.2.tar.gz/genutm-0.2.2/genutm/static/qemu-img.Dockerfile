FROM alpine:3.23.0 AS qemu-img

RUN apk add --no-cache qemu-img

ENTRYPOINT ["/usr/bin/qemu-img"]
