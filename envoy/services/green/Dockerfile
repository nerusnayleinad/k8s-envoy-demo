FROM envoyproxy/envoy-alpine:latest

RUN apk update && apk add python3 bash
RUN python3 --version && pip3 --version
RUN pip3 install -q Flask==0.11.1 requests==2.18.4
RUN mkdir /code
ADD ./service-envoy.yaml /etc/service-envoy.yaml
ADD ./service.py /code
ADD ./start_service.sh /usr/local/bin/start_service.sh
RUN chmod u+x /usr/local/bin/start_service.sh
ENV SERVICE_NAME green
ENTRYPOINT /usr/local/bin/start_service.sh