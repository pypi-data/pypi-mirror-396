import base64
import io
import logging
import os
import re
from enum import Enum
from functools import lru_cache
from typing import List, cast, Type

import pymupdf
import requests
from filetype import filetype
from pydantic import Field, BaseModel
from pylatexenc.latex2text import latex2text
from pylatexenc.latexwalker import LatexWalkerError
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document, Boundary, AltText
from starlette.datastructures import UploadFile

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)
DEFAULT_MISTRAL_URL = "https://api.mistral.ai/v1/"
MISTRAL_URL = os.getenv(
    "MISTRAL_URL", DEFAULT_MISTRAL_URL
)

logger = logging.getLogger("pymultirole")


class MistralOCRModel(str, Enum):
    mistral_ocr_latest = "mistral-ocr-latest"


class MistralOCRParameters(ConverterParameters):
    model_str: str = Field(
        None, extra="advanced"
    )
    model: MistralOCRModel = Field(
        MistralOCRModel.mistral_ocr_latest,
        description="""Latest Mistral OCR [model](https://docs.mistral.ai/capabilities/document/)"""
    )
    segment: bool = Field(
        False,
        extra="internal"
    )
    level_to_split_on: int = Field(
        -1,
        extra="internal"
    )
    max_pages_split: int = Field(
        -1,
        description="""To split a large PDF file into files of no more than max pages""",
        extra="advanced"
    )
    latex_to_text: bool = Field(
        True,
        description="""Convert LaTeX codes to plain text with unicode characters"""
    )
    include_image_base64_as_links: bool = Field(
        False, extra="advanced",
        description="""To include the image data as base64 links `![img-0.jpeg](data:image/jpeg;base64,`"""
    )
    include_image_base64_as_altTexts: bool = Field(
        False, extra="advanced",
        description="""To include the image data as base64 altTexts"""
    )


class MistralOCRConverter(ConverterBase):
    """MistralOCR PDF converter ."""

    def convert(
            self, source: UploadFile, parameters: ConverterParameters
    ) -> List[Document]:
        params: MistralOCRParameters = cast(MistralOCRParameters, parameters)
        model_str = params.model_str if bool(params.model_str and params.model_str.strip()) else None
        model = params.model.value if params.model is not None else None
        params.model_str = model_str or model
        client = get_client(MISTRAL_URL)
        docs = []
        doc = client.split_and_convert(source, params)
        docs.append(doc)
        return docs

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return MistralOCRParameters


@lru_cache(maxsize=None)
def get_client(base_url):
    client = MistralClient(base_url)
    return client


def guess_kind(base64_src):
    kind = None
    img_regex = r"data:(image/[^;]+);base64"
    matches = re.search(img_regex, base64_src)
    if matches:
        mime = matches.group(1)
        kind = filetype.get_type(mime)
    return kind


class MistralClient:
    def __init__(self, base_url):
        self.base_url = base_url[0:-1] if base_url.endswith("/") else base_url
        self.use_base64 = self.base_url != DEFAULT_MISTRAL_URL
        self.dsession = requests.Session()
        self.dsession.headers.update({
            'Authorization': f"Bearer {MISTRAL_API_KEY}",
            'Accept': 'application/json',
            'user-agent': "speakeasy-sdk/python 1.2.6 2.486.1 0.0.2 mistralai_azure"
        })
        self.dsession.verify = False

    def upload(self, source: UploadFile):
        file_url = None
        try:
            payload = {'file': (source.filename, source.file, 'application/pdf')}
            resp = self.dsession.post(
                f"{self.base_url}/files",
                files=payload,
                data={'purpose': "ocr"},
            )
            if resp.ok:
                result = resp.json()
                file_id = result["id"]
                resp = self.dsession.get(
                    f"{self.base_url}/files/{file_id}/url",
                    params={'expiry': 1},
                    headers={'Accept': 'application/json'},
                )
                if resp.ok:
                    result = resp.json()
                    file_url = result['url']
                else:
                    logger.warning(f"Unsuccessful file upload: {source.filename}")
                    resp.raise_for_status()
            else:
                logger.warning(f"Unsuccessful file upload: {source.filename}")
                resp.raise_for_status()
        except BaseException as err:
            logger.warning("An exception was thrown!", exc_info=True)
            raise err
        return file_url

    def split_and_convert(self, source: UploadFile, params: MistralOCRParameters):
        docs = {}
        max_pages = params.max_pages_split

        if max_pages > 0:
            pdfdoc = pymupdf.open(source.file)
            total_pages = pdfdoc.page_count
            for start in range(0, total_pages, max_pages):
                end = min(start + max_pages, total_pages)
                pdfpart = pymupdf.open()  # nouveau PDF
                for page_num in range(start, end):
                    pdfpart.insert_pdf(pdfdoc, from_page=page_num, to_page=page_num)
                partbytes = pdfpart.tobytes()
                partfile = UploadFile(filename=source.filename, file=io.BytesIO(partbytes))
                doc = self.convert(partfile, start, params)
                docs[start] = (doc)
                pdfpart.close()
            pdfdoc.close()
        else:
            docs[0] = self.convert(source, 0, params)

        consolidated = docs.pop(0)
        for start, doc in docs.items():
            offset = len(doc.text)
            consolidated.text += doc.text
            consolidated.altTexts.extend(doc.altTexts)
            consolidated.boundaries['page'].extend([Boundary(start=b.start + offset, end=b.end + offset) for b in doc.boundaries['page']])
        return consolidated

    def convert(self, source: UploadFile, part: int, params: MistralOCRParameters):
        doc = None
        altTexts = []
        latex_regex = r"(\$[^\$]+\$)"
        link_regex = r"\[([^]]+)\]\(([^]]+)\)"

        try:
            file_url = None
            if self.use_base64:
                data = source.file.read()
                rv = base64.b64encode(data)
                file_url = f"data:application/pdf;base64,{rv.decode('utf-8')}"
            else:
                file_url = self.upload(source)
            if file_url is not None:
                resp = self.dsession.post(
                    f"{self.base_url}/ocr",
                    json={
                        'model': params.model_str,
                        'include_image_base64': params.include_image_base64_as_links or params.include_image_base64_as_altTexts,
                        'document': {
                            'type': 'document_url',
                            'document_url': file_url
                        }},
                    headers={'content-type': 'application/json'},
                )
                if resp.ok:
                    result = resp.json()
                    pages = []
                    start = 0
                    text = ""
                    title = None
                    for pi, page in enumerate(result['pages']):
                        markdown = page['markdown']
                        images = {im['id']: im['image_base64'] for im in page['images'] if im['image_base64'] is not None}
                        if pi == 0:
                            if markdown.startswith("# ") and "\n" in markdown:
                                firstline = markdown.split('\n', 1)[0]
                                title = firstline[2:]

                        def convert_latex(matchobj):
                            m = matchobj.group(0)
                            try:
                                return latex2text(m)
                            except LatexWalkerError:
                                # logger.warning("An exception was thrown during lateX conversion!", exc_info=True)
                                return m

                        ptext = re.sub(latex_regex, convert_latex, page['markdown'], 0, re.MULTILINE) if params.latex_to_text else page['markdown']

                        def convert_links(matchobj):
                            m = matchobj.group(0)
                            m_id = matchobj.group(1)
                            m_data = matchobj.group(2)
                            link = m
                            if m_id in images:
                                img_id = f"{part}/{m_id}"
                                m_url = images[m_id]
                                kind = guess_kind(m_url)
                                if kind is not None and kind.mime.startswith("image"):
                                    if params.include_image_base64_as_altTexts:
                                        altTexts.append(AltText(name=img_id, text=m_url, properties={'mime-type': kind.mime}))
                                        link = f"[{img_id}]({m_data})"
                                    if params.include_image_base64_as_links:
                                        link = f"[{img_id}]({images[m_id]})"
                            return link
                        if params.include_image_base64_as_altTexts or params.include_image_base64_as_links:
                            ptext = re.sub(link_regex, convert_links, ptext, 0,
                                           re.MULTILINE) if params.latex_to_text else page['markdown']
                        text += ptext + '\n'
                        pages.append(Boundary(start=start, end=len(text)))
                        start = len(text)
                    doc = Document(identifier=source.filename, title=title or source.filename, text=text,
                                   altTexts=altTexts,
                                   boundaries={'page': pages},
                                   metadata={'original': source.filename, 'mime-type': 'text/markdown'})
                else:
                    logger.warning(f"Unsuccessful OCR conversion: {source.filename}")
                    resp.raise_for_status()
        except BaseException as err:
            logger.warning("An exception was thrown!", exc_info=True)
            raise err
        return doc
