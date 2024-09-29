include .env
SERVICE_NAME=run-pix-admin
IMAGE_NAME=gcr.io/run-pix/run-pix-admin
$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

dev:
	export MODE=DEV;\
	cd src;\
	pwd;\
	export SSL_DISABLE=True MODE=DEV& \
	fastapi dev app.py  --port 8080 --host 0.0.0.0

flask_dev:
	export MODE=DEV;\
	cd src;\
	pwd;\
	SSL_DISABLE=True MODE=DEV FLASK_APP=app_flask.py:app \
	flask run -p 8080

flask_debug:
	cd src;\
	pwd;\
	flask run --debug -p 8080 \
	# --cert=../auth/cert.pem --key=../auth/key.pem 
test:
	# cd test;\
	export MODE=DEV; pytest -rA -v
perf:
	python -m cProfile --o tests/_temp/cProfile.pstats -m pytest -rA;\
	cd tests/_temp;\
	python read_perf.py
d-build:
	docker build . -t ${IMAGE_NAME}

run_cmd:
	gcloud config set run/region us-central1

d-run:
	# docker run -it -t ${IMAGE_NAME} --env-file ./.env 
	docker run -p 8080:8080 --env-file ./.env.docker -e PORT=8080 -t ${IMAGE_NAME}
	#--env SERVICE_ACCOUNT='${SERVICE_ACCOUNT}'

d-push:
	docker push ${IMAGE_NAME}:latest

tbuild:
	gcloud run deploy ${SERVICE_NAME}-test --source . \
        --cpu=1 \
        --max-instances=10 --memory=256M\
        --min-instances=0\
        --env-vars-file=./.env.yaml \
        --allow-unauthenticated \
        --description="Misc services"\
		--region=us-central1
tclean:
	gcloud run deploy delete ${SERVICE_NAME}-test
d-deploy:
	#to be written #
	@echo gcloud auth login --no-launch-browser
	
	gcloud run deploy ${SERVICE_NAME} --image ${IMAGE_NAME} \
        --cpu=1 \
        --max-instances=10 --memory=512M\
        --min-instances=0\
        --env-vars-file=./.env.yaml \
        --allow-unauthenticated \
        --description="Misc services"\
		--region=us-central1
	#--service-account 1008690560612-compute@developer.gserviceaccount.com \
        
          

check_env:
	set 

cors:
	gsutil cors set cors.json gs://indiathon.appspot.com
