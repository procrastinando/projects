import streamlit as st
from sub_translator import sub_translator
from csv_translator import csv_translator
from srt_translator import srt_translator
from img2img import img2img
from ip_insight import ip_insight
from sub2audio import sub2audio
from cv_maker import cv_maker
import yaml

def intro():
    st.sidebar.success("Select a demo above.")
    st.title("Ibarcena Demos")
    st.markdown(
        """
        # My Demos: A Journey Through Code, Ideas, and Exploration 🚀

        Welcome to my little corner of creativity! In these repositories, you’ll find projects that are not just lines of code — they are a reflection of my journey in communication and transportation engineering, haloed by the occasional chaotic brainstorming session. It's like baking — a mix of precise codes and ingredients, sometimes failing spectacularly, but eventually ending up with something uniquely *mine*. What you see here is a work in progress, a living thing that evolves as I grow, much like the ever-thrumming world of technology I live and breathe. 

        ## 1. **CSV Translation Web App: Language Without Borders 🌍**
        [GitHub Repo](https://github.com/procrastinando/translator)

        Imagine holding the power to break through language barriers with just a click. This app harnesses the muscle of **OpenAI**, **LibreTranslate**, and **Ollama APIs** to translate CSV contents into multiple languages, all within an easy-to-use **Streamlit** interface. 

        I built this because translation is, after all, not just about shifting words around. It's about opening doors, connecting strangers, mending distances — and this project attempts to serve that with efficiency and comfort (as much as a CSV can be comfortable, anyway).

        ---

        ## 2. **Image Inpainting API: Painting With AI 🎨**
        [GitHub Repo](https://github.com/procrastinando/img2img-automatic1111-API)

        This is me, indulging in my more artistic side. I created a script that takes an image, a mask, a sprinkle of base64, and some finely tuned algorithms and says, "Hey, let’s fill in the gaps, restore what was lost!" Inspired by my love for crossed-out mistakes in sketchbooks, it’s a playful exploration into AI-powered image restoration. 

        It might sound technical, but really, what I love about it is that it makes me feel like I'm part of this ancient art form — only, it's not ink or brush strokes, it’s pure digital magic.

        ---

        ## 3. **IP Insight: Detective Work for the Curious 🔍**
        This one was born out of pure curiosity. Ever wonder what’s hiding behind an IP address or a domain name, like they’re tiny little secrets waiting to be uncovered? **IP Insight** tackles that — it lets you peek behind the curtain to see who, where, and what powers the digital footprint.

        It's something I built on a late night, after I couldn’t sleep and wanted to play Sherlock. And honestly? It’s more fun than you’d think tracking down geolocations and pinging domains. 

        ---

        ## 4. **Subtitle-to-Audio Converter: Let’s Give Words a Voice 🎤**  
        [GitHub Repo](https://github.com/procrastinando/subtitle-to-audio)

        Text-to-speech. It’s not just about converting subtitles into sound. To me, it’s about *rendering silence redundant*. This app takes cold, lifeless text, and injects it with warmth — voices who may live far away or not at all. Using the **Parler-TTS** model and some subtitle wizardry, it transforms written words into spoken stories.

        It was inspired by those quiet moments when you just *don’t want to read*, but need to listen… perhaps to let someone else’s voice soften the edges of the evening for you. We all need stories, after all. 

        ---

        ## Why These? Because They Matter to Me

        There’s a lot I’m still learning, a lot still unfinished. Some things break. Some don’t work the way I want them to — yet. That’s the beauty of it. Every time I tackle a project, there’s this unquenchable feeling—a *stubborn urge to fix, improve, create.* 

        I’m knee-deep into my PhD in autonomous driving, and although that path is laser-focused, these projects remind me that all of this, even coding and transportation engineering, is fundamentally human. The yearning to connect. The need to visualize. And yes, the recurring sleepless nights because ideas refuse to stop popping up in my head. 

        ### Dive In, Break the Code, Bend It to Your Will.
        These demos aren’t static—they’re alive, and I hope you’ll find in them what I’ve found: a whole lot of chaotic beauty, a step closer to making things simpler, and a dash of magic.
        """
    )

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    if config['token'] == "":
        telegram_token = st.text_input("Enter telegram token")
        bot_username = st.text_input("Enter bot username, for example: cool_bot")
        if st.button("Set token"):
            config['token'] = telegram_token
            config['bot_username'] = bot_username
            with open("config.yaml", "w") as file:
                yaml.dump(config, file)

st.set_page_config(page_title="Ibarcena Demos", page_icon="icon.webp")

def main():
    page_names_to_funcs = {
        "—": intro,
        "CSV translator": csv_translator.main,
        "SRT translator": srt_translator.main,
        "img2img SD API": img2img.main,
        "IP insight": ip_insight.main,
        "Subtitle to audio": sub2audio.main,
        "CV maker": cv_maker.main,
        "Subtitle translator": sub_translator.main,
    }

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()

if __name__ == "__main__":
    main()
