
from cmd_ai import api_key
from cmd_ai import config, texts, api_key
import sys

from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from console import fg,bg,fx

#client = genai.Client( )


def announce_model(model):
    """
    same printout for all
    """
    #print("...",bg.green," >>OK", bg.default, f" model={model}")
    print(fg.dimgray, "... ... ... ... ...  model=",texts.color_of_model(model, inverse=True), model, fg.default, bg.default)


# ============================================================
#    GOOGLE GEMINI return resp_content, resp_reason, config.MODEL_TO_USE
# ------------------------------------------------------------
#
def g_ask_gemini(prompt ,
                 temp=0,
                 model="gemini-3-pro-preview",
#                 model="gemini-2.5-pro-exp-03-25",
#                 max_tokens=1000,
#                 role=None,
                 dontadd=False):
    APIKEY = api_key.get_api_key_gemini()
    if APIKEY is None:
        return "failed", "failed", model
    STOPPED_BY_LENGTH = False
    # ** init


    limit_tokens = config.CONFIG['limit_tokens']
    if limit_tokens < 30000: # ;max_tokens
        max_tokens = limit_tokens
    else:
        max_tokens = 300
    TOKENSMIN = 1700
    if max_tokens < TOKENSMIN:
        max_tokens = TOKENSMIN
    #print(f"D... tokens {max_tokens}")

    system_prompt = texts.role_assistant
    #if role is None:
    #    system_prompt = texts.role_assistant
    newmsg = []

    for i in config.messages:
        newmsg.append( i )
    newmsg.append(  {"role": "user", "content": prompt} )

    if not dontadd:
        config.messages.append(  {"role": "user", "content": prompt} )

    #newmsg.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    limit_tokens = config.CONFIG['limit_tokens']
    # GEMINI HAS PROBLEM with limits
    #limit_tokens = 3500 + limit_tokens

    limit_tokens = limit_tokens + 2500 + int(sys.getsizeof(newmsg) / 2)# in bytes... tokens is always less.
    if config.DEBUG:
        #print("D... tokens in gemini: ", limit_tokens)
        print(fg.pink, newmsg, fg.default)


    res = ""
    # NATIVE GEMINI  API STYLE -------------------------------------------------------
    NATIVE = True
    if NATIVE:
        config.client = genai.Client(api_key=APIKEY)

        google_search_tool = Tool(
            google_search = GoogleSearch()
        )

        if config.gemini_chat is None:
            config.gemini_chat = config.client.chats.create(model=model)
            #print(f"i... creating a model /{model}/")
        #else:
            #print(f"i... gemini_chat is not NONE... having already a model /{model}/ and chat {config.gemini_chat}")


        response = config.gemini_chat.send_message(prompt, config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
        )

        #print(f"###RESPONSE### {response}")
        res = ""
        # Iterate through all candidates and parts like in gemini3_test.py
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if res:
                    res = f"{res}\n{part.text}"
                else:
                    res = part.text

        #res = response.text # chat..
        # response = client.models.generate_content(
        #     model=model,
        #     #contents=["How does AI work?"]
        #     contents=newmsg
        # )
        # #print(response.text)
        # res = response.text

    # else:# ----------------- NOT GOING HERE ----------------------------------
    #     # OPENAI _ API STYLE -------------------------------------------------------
    #     clientg = openai.OpenAI( api_key= APIKEY,
    #                       base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    #                      )

    #     #************ GO
    #     try:
    #         message = clientg.chat.completions.create(
    #             model=model,
    #             max_tokens=limit_tokens,
    #             temperature=temp,
    #             messages=newmsg
    #         )
    #     except Exception as e:
    #         print(fg.red, f"X... {e.message}", fg.default)
    #         return "Failed to answer", True

    #     # DONE ******
    #     if config.DEBUG: print(fg.cyan, message, fg.default)

    #     if message.choices is None:
    #         print(fg.red,"x... NO RESPONSE.... CHECK AVAILABLE TOKENS... ", fg.default)
    #         print(fg.dimgray, message, fg.default)
    #         return "Failed to answer", True
    #     response = message.choices[0].message

    #     #print(fg.lime, response, fg.default)
    #     res = response.content #[0].text #decode_response_anthropic(message.content)
    #     #print(fg.yellow, res, fg.default)
    # ================= HERE res contains the response content =====================  RES =====

    if not dontadd: # when big3 big4 used...
        if res is None:
            config.messages.append(  {"role": "assistant", "content": "<Internal error>"} )
        else:
            config.messages.append(  {"role": "assistant", "content": res} )

    if not config.silent:
        announce_model(model)
        #print("...",bg.green," >>OK", bg.default, f" model={model}") # gemini
    return res, STOPPED_BY_LENGTH, model
