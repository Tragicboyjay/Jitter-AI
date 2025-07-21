

# Jitter

Jitter is a simple, modular framework for building conversational AI agents with retrieval-augmented generation (RAG) and multi-provider support (Google Gemini, OpenRouter, etc.).

---

## How to Use

### 1. Set up your environment

- Run the setup script to create a virtual environment and install dependencies:

  ```bash
  python setup.py
  ```

- Follow the printed instructions to activate your environment before starting Jitter.

---

### 2. Configure environment variables

- Copy the provided `.env Example` file and edit it to add your API keys and model values for Google or OpenRouter.
- Set `OPENROUTER_API_KEY`, `OPENROUTER_MODEL_ID`, `GOOGLE_API_KEY`, and `GOOGLE_MODEL_ID` as needed.

  ```bash
  pip install -r requirements.txt
  ```

---

### 3. Create your agent

- Copy and edit the provided being template (e.g., `being.json example`) to define your agent's character, knowledge, and style.
- Place your being file in the `beings` directory (e.g., `beings/your_agent.json`).
- Add any `.txt`, `.pdf`, `.html`, `.csv`, or `.md` files to the `files` folder for extra knowledge (RAG).

---

### 4. Start the backend server

  ```bash
  python main.py --being your_agent
  ```

- Replace `your_agent` with the name of your being file (without `.json`).
- If you do not specify `--being`, the default agent will be loaded.
- The API will be available at `http://localhost:8000`.

---

### 5. (Optional) Start the client

- After starting your agent, open a new terminal window.
- Change directory to the `client` folder:

  ```bash
  cd client
  ```

- Start the client:

  ```bash
  npm run dev
  ```

---

### 6. Agent Live Status (Optional)

- Jitter can run a background "live" task that prints how the agent is feeling, based on recent messages and context.
- To enable, set `AGENT_ALIVE=True` in your `.env` file (enabled by default).
- The agent will periodically print its mood and status to the console, making the experience more interactive and fun.

---

### 7. Chat with your agent

- Use the `/message` endpoint to send messages and get responses.
- Use the `/being` endpoint to see your agent's details.

---

## Features

- Easy agent customization via `being.json` (character, knowledge, style)
- Supports RAG from `.txt`, `.pdf`, `.html`, `.csv`, `.md` files
- Multi-provider: Google Gemini, OpenRouter, and more
- Add custom tools/functions for your agent to use

---

## License

MIT