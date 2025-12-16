"""Document chunking utilities."""

import re
from dataclasses import dataclass
from typing import List

MAX_CHUNK_SIZE = 12000  # bytes


@dataclass
class Chunk:
    """A chunk of document content."""
    content: str
    index: int


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for clean storage."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text.strip()


def split_into_paragraphs(content: str) -> List[str]:
    """Split content into paragraphs."""
    paragraphs = re.split(r'\n\s*\n', content)
    return [p.strip() for p in paragraphs if p.strip()]


def split_at_bytes(text: str, max_size: int) -> List[str]:
    """Split text at byte boundaries, respecting UTF-8."""
    chunks = []
    current = []
    current_size = 0

    for char in text:
        char_size = len(char.encode('utf-8'))
        if current_size + char_size > max_size and current:
            chunks.append(''.join(current))
            current = []
            current_size = 0
        current.append(char)
        current_size += char_size

    if current:
        chunks.append(''.join(current))
    return chunks


def split_large_paragraph(para: str, max_size: int) -> List[str]:
    """Split a paragraph that's too large."""
    sentences = re.split(r'(?<=[.!?])\s+', para)
    chunks = []
    current = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence.encode('utf-8'))

        if current_size + sentence_size > max_size and current:
            chunks.append(' '.join(current))
            current = []
            current_size = 0

        if sentence_size > max_size:
            words = sentence.split()
            if len(words) > 1:
                word_chunk = []
                word_size = 0
                for word in words:
                    ws = len(word.encode('utf-8')) + 1
                    if word_size + ws > max_size and word_chunk:
                        chunks.append(' '.join(word_chunk))
                        word_chunk = []
                        word_size = 0
                    if ws > max_size:
                        if word_chunk:
                            chunks.append(' '.join(word_chunk))
                            word_chunk = []
                            word_size = 0
                        chunks.extend(split_at_bytes(word, max_size))
                    else:
                        word_chunk.append(word)
                        word_size += ws
                if word_chunk:
                    current.extend(word_chunk)
                    current_size += word_size
            else:
                if current:
                    chunks.append(' '.join(current))
                    current = []
                    current_size = 0
                chunks.extend(split_at_bytes(sentence, max_size))
        else:
            current.append(sentence)
            current_size += sentence_size + 1

    if current:
        chunks.append(' '.join(current))

    return [c for c in chunks if c.strip()]


def chunk_document(content: str, max_size: int = MAX_CHUNK_SIZE) -> List[Chunk]:
    """Split document into chunks respecting paragraph boundaries."""
    content = normalize_whitespace(content)

    if len(content.encode('utf-8')) <= max_size:
        return [Chunk(content=content, index=0)]

    paragraphs = split_into_paragraphs(content)
    chunks = []
    current_paras = []
    current_size = 0

    for i, para in enumerate(paragraphs):
        para_size = len(para.encode('utf-8')) + 2

        if current_size + para_size > max_size and current_paras:
            chunk_content = '\n\n'.join(current_paras)
            chunks.append(Chunk(content=chunk_content, index=len(chunks)))
            current_paras = []
            current_size = 0

        if para_size > max_size:
            sub_paras = split_large_paragraph(para, max_size - 100)
            for sub in sub_paras:
                if current_paras:
                    chunk_content = '\n\n'.join(current_paras)
                    chunks.append(Chunk(content=chunk_content, index=len(chunks)))
                    current_paras = []
                    current_size = 0
                chunks.append(Chunk(content=sub, index=len(chunks)))
        else:
            current_paras.append(para)
            current_size += para_size

    if current_paras:
        chunk_content = '\n\n'.join(current_paras)
        chunks.append(Chunk(content=chunk_content, index=len(chunks)))

    return chunks
