all:
	@echo "Fenrir: Asynchronous HTTP Server"

ragel:
	ragel -G2 fenrir/c/http11/src/http11/http11_parser.rl
	ragel -G2 fenrir/c/http11/src/http11/httpclient_parser.rl
	sed -i '' -e 's/[ ]*$$//g' fenrir/c/http11/src/http11/http11_parser.c
	sed -i '' -e 's/[ ]*$$//g' fenrir/c/http11/src/http11/httpclient_parser.c
