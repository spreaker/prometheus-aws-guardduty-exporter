FROM alpine:3.9

RUN apk add --update --no-cache python3~=3.6 && \
    python3 -m pip install prometheus-aws-guardduty-exporter==1.1.2 --no-cache-dir

# Run as non-root
RUN adduser app -S -u 1000
USER app

ENTRYPOINT ["prometheus-aws-guardduty-exporter"]
