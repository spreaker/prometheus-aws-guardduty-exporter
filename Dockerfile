FROM alpine:3.18

RUN apk add --update --no-cache python3~=3.11 && \
    python3 -m pip install prometheus-aws-guardduty-exporter==2.0.0 --no-cache-dir

# Run as non-root
RUN adduser app -S -u 1000
USER app

ENTRYPOINT ["prometheus-aws-guardduty-exporter"]
