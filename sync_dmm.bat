@echo off
if not exist "output" mkdir "output"
cd tools/gamewith/
pipenv run scrapy crawl support_card
cd ../..
cd scripts/
call gen_all_resources.bat < nul
cd ..
pipenv run python run_local.py
pause
