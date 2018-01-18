deps:
	pip install -r requirements.txt

# empty for everything
TICKERS=

test: deps
	python test.py

run: test
	echo "follow progress with tail -f progress.log"
	python main.py $(TICKERS) > result/`date +%Y%m%d`.html
	xdg-open result/`date +%Y%m%d`.html
