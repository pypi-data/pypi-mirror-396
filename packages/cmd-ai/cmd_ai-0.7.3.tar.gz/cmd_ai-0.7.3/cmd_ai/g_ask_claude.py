
from cmd_ai import api_key
from cmd_ai import config, texts, api_key
import sys

from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from console import fg,bg,fx

import anthropic

def announce_model(model):
    """
    same printout for all
    """
    #print("...",bg.green," >>OK", bg.default, f" model={model}")
    print(fg.dimgray, "... ... ... ... ...  model=",texts.color_of_model(model, inverse=True), model, fg.default, bg.default)


# ============================================================
#
# ------------------------------------------------------------
#
# ============================================================
#    ANTHROPIC return resp_content, resp_reason, config.MODEL_TO_USE
# ------------------------------------------------------------
#
def g_ask_claude(prompt ,
                 temp=0,
                 model="claude-3-7-sonnet-20250219",
#                 model="claude-3-5-sonnet-20241022",
                 #role=None,
                 dontadd=False):
    STOPPED_BY_LENGTH = False
    # ** init
    APIKEY = api_key.get_api_key_anthropic()
    if APIKEY is None:
        return "failed", "failed", model
    config.client = anthropic.Anthropic(api_key=APIKEY)

    system_prompt = texts.role_assistant
    #if role is None:
    #    system_prompt = texts.role_assistant
    # my message system (may be difference in naming)
    nmsg = []
    for i in config.messages:
        nmsg.append( i )

    nmsg.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    limit_tokens = config.CONFIG['limit_tokens']

    #********************************************** GO
    message = config.client.messages.create(
        model=model,
        max_tokens=limit_tokens,
        temperature=temp,
        system=system_prompt,
        messages=nmsg
    )
    # **********
    response = message.content
    res = response[0].text #decode_response_anthropic(message.content)

    # i just add prompt and answer here....bug until 20250405
    if not dontadd:
        config.messages.append(  {"role": "user", "content": prompt} )
        config.messages.append(  {"role": "assistant", "content": res} )

    if not config.silent:
        announce_model(model)
        #print("...",bg.green," >>OK", bg.default, f" model={model}") # claude
    return res, STOPPED_BY_LENGTH, model
