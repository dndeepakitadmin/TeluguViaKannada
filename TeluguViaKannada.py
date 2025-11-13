import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process as aksharamukha_process
from gtts import gTTS
from io import BytesIO
import unicodedata
import time

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Kannada → Telugu Learning",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------- HIDE TOOLBAR ---------------- #
hide_streamlit_style = """
<style>
#MainMenu {visibility:hidden;}
header {visibility:hidden;}
footer {visibility:hidden;}
[data-testid="stToolbar"] {visibility:hidden !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------- HELPERS ---------------- #
def make_audio_bytes(text, lang="te"):
    fp = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def safe_aksharamukha(src, tgt, text):
    """Robust conversion wrapper."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    for s in [src, src.capitalize(), src.upper(), src.title()]:
        for t in [tgt, tgt.capitalize(), tgt.upper(), tgt.title()]:
            try:
                out = aksharamukha_process(s, t, text)
                if out and out.strip():
                    return out
            except:
                pass
    return text

def itrans_to_english_pron(x):
    """Convert Kannada ITRANS → simple readable English phonetics."""
    x = x.replace("A", "aa").replace("I", "ee").replace("U", "oo")
    x = x.replace("E", "ee").replace("O", "oo")
    x = x.replace(".", "")
    x = x.replace("M", "n").replace("H", "h")
    x = x.replace("sh", "sh").replace("ch", "ch")
    return x.lower().strip()

# ---------------- UI ---------------- #
st.title("📝 Learn Telugu using Kannada")
st.subheader("ಕನ್ನಡ → తెలుగు")

kannada_text = st.text_area(
    "Enter Kannada text:", 
    height=150,
    placeholder="ಉದಾಹರಣೆ: ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ"
)

if st.button("Translate"):
    if not kannada_text.strip():
        st.warning("Please enter Kannada text.")
    else:
        # Normalize
        kannada_norm = unicodedata.normalize("NFC", kannada_text.strip())

        # ---------------- SENTENCE-LEVEL ---------------- #
        telugu_sentence = GoogleTranslator(source="kn", target="te").translate(kannada_norm)

        # Telugu (native script)
        telugu_native = telugu_sentence

        # Telugu → Kannada phonetic script
        telugu_in_kannada = safe_aksharamukha("Telugu", "Kannada", telugu_native)

        # Telugu → English phonetic (via Kannada → ITRANS → English)
        itr_raw = transliterate(telugu_in_kannada, sanscript.KANNADA, sanscript.ITRANS)
        english_phonetic = itrans_to_english_pron(itr_raw)

        # Sentence audio
        audio_sentence = make_audio_bytes(telugu_native, lang="te")

        # ---------------- OUTPUT ---------------- #
        st.markdown("## 🔹 Sentence Output")

        st.write("### **Kannada Input:**")
        st.write(kannada_norm)

        st.write("### **Telugu (తెలుగు):**")
        st.write(telugu_native)

        st.write("### **Telugu in Kannada Script (phonetic base):**")
        st.write(telugu_in_kannada)

        st.write("### **English Phonetic Pronunciation:**")
        st.code(english_phonetic)

        st.write("### 🔊 Telugu Audio (Sentence)")
        st.audio(audio_sentence, format="audio/mp3")
        st.download_button("Download Telugu Sentence Audio", audio_sentence, "telugu_sentence.mp3")

        # ---------------- FLASHCARDS ---------------- #
        st.markdown("---")
        st.markdown("## 🃏 Flashcards — Word-by-Word")

        kannada_words = kannada_norm.split()
        telugu_words = []

        # Per-word translation
        for w in kannada_words:
            try:
                tw = GoogleTranslator(source="kn", target="te").translate(w)
            except:
                tw = ""
            telugu_words.append(tw)
            time.sleep(0.05)

        for i, k_word in enumerate(kannada_words):
            t_word = telugu_words[i]

            # Telugu → Kannada
            t_in_kannada = safe_aksharamukha("Telugu", "Kannada", t_word)

            # Telugu → English phonetics
            t_itr = transliterate(t_in_kannada, sanscript.KANNADA, sanscript.ITRANS)
            t_english = itrans_to_english_pron(t_itr)

            # Word audio
            t_audio = make_audio_bytes(t_word, lang="te") if t_word else b""

            with st.expander(f"Word {i+1}: {k_word}", expanded=False):
                st.write("**Kannada:**", k_word)
                st.write("**Telugu:**", t_word)
                st.write("**Telugu in Kannada Script:**", t_in_kannada)
                st.write("**English Phonetic:**")
                st.code(t_english)

                if t_audio:
                    st.audio(t_audio, format="audio/mp3")
                    st.download_button(
                        f"Download Word Audio {i+1}",
                        t_audio,
                        f"te_word_{i+1}.mp3",
                        mime="audio/mpeg"
                    )
                else:
                    st.write("_No audio for this word._")
