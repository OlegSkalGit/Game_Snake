"""
Music Generator using Google Lyria 3.5 (lyria-3.5-pro-preview / lyria-3.5-clip-preview).
Generates rich, atmospheric, thematic background music tracks for all 18 worlds in 3D Snake Adventure.

Usage:
  python generate_music_lyria.py --theme forest
  python generate_music_lyria.py --all
  python generate_music_lyria.py --list
  python generate_music_lyria.py --theme space --format mp3
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load credentials from .env in current directory or user home
load_dotenv()
load_dotenv(os.path.expanduser("~/.env"))

THEME_PROMPTS = {
    'forest': (
        "Peaceful fantasy woodland adventure soundtrack, acoustic guitar fingerpicking, "
        "gentle wooden flutes, warm melodic marimba, soft rhythmic forest percussion, "
        "lush nature ambiance, loopable background game music"
    ),
    'desert': (
        "Ancient Egyptian desert adventure music, mystic oud melodies, ney flute, "
        "framed darbuka hand drums, warm shimmering winds, exotic caravan theme, loopable"
    ),
    'ocean': (
        "Deep tranquil ocean seabed soundtrack, ethereal aquatic pads, gentle reverberant "
        "piano notes, soft underwater bubbles and sonar pulse, serene marine mystery, loopable"
    ),
    'space': (
        "Deep cosmic sci-fi space synthwave, analog synthesizer arpeggios, pulsing retro "
        "bassline, starry ambient pads, majestic celestial odyssey, loopable"
    ),
    'factory': (
        "Cyberpunk industrial factory music, rhythmic mechanical percussion, heavy grinding "
        "bass synth, energetic punchy electronic beat, high-tech cyber groove, loopable"
    ),
    'city': (
        "Neon metropolis night synthwave, upbeat retro electro drums, driving synth leads, "
        "smooth urban night vibe, futuristic skyline rhythm, loopable"
    ),
    'arctic': (
        "Frozen glacial tundra soundtrack, crystal music box, sparkling ice chimes, "
        "cold atmospheric wind textures, serene delicate winter melody, loopable"
    ),
    'lava': (
        "Dramatic volcanic inferno soundtrack, driving rock drums, heavy distorted bass guitar, "
        "cinematic brass stabs, intense fiery volcanic adrenaline, loopable"
    ),
    'crystal': (
        "Magical sparkling crystal cavern music, resonant celesta, shimmering glass bells, "
        "ethereal fantasy strings, magical echoing harmonies, loopable"
    ),
    'jungle': (
        "Vibrant tropical rainforest adventure, energetic tribal djembe and bongo percussion, "
        "lively bamboo pan flutes, exotic jungle groove, loopable"
    ),
    'sky': (
        "Sky sanctuary orchestral theme, soaring aerial violins, majestic horns, "
        "uplifting fantasy adventure melody, floating cloud islands, loopable"
    ),
    'toxic': (
        "Dark acidic toxic wasteland electronic soundtrack, heavy glitch hop beats, "
        "resonant 303 acid bassline, hazardous radioactive atmosphere, loopable"
    ),
    'swamp': (
        "Atmospheric mystic swamp bayou soundtrack, slide acoustic resonator guitar, "
        "slow bluesy bass groove, eerie ambient twilight swamp vibe, loopable"
    ),
    'necropolis': (
        "Ancient gothic necropolis theme, somber cathedral pipe organ, eerie haunting choir, "
        "slow dramatic timpani, mysterious pharaoh tomb, loopable"
    ),
    'steampunk': (
        "Victorian steampunk airship theme, energetic brass section, ticking clockwork gears, "
        "lively accordion, bouncy whimsical adventure rhythm, loopable"
    ),
    'event_horizon': (
        "Black hole event horizon dark cinematic ambient soundtrack, pulsating deep sub-bass, "
        "mysterious granular textures, cosmic spacetime distortion, loopable"
    ),
    'dungeon': (
        "Dark medieval stone castle dungeon music, ominous minor-key harpsichord, "
        "deep cello, heavy war drums, classic dungeon crawler tension, loopable"
    ),
    'quantum': (
        "Hyper-energetic quantum speedway techno, blisteringly fast synth sequences, "
        "heavy cyber drops, futuristic electronic beats, boss battle energy, loopable"
    )
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(PROJECT_ROOT, "sounds")

def check_gemini_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n" + "=" * 65)
        print("❌ ПОМИЛКА: Не знайдено ключ GEMINI_API_KEY!")
        print("=" * 65)
        print("Щоб використовувати модель Lyria 3.5 для створення музики,")
        print("отримайте ключ на https://aistudio.google.com/")
        print("та налаштуйте його в середовищі або у файлі .env:\n")
        print("У PowerShell (безпечне додавання без збереження в історії):")
        print('  $val = Read-Host "Введіть GEMINI_API_KEY" -AsSecureString')
        print('  $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($val)')
        print('  $key = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)')
        print('  Add-Content -Path .env -Value "GEMINI_API_KEY=$key"')
        print("\nАбо запустіть команду з ключем:")
        print('  $env:GEMINI_API_KEY="ваш_ключ"; python generate_music_lyria.py --all')
        print("=" * 65 + "\n")
        return None
    return api_key

def generate_track(theme, prompt, client, model="lyria-3.5-pro-preview", output_format="wav"):
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    ext = "wav" if output_format.lower() == "wav" else "mp3"
    mime_type = "audio/wav" if ext == "wav" else "audio/mp3"
    target_file = os.path.join(SOUNDS_DIR, f"bgm_{theme}.{ext}")

    print(f"\n🎵 [Lyria 3.5] Створення треку для теми '{theme}'...")
    print(f"   Модель: {model}")
    print(f"   Опис: {prompt[:75]}...")

    from google.genai import types

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                response_format={"audio": {"mime_type": mime_type}}
            )
        )
    except Exception as e:
        print(f"   ⚠️ Помилка виклику моделі {model}: {e}")
        if model != "lyria-3.5-clip-preview":
            print("   Перехід на резервну модель lyria-3.5-clip-preview...")
            return generate_track(theme, prompt, client, model="lyria-3.5-clip-preview", output_format=output_format)
        return False

    audio_bytes = None
    if hasattr(response, 'parts') and response.parts:
        for part in response.parts:
            if getattr(part, 'inline_data', None) is not None:
                audio_bytes = part.inline_data.data
                break
    elif hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
            for part in candidate.content.parts:
                if getattr(part, 'inline_data', None) is not None:
                    audio_bytes = part.inline_data.data
                    break

    if audio_bytes:
        with open(target_file, "wb") as f:
            f.write(audio_bytes)
        print(f"   ✅ Трек збережено: sounds/bgm_{theme}.{ext} ({len(audio_bytes):,} байт)")
        return True
    else:
        print("   ❌ Не вдалося отримати аудіо-дані з відповіді моделі.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Створення фонової музики за допомогою Lyria 3.5")
    parser.add_argument("--theme", type=str, help="Назва теми (наприклад, forest, desert, ocean...)")
    parser.add_argument("--all", action="store_true", help="Згенерувати музику для всіх 18 світів")
    parser.add_argument("--list", action="store_true", help="Список доступних тем")
    parser.add_argument("--model", type=str, default="lyria-3.5-pro-preview", help="Модель Lyria (lyria-3.5-pro-preview або lyria-3.5-clip-preview)")
    parser.add_argument("--format", type=str, default="wav", choices=["wav", "mp3"], help="Формат аудіо (wav або mp3)")

    args = parser.parse_args()

    if args.list:
        print("Доступні теми для генерації музики:")
        for idx, t in enumerate(THEME_PROMPTS.keys(), 1):
            print(f"  {idx:2d}. {t:<15} - {THEME_PROMPTS[t][:60]}...")
        return

    api_key = check_gemini_api_key()
    if not api_key:
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    if args.theme:
        theme = args.theme.lower()
        if theme not in THEME_PROMPTS:
            print(f"Невідома тема '{theme}'. Використовуйте --list для перегляду доступних тем.")
            sys.exit(1)
        generate_track(theme, THEME_PROMPTS[theme], client, model=args.model, output_format=args.format)

    elif args.all:
        print(f"🚀 Початок генерації музики для всіх 18 світів за допомогою {args.model}...")
        success_count = 0
        for theme, prompt in THEME_PROMPTS.items():
            if generate_track(theme, prompt, client, model=args.model, output_format=args.format):
                success_count += 1
        print(f"\n🎉 Завершено! Успішно створено {success_count}/{len(THEME_PROMPTS)} треків.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
