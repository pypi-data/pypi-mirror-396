import requests
from IPython.display import display, Markdown, IFrame
import uuid
import os
from .. import utils
from . import utils as analyzer_utils


def create_mermaid_html(mermaid_code):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </body>
    </html>
    """
    return html_template
    
class MarkdownText:
    def __init__(self, text):
        self.text = text
    def display(self):
        display(Markdown(self.text))
    def __repr__(self):
        return f"MarkdownText {self.text[:50]}..."
    def __str__(self):
        return f"MarkdownText {self.text[:50]}..."
    
class Analyzer:
    def __init__(self, service_uri, api_key):
        """Init Analizer class

        Args:
            service_uri (str): services uri, eg : "https://training.services.storemesh.com"
            api_key (str): api key, eg : "Bq9EYgko.EBH64MH8LTxXzSPXU8NMKnguEZCHTUGl"
        """
        self._service_uri = service_uri
        self._header = {
            'Authorization': f'Api-Key {api_key}'
        }
        res = requests.get(f"{self._service_uri}/training/api/")
        utils.check_http_status_code(response=res, extra_text="Can not connect to service")
        os.makedirs('tmp', exist_ok=True)
    
    def list_district(self):
        """List districs

        Returns:
            List of distric
        """
        res = requests.get(f"{self._service_uri}/training/api/district/")
        utils.check_http_status_code(response=res)
        return res.json()

    def get_district(self, district_id):
        """get_district detail

        Args:
            district_id (str): distric id, can get from .list_district()

        Returns:
            MarkdownText: Markdown display, can call .display() for pretty print
        """
        res = requests.get(f"{self._service_uri}/training/api/district/{district_id}/")
        utils.check_http_status_code(response=res)
        return MarkdownText(res.json().get('context'))

    def prep_context(self, data):
        """
        prepair context

        Args:
            data (dict): has keys {'2.1', '2.2', '2.3', '2.4', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '6.1'}

        Returns:
            MarkdownText: Markdown display, can call .display() for pretty print
        """
        require_key = {'2.1', '2.2', '2.3', '2.4', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '6.1'}
        diff = require_key - set(data.keys())
        if diff!=set():
            raise Exception(f"Please input key {diff}")
        template = f"""

## Agritourism Activities
{data.get('2.1')}

## Locations
{data.get('2.2')}

## Crops and Product
{data.get('2.3')}

## Farmers and Producers
{data.get('2.4')}

## Tourists
{data.get('3.1')}

## Events and Festivals
{data.get('3.2')}

## Accommodations
{data.get('4.1')}

## Transportation
{data.get('4.2')}

## Local Cuisine
{data.get('5.1')}

## Cultural Practices
{data.get('5.2')}

## Vision (Inspiration) / Concept
{data.get('6.1')}
"""
        return MarkdownText(template)
    
    def context2article(self, context):
        if type(context)!= MarkdownText:
            raise Exception("`context` expect type `MarkdownText`")
        template = f"""
From this context markdown please create article in thai language

# Context
{context.text}
"""
        md_article = self.llm(prompt=template)
        return md_article
            
    def upload_context(self, context, district_id):
        """upload context to services

        Args:
            context (MarkdownText): MarkdownText from .prep_context()
            district_id (str): distric_id from .list_district()

        Raises:
            Exception: "Please input `context` type MarkdownText"
        Return:
            data: context_id and msg
        """
        if type(context) != MarkdownText:
            raise Exception("Please input `context` type MarkdownText")
        res = requests.post(
            f"{self._service_uri}/training/api/context/", headers=self._header,
            json={
                'context': context.text,
                'district': district_id
            }
       )
        utils.check_http_status_code(response=res)
        return res.json()
        
    def get_wizmap(self, version=-1):
        """get_wizmap to get wizmap vizualization
        Args:
            version (int): version wizmap -1 -> latest 0 -> oldest
        Return:
            Iframe display on notebook
        """
        res = requests.get(f"{self._service_uri}/training/api/wizmap/", headers=self._header)
        utils.check_http_status_code(response=res)
        versions = res.json()[::-1]
        v = versions[version]
        print(f"\twizmap {v}")
        res = requests.get(f"{self._service_uri}/training/api/wizmap/{v.get('id')}/", headers=self._header)
        utils.check_http_status_code(response=res)
        data = res.json()
        url = f"https://poloclub.github.io/wizmap/?dataURL={data.get('data').replace('http', 'https')}&gridURL={data.get('grid').replace('http', 'https')}"
        print(url)
        topic = "- "+"\n- ".join(data.get('topic'))
        template = f"""
# Topics

{topic}
"""
        display(Markdown(template))
        return IFrame(src=url, width='100%', height='600px')

    def rag(self, prompt):
        """RAG promt to return context from llm

        Args:
            prompt (str): LLM prompt

        Returns:
            MarkdownText: markdown context contain llm response
        """
        res = requests.post(f"{self._service_uri}/training/api/rag/", headers=self._header, json={'prompt': prompt})
        utils.check_http_status_code(response=res)
        return MarkdownText(res.json().get('response'))

    def list_rag(self):
        """list history of call LLM

        Returns:
            MarkdownText: markdown context contain llm response
        """
        res = requests.get(f"{self._service_uri}/training/api/rag/", headers=self._header)
        utils.check_http_status_code(response=res)
        return res.json()

    def get_rag(self, rag_id):
        """get RAG detail from history

        Args:
            rag_id (int): rag id from .list_rag()

        Returns:
            MarkdownText: markdown context contain llm response
        """
        res = requests.get(f"{self._service_uri}/training/api/rag/{rag_id}/", headers=self._header)
        utils.check_http_status_code(response=res)
        template = f"""
# Prompt
{res.json().get('prompt')}

# Result
{res.json().get('response')}
        """
        return MarkdownText(template)

    def create_mindmap(self, prompt, colab=False):
        """create mindmap using llm in mermaid syntax

        Args:
            prompt (str): LLM prmpt
            colab (bool, optional): if use in colab please set to `True`. Defaults to False.

        Returns:
            _type_: _description_
        """
        res = requests.post(f"{self._service_uri}/training/api/rag/mermaid/", headers=self._header, json={'prompt': prompt})
        utils.check_http_status_code(response=res)
        
        html_content = create_mermaid_html(res.json().get('response'))
        
        html_file = f"tmp/{uuid.uuid4().hex}.html"
        with open(html_file, "w") as file:
            file.write(html_content)
        if colab:
          from google.colab import files
          return files.download(html_file)
        return IFrame(src=html_file, width="100%", height=600)

    def llm(self, prompt):
        """LLM direct call

        Args:
            prompt (str): LLM prompt

        Returns:
             MarkdownText: markdown context contain llm response
        """
        res = requests.post(f"{self._service_uri}/training/api/rag/llm/", headers=self._header, json={'prompt': prompt})
        utils.check_http_status_code(response=res)
        return MarkdownText(res.json().get('response'))
    
    def list_template(self):
        return list(analyzer_utils.TEMPLATE.keys())
    
    def get_template(self, template_name):
        return analyzer_utils.TEMPLATE.get(template_name, [f"NotFound template {template_name}"])