.PHONY: install serve

install:
    pip install -r requirements.txt && \
    cd autoprompt-ui && \
    npm install && \
	cd ..

serve:
    npm run watch --prefix autoprompt-ui & \
    uvicorn webapp:app --reload && \
    fg