include .env
SERVICE_NAME=run-pix-admin
IMAGE_NAME=gcr.io/run-pix/run-pix-admin
$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))


dev:
	cd src;\
	pwd;\
	export SSL_DISABLE=True & \
	flask run -p 8080

debug:
	cd src;\
	pwd;\
	flask run --debug -p 8080 \
	# --cert=../auth/cert.pem --key=../auth/key.pem 

tem:
	python template.py

build:
	docker build . -t ${IMAGE_NAME}

run_cmd:
	gcloud config set run/region us-central1
	

run:
	# docker run -it -t ${IMAGE_NAME} --env-file ./.env 
	docker run -p 8080:8080 --env-file ./.env -t ${IMAGE_NAME}
	#--env SERVICE_ACCOUNT='${SERVICE_ACCOUNT}'

push:
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
deploy:
	#to be written #
	@echo gcloud auth login --no-launch-browser
	
	gcloud run deploy ${SERVICE_NAME} --image ${IMAGE_NAME} \
        --cpu=0.5 \
        --max-instances=10 --memory=256M\
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
