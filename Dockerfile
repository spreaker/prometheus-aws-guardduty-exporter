ARG ARCH=
FROM ${ARCH}alpine:3.18

RUN apk add --update --no-cache python3~=3.11 py3-pip && \
    pip3 install prometheus-aws-guardduty-exporter==3.0.0 --no-cache-dir

# Run as non-root
RUN adduser app -S -u 1000
USER app

ENTRYPOINT ["prometheus-aws-guardduty-exporter"]
