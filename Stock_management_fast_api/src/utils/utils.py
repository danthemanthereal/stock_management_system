from fastapi import  Request
import json
from pathlib import Path
from starlette.templating import Jinja2Templates

print(Path(__file__).parents[2].absolute())
with open(f"{str(Path(__file__).parents[2].absolute())}/locales/de.json", "r", encoding="utf-8") as f:
    de_translations = json.load(f)
with open(f"{str(Path(__file__).parents[2].absolute())}/locales/en.json", "r", encoding="utf-8") as f:
    en_translations = json.load(f)

translations = {"de": de_translations, "en": en_translations}

templates = Jinja2Templates(directory="templates")
def render_localized(template_name: str, request: Request, context: dict):
    locale = get_locale(request)
    lang_dict = translations.get(locale, translations["en"])

    def translate(key: str) -> str:
        return lang_dict.get(key, key)

    context["_"] = translate
    context["current_locale"] = locale

    return templates.TemplateResponse(request, template_name, context)


def get_locale(request: Request) -> str:
    lang = request.query_params.get("lang")
    if lang in ["de", "en"]:
        return lang

    lang = request.cookies.get("preferred_lang")
    if lang in ["de", "en"]:
        return lang

    accept_language = request.headers.get("Accept-Language", "")
    if "de" in accept_language.lower():
        return "de"

    return "en"