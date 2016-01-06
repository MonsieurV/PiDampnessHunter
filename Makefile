PID=$(shell cat run.pid)

start:
	/usr/bin/python -u app.py > log.txt 2>&1 & echo $$! > run.pid

stop:
	kill -2 ${PID}
