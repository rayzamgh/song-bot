import base64
import io
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage

def encode_image_pil(image):
    ''' Convert PIL Image to base64 string '''
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def extract_image(image, prompt):
    ''' Extracts information from a PIL Image using GPT-4 Vision Preview model '''
    # Encode the image to base64
    img_base64 = encode_image_pil(image)

    # Initialize the ChatOpenAI model
    chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024)

    # Create the message with the image and the prompt
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}",
                            "detail": "auto",
                        },
                    },
                ]
            )
        ]
    )
    # Return the model's response
    return msg.content
