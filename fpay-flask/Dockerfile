FROM jamestjw/face-rec
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp
RUN pip install -r ./requirements.txt
RUN adduser -D myuser
USER myuser
ENTRYPOINT ["python"]
CMD ["app.py"]