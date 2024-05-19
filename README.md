# Song-Bot

Song-Bot is an advanced, highly interactive, and conversational Discord bot designed to engage users through voice channels. It leverages cutting-edge technologies such as speech recognition, natural language processing, text-to-speech synthesis, and image generation to provide a rich and immersive user experience.

## Features

### Voice Recognition

- Utilizes Google Cloud Speech-to-Text and OpenAI Whisper to accurately transcribe audio from Discord voice channels into text.

### Natural Language Processing

- Employs LangChain for advanced processing of transcribed text to understand user intent, context, and sentiment.
- Utilizes a custom-built "Song Brain" powered by OpenAI's GPT-3 to generate contextually relevant and engaging responses.

### Text-to-Speech Synthesis

- Leverages ElevenLabs API to generate high-quality, realistic voice responses based on the bot's persona.

### Image Generation

- Utilizes DALL-E and Stable Diffusion to generate images based on user prompts or conversation context.

### Scheduled Messages and Tasks

- Sends periodic messages to designated channels to keep users engaged and informed.
- Performs scheduled tasks such as updating the bot's internal clock and fetching news updates from the GameSpot API.

### Extensible Plugin System

- Implements a modular plugin system to easily add new features and functionality to the bot.

### Custom Bot Commands

- Supports custom bot commands such as "song diem" and "halo song" to control the bot's behavior.

### GameSpot Integration

- Fetches the latest articles, games, and releases from the GameSpot API and shares them in designated channels.

### Clock and Scheduling

- Maintains an internal clock to keep track of the bot's activities and schedule tasks accordingly.

### CI/CD with GitHub Actions

- Utilizes GitHub Actions for continuous integration and deployment.
- Automatically builds and pushes Docker images to Google Container Registry (GCR) on each push to the main branch.

## Technologies Used

- Python
- Discord.py
- Google Cloud Speech-to-Text
- OpenAI GPT-3 and Whisper
- LangChain
- ElevenLabs API
- DALL-E and Stable Diffusion
- GameSpot API
- Docker
- Google Cloud Platform (GCP)
- GitHub Actions

## Setup and Deployment

### Clone the repository

```
git clone https://github.com/yourusername/song-bot.git
```

### Install the required dependencies

```
pip install -r requirements.txt
```

### Set up the necessary environment variables

- GOOGLE_API_KEY
- GOOGLE_CSE_ID
- CLIENT_ID
- CLIENT_SECRET
- OPENAI_API_KEY
- FIREBASE_API_KEY
- DISCORD_TOKEN
- GOOGLE_APPLICATION_CREDENTIALS
- GAMESPOT_API_KEY
- ACTIVE_CHANNEL_NAME
- ELEVENLABS_API_KEY
- COHERE_API_KEY
- GEMINI_API_KEY

### Build the Docker image

```
docker build -t song-bot .
```

### Run the Docker container

```
docker run song-bot
```

### Deploy the bot to Google Cloud Platform (optional)

- Tag the Docker image:
  ```
  docker tag song-bot gcr.io/portfolio-web-249407/song-bot-latest
  ```

- Configure Docker to use gcloud as the credential helper:
  ```
  gcloud auth configure-docker
  ```

- Push the Docker image to Google Container Registry:
  ```
  docker push gcr.io/portfolio-web-249407/song-bot-latest
  ```

- Create a VM instance with the container:
  ```
  gcloud compute instances create-with-container instance-template-1 --project=portfolio-web-249407 --zone=us-central1-a --machine-type=e2-micro --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=ga-song@portfolio-web-249407.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --enable-display-device --tags=http-server,https-server --image=projects/cos-cloud/global/images/cos-stable-105-17412-156-4 --boot-disk-size=10GB --boot-disk-type=pd-balanced --boot-disk-device-name=instance-template-1 --container-image=gcr.io/portfolio-web-249407/song-bot-latest --container-restart-policy=always --container-tty --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud,container-vm=cos-stable-105-17412-156-4
  ```

## Bot Architecture

### bot/

- Contains the core bot implementation and plugins.
- `__init__.py`: Initializes the bot module.
- `bot.py`: Defines the main

 SongBot class, which inherits from various plugin classes.

### plugin/

- Contains plugin modules for different bot functionalities.
- `__init__.py`: Initializes the plugin module.
- `babble.py`: Implements the babbling functionality for the bot.
- `clock.py`: Handles the bot's internal clock and scheduling tasks.
- `config.py`: Stores configuration variables for the bot.
- `gamespot.py`: Integrates with the GameSpot API to fetch and share gaming-related content.
- `voice.py`: Manages voice-related functionalities, such as voice recognition and text-to-speech.

### apis/

- Contains API integration modules.
- `__init__.py`: Initializes the APIs module.
- `news.py`: Implements the GameSpot API integration.

### .github/workflows/

- Contains GitHub Actions workflows for CI/CD.
- `docker-publish.yml`: Defines the workflow to build and push Docker images to GCR.

### credentials/

- Stores credential files for various services (e.g., Google Cloud credentials).

### module/

- Contains modules for specific functionalities.

### brain/

- Implements the "Song Brain" module for natural language processing and response generation.
- `__init__.py`: Initializes the brain module.
- `brain.py`: Defines the main SongBrain class.
- `keeper.py`: Manages the bot's internal state and memory.
- `prompts.py`: Stores prompt templates for generating responses.

### interractor/

- Contains modules for interacting with external services and APIs.
- `base_interractor.py`: Defines the base class for interactors.
- `image.py`: Implements image generation functionality using DALL-E and Stable Diffusion.

### router/

- Implements the message routing system for the bot.
- `router.py`: Defines the Router class for routing messages to appropriate handlers.

### utils/

- Contains utility functions used throughout the bot.

### main.py

- The entry point of the bot application.

### Dockerfile

- Defines the Docker image for the bot.

### requirements.txt

- Lists the Python dependencies required by the bot.

### README.md

- Provides an overview of the bot, its features, and setup instructions.

## Usage

Once the bot is deployed and running, it will automatically join the designated voice channels and start listening for user interactions. Users can engage with the bot through voice commands, text messages, and by requesting image generation.

## Contributing

Contributions to Song-Bot are welcome! If you find any bugs, have feature requests, or want to contribute improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgements

Song-Bot was developed using various open-source libraries and APIs. We would like to express our gratitude to the developers and communities behind these projects for their valuable contributions.