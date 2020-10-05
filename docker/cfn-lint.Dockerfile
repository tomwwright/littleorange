FROM python:3.8-alpine

RUN pip install cfn-lint
RUN pip install pydot

WORKDIR /path
ENTRYPOINT ["cfn-lint"]
CMD ["--help"]