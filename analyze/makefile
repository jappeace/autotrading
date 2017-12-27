deps:
	pip install -r requirements.txt
run: deps
	python main.py > result/`date +%Y%m%d`.html
	xdg-open result/`date +%Y%m%d`.html
