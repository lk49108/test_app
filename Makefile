run: setup
	python manage.py runserver

setup: requirements.txt
	pip install -r requirements.txt

clean:
	rm -rf __pycache__