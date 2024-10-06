# OpenAIPodcastFactory

This project generates a podcast from a given PDF document using OpenAI's GPT model for text summarization and Text-to-Speech (TTS) for generating audio. It produces a conversational podcast format with two hosts (Ali and Craig) discussing the content of the document.

## Features

Text extraction from PDFs: Extracts text from the provided PDF document.
Automatic script generation: Uses OpenAI's language model to generate a podcast script in the form of a conversation between two hosts.
Text-to-Speech (TTS): Converts the podcast script into audio using OpenAI's TTS models.
Audio processing: Merges the generated audio into a single MP3 file.

## Requirements

    Python 3.6+
    OpenAI API Key
    Libraries:
        os
        argparse
        datetime
        pydub
        PyPDF2
        tqdm
        openai

You can install the required dependencies using:

```bash
pip install pydub PyPDF2 tqdm openai
```

Usage

To run the script, execute the following command:

```bash

python openai_podcast_factory.py --input_file <path_to_pdf> --llm <llm_model_name> --tts <tts_model_name> --output_file <output_file_path>

```

Arguments:

    --input_file: Path to the PDF file from which the script will extract text.
    --llm: The name of the OpenAI model to use for generating the podcast script. Default is gpt-4o.
    --tts: The name of the TTS model to use for generating the podcast audio. Default is tts-1.
    --output_file: The file name for the generated MP3 podcast. If not provided, the output will be saved as a timestamped MP3 file.

Example:

bash
```bash
  python openai_podcast_factory.py --input_file "example.pdf" --llm "gpt-4" --tts "tts-1" --output_file "podcast.mp3"
```

Workflow

    Text Extraction: Extracts text from the specified PDF file using the PyPDF2 library.
    Script Generation: Prompts OpenAI's model to create a dialogue between two hosts (Ali and Craig) discussing the content of the PDF file.
    Audio Generation: Converts the generated dialogue into audio using the TTS model and combines all audio segments into a single MP3 file.
    Output: Saves the generated podcast as an MP3 file.

Notes

    Ensure you have a valid OpenAI API key stored in your environment as OPENAI_API_KEY.
    The script creates temporary files for audio segments, which are deleted after the final podcast is generated.

License

This project has absolutely no licensing whatsoever, do whatever you want with it.