from src.Novel import Novel


class NovelChapter:

    def __init__(self, title_rus: str, source_link: str, next_source_link: str, content: str, volume: str, novel: Novel):
        self.title_rus = title_rus
        self.source_link = source_link
        self.next_source_link = next_source_link
        self.content = content
        self.volume = volume
        self.novel = novel
