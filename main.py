import os
import argparse
from datetime import datetime, timedelta, timezone
from pydub import AudioSegment
import PyPDF2
from openai import OpenAI
from tqdm import tqdm



def extract_text_from_pdf(pdf_path):
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""




class OpenAIPodcastFactory:
    def __init__(self, model_name='gpt-4', input_file=None, output_file=f"{datetime.utcnow()}.mp3"):
        self.model_name = model_name
        self.script = "HOST1:  Sorry, you have not generated a podcast script yet."
        self.output_file = output_file
        self.input_file = input_file

    def _generate_podcast_script(self):
        # Build the prompt
        if not self.input_file:
            raise Exception("Must pass an input file to the OpenAIPodcastFactory object...")

        prompt = ""
        prompt += "Here is the document to summarize:\n"
        prompt += extract_text_from_pdf(self.input_file)

        system_prompt = 'You are an AI language model that generates engaging podcast scripts with two hosts discussing the information they have. ' \
                        'One host should have HOST1: as the start of each line where they talk, and the other should have HOST2:, respond ' \
                        'only with the dialog and who says it and nothing else. Host 1 is named Ali and Host 2 is named Craig.  It MUST be' \
                        'formatted this way, and any other formatting will break the code. Give a quick explanation of the document.  Make it fun and simplify things as best as you can for the layperson.' \
                        'Include the strengths and weaknesses of any analysis contained in the document, otherwise, if it is guidance or policy summarize it. '\
                        'Try to keep the flow of a show.' \

        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.chat.completions.create(model=self.model_name,
                                                  messages=[
                                                      {'role': 'system', 'content': system_prompt},
                                                      {'role': 'user', 'content': prompt}
                                                  ],
                                                  max_tokens=10_000,
                                                  temperature=0.7)
        script = response.choices[0].message.content.strip()

        self.script = script

    def _split_dialogue(self):
        dialogue = []
        current_speaker = None
        lines = self.script.split('\n')
        for line in lines:
            if line.startswith('HOST1:') or line.startswith('HOST 1:'):
                current_speaker = 'HOST1'
                content = line.split(':', 1)[1].strip()
                dialogue.append((current_speaker, content))
            elif line.startswith('HOST2:') or line.startswith('HOST 2:'):
                current_speaker = 'HOST2'
                content = line.split(':', 1)[1].strip()
                dialogue.append((current_speaker, content))
            elif current_speaker:
                dialogue.append((current_speaker, line.strip()))
        return dialogue


    def generate_audio(self,
                       speed=1.0,
                       model='tts-1',
                       default_voice='nova',
                       voice_map={
                                'HOST1': 'nova',  # Voice for Host1
                                'HOST2': 'onyx',  # Voice for Host2
                                'HOST3': 'echo'
                                },
                       verbose=False,
                       ):
        if not os.path.exists("temp"):
            os.makedirs("temp")

        if verbose:
            print('Generating podcast script...')

        self._generate_podcast_script()

        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        audio_files = []

        iterator = tqdm(enumerate(self._split_dialogue())) if verbose else enumerate(self._split_dialogue())
        for i, (speaker, line) in iterator:
            voice = voice_map.get(speaker, default_voice)  # Default to Nova if speaker not found
            if not line:
                continue
            try:
                response = client.audio.speech.create(input=line,
                                                      voice=voice,
                                                      speed=speed,
                                                      model=model)
                filename = os.path.join("temp", f"{speaker}_{i}.mp3")
                audio_files.append(filename)
                response.write_to_file(filename)
            except Exception as e:
                print(f"Error generating audio for line '{line}': {e}")


        combined = AudioSegment.empty()
        for filename in audio_files:
            sound = AudioSegment.from_mp3(filename)
            combined += sound
        combined.export(self.output_file, format='mp3')
        if verbose:
            print(f"Exported podcast audio to {self.output_file}")

        # clean up our mess
        for file in audio_files:
            os.remove(file)
        os.rmdir("temp")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a podcast from recent arXiv papers.')
    parser.add_argument('--input_file', help="Input file name")
    parser.add_argument('--llm', default='gpt-4o', help='Model name for openAI model.')
    parser.add_argument('--tts', default='tts-1', help='Model name for text-to-speech.')
    parser.add_argument("--output_file", help="Output file name")

    args = parser.parse_args()

    input_file = args.input_file
    llm = args.llm
    tts = args.tts
    output_file = args.output_file

    factory = OpenAIPodcastFactory(
        model_name=llm, input_file=input_file, output_file=output_file,
    )
    factory.generate_audio(model=tts, verbose=True)

