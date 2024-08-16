bundle:
	tar -czf module.tar.gz run.sh process.py requirements.txt

clean:
	rm -rf module.tar.gz