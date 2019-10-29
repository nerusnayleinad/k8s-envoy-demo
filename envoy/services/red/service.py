from flask import Flask
from flask import request
import socket
import os
import sys
import requests
import argparse

from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer

app = Flask(__name__)

TRACE_HEADERS_TO_PROPAGATE = [
    'X-Ot-Span-Context',
    'X-Request-Id',

    # Zipkin headers
    'X-B3-TraceId',
    'X-B3-SpanId',
    'X-B3-ParentSpanId',
    'X-B3-Sampled',
    'X-B3-Flags',

    # Jaeger header (for native client)
    "uber-trace-id"
]

def initialize_tracer(project_id):
    exporter = stackdriver_exporter.StackdriverExporter(
        project_id=project_id
    )
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    )

    return tracer

def render_page():
    return ('<body bgcolor="{}"><span style="color:white;font-size:4em;">\n'
            'Hello from {} (hostname: {} resolvedhostname:{})\n</span></body>\n'.format(
                    os.environ['SERVICE_NAME'],
                    os.environ['SERVICE_NAME'],
                    socket.gethostname(),
                    socket.gethostbyname(socket.gethostname())))

@app.route('/service/<service_color>')
def service(service_color):
    tracer = app.config['TRACER']
    tracer.start_span(name='service')
    result = render_page()
    tracer.end_span()
    return result

@app.route('/trace/<service_color>')
def trace(service_color):
    tracer = app.config['TRACER']
    tracer.start_span(name='trace')
    headers = {}
    ## For Propagation test ##
    # Call service 'green' from service 'blue'
    if (os.environ['SERVICE_NAME']) == 'blue':
        for header in TRACE_HEADERS_TO_PROPAGATE:
            if header in request.headers:
                headers[header] = request.headers[header]
        ret = requests.get("http://localhost:9000/trace/green", headers=headers)
    # Call service 'red' from service 'green'
    elif (os.environ['SERVICE_NAME']) == 'green':
        for header in TRACE_HEADERS_TO_PROPAGATE:
            if header in request.headers:
                headers[header] = request.headers[header]
        ret = requests.get("http://localhost:9000/trace/red", headers=headers)
    result = render_page()
    tracer.end_span()
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--project_id', help='Project ID you want to access.', required=True)
    args = parser.parse_args()

    tracer = initialize_tracer(args.project_id)
    app.config['TRACER'] = tracer
    app.run(host='0.0.0.0', port=8080, debug=True)