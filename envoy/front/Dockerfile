FROM envoyproxy/envoy:latest

RUN apt-get update && apt-get -q install -y \
    curl

ADD ./front-envoy.yaml /etc/

EXPOSE 80 8001

CMD /usr/local/bin/envoy -c /etc/front-envoy.yaml --service-cluster front-proxy