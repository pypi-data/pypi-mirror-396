from typing import List
from pathlib import Path
from langchain_core.documents import Document
import csv

class DocumentLoader:
    #base class for all loaders
    def __init__(self):
        #how many docs loaded
        self.count =0  

    def load(self, paths: List[str]) -> List[Document]:
        #subclass must override
        raise NotImplementedError

    def _ext_ok(self, p: str, ext: str) -> bool:
        #check ext
        try:
            return p.lower().endswith(ext)
        except AttributeError:
            #p is not a string
            raise TypeError("path must be a string")

    def _add(self, n: int):
        #update count
        try:
            self.count += n
        except TypeError:
            raise ValueError("count must be an int")


class PDFLoader(DocumentLoader):
    #load pdf files
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        try:
            from pypdf import PdfReader
        except ImportError:
            #keep the old behaviour
            raise ImportError("need pypdf")
        except Exception as ex:
            #unexpected import problem
            raise RuntimeError(f"failed to import pypdf: {ex}") from ex

        for p in paths:
            if not self._ext_ok(p, ".pdf"):
                continue

            try:
                reader = PdfReader(p)
            except FileNotFoundError:
                raise FileNotFoundError(f"file not found: {p}")
            except Exception as ex:
                #pdf file exists but cannot be opened/read
                raise RuntimeError(f"failed to open pdf: {p}") from ex

            buf = []

            #read pages
            for pg in reader.pages:
                try:
                    txt = pg.extract_text() or ""
                except Exception:
                    #if a single page fails, skip its text but keep going
                    txt = ""
                buf.append(txt)

            all_txt = "\n".join(buf).strip()

            if all_txt:
                d = Document(
                    page_content=all_txt,
                    metadata={
                        "name": Path(p).name,
                        "path": p,
                        "type": "pdf"
                    }
                )
                out.append(d)

        self._add(len(out))
        return out

    def summary(self):
        #just show count
        return f"pdf: {self.count}"

    def reset(self):
        #reset counter
        self.count = 0


class TXTLoader(DocumentLoader):
    #load txt files
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        for p in paths:
            if not self._ext_ok(p, ".txt"):
                continue

            try:
                with open(p, encoding="utf-8") as f:
                    txt = f.read().strip()
            except FileNotFoundError:
                raise FileNotFoundError(f"file not found: {p}")
            except UnicodeDecodeError as ex:
                #file is not valid utf-8 text
                raise UnicodeDecodeError(ex.encoding, ex.object, ex.start, ex.end, "cannot decode txt file") from ex
            except Exception as ex:
                raise RuntimeError(f"failed to read txt file: {p}") from ex

            d = Document(
                page_content=txt,
                metadata={
                    "name": Path(p).name,
                    "path": p,
                    "type": "txt"
                }
            )
            out.append(d)

        self._add(len(out))
        return out

    def summary(self):
        return f"txt: {self.count}"

    def reset(self):
        self.count = 0


class CSVLoader(DocumentLoader):
    #load csv rows
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        for p in paths:
            if not self._ext_ok(p, ".csv"):
                continue

            try:
                with open(p, encoding="utf-8", newline="") as f:
                    r = csv.DictReader(f)
                    for i, row in enumerate(r):
                        line = ", ".join(f"{k}={v}" for k, v in row.items())
                        d = Document(
                            page_content=line,
                            metadata={
                                "name": Path(p).name,
                                "path": p,
                                "row": i,
                                "type": "csv"
                            }
                        )
                        out.append(d)
            except FileNotFoundError:
                raise FileNotFoundError(f"file not found: {p}")
            except csv.Error as ex:
                #bad csv format
                raise csv.Error(f"csv parse error in {p}: {ex}") from ex
            except Exception as ex:
                raise RuntimeError(f"failed to read csv file: {p}") from ex

        self._add(len(out))
        return out

    def summary(self):
        return f"csv rows: {self.count}"

    def reset(self):
        self.count = 0