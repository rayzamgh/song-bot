# song-bot
Deploy by : 
- docker build -t song-bot .
- docker run song-bot
- docker tag song-bot gcr.io/portfolio-web-249407/song-bot-latest
- gcloud auth configure-docker
- docker push gcr.io/portfolio-web-249407/song-bot-latest

In VM
- docker pull gcr.io/portfolio-web-249407/song-bot-latest
- docker run gcr.io/portfolio-web-249407/song-bot-latest

gcloud compute instances create-with-container instance-template-1 --project=portfolio-web-249407 --zone=us-central1-a --machine-type=e2-micro --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=ga-song@portfolio-web-249407.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --enable-display-device --tags=http-server,https-server --image=projects/cos-cloud/global/images/cos-stable-105-17412-156-4 --boot-disk-size=10GB --boot-disk-type=pd-balanced --boot-disk-device-name=instance-template-1 --container-image=gcr.io/portfolio-web-249407/song-bot-latest --container-restart-policy=always --container-tty --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud,container-vm=cos-stable-105-17412-156-4