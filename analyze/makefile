deps:
	pip install -r requirements.txt

TICKERS=ONT TGP	1ST 1PG MOQ T3D

test: deps
	python test.py

run: test
	python main.py $(TICKERS) > result/`date +%Y%m%d`.html
	xdg-open result/`date +%Y%m%d`.html
