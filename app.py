from dotenv import load_dotenv

load_dotenv()

from desk import create_app  # noqa: E402  (OPENAI_API_KEY must be loaded first)

app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
