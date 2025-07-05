Some basic instructions for running the package. 

1. In a terminal, launch `server.py`. This will start a local server with an LLM and DB that will be listening. You can specify the model you want to use with the arugment `--model`, Ex : `python3 server.py --model Qwen/Qwen3-4B`
2. Go to firefox, type `about:debugging` in page, then go to `This Firefox`, `Load Temporary Add-on`, and click on any files in the `yololo/Firefox_Extension` folder.
3. When you go to another page (ex reddit) and select text, you should have a button appearing next to it. When you click on it, it should send the text to the server for fact checking with RAG> 