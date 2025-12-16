from typing import List
from langchain_core.documents import Document

class TextChunker:
    #split long text into smaller chunks
    def __init__(self, chunk_size=1000, overlap=200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if overlap < 0:
            raise ValueError("overlap must be >= 0")
        if overlap >= chunk_size:
            #avoid infinite loop when moving start = end - overlap
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_docs(self, docs: List[Document]) -> List[Document]:
        #loop docs
        if not isinstance(docs, list):
            raise TypeError("docs must be a list of Document")
        result = []
        for d in docs:
            parts = self.chunk_one(d)
            result.extend(parts)
        return result

    def chunk_one(self, doc: Document) -> List[Document]:
        #split one doc
        if not isinstance(doc, Document):
            raise TypeError("doc must be a Document")
        t = doc.page_content
        if not isinstance(t, str):
            raise TypeError("page_content must be a string")

        res = []
        start = 0

        while start < len(t):
            end = start + self.chunk_size
            piece = t[start:end]

            meta2 = dict(doc.metadata)
            meta2["chunk"] = len(res)

            new_doc = Document(
                page_content=piece,
                metadata=meta2
            )
            res.append(new_doc)

            #protect against bad settings during runtime
            if self.overlap >= self.chunk_size:
                raise ValueError("overlap must stay smaller than chunk_size")
            start = end - self.overlap

        return res

    def set_size(self, s: int):
        #change chunk size
        if s <= 0:
            raise ValueError("chunk_size must be > 0")
        self.chunk_size = s