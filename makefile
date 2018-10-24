run: 
	. h/bin/activate
setup:
	python3 -m venv h/
	. h/bin/activate
	pip3 install wheel
	pip3 install flask
	pip3 install passlib
remove:
	rm -rf h/
