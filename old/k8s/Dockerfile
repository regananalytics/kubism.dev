FROM arm32v7/python:3

RUN mkdir /app
WORKDIR /app
ADD echo_server.py /app/

EXPOSE 65432
CMD ["python", "/app/echo_server.py"]
