config:
	bash autoconfig.sh
clean:
	rm data/*
	touch data/people.txt
	touch data/shifts.csv
commit: clean
	git add *
	git commit
	git push origin master
build: commit
	git push heroku master
