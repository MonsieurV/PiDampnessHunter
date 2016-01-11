PID=$(shell cat run.pid)

start:
	/usr/bin/python -u web.py > log.txt 2>&1 & echo $$! > run.pid

stop:
	kill -2 ${PID}
