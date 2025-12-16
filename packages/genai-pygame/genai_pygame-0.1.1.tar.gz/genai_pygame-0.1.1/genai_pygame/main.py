from transformers import pipeline

pipe = pipeline()

def create_model(model_name: str):
    return_model = pipeline(
        "text-generation",
        model=model_name
    )

    return return_model

def generate_response(model: str, message: str, max_tokens: int, temperature: float):
    response = model(
        message,
        max_new_tokens=max_tokens,
        temperature=temperature
    )

    return response

model = create_model("gpt2")
print(generate_response(model, "How are you?", max_tokens=40, temperature=0.5))