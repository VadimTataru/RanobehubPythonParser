from src.Novel import Novel


class NovelChapter:

    def __init__(self, title_rus: str, source_link: str, next_source_link: str, content: str, volume: str,
                 novel_id: int):
        self.title_rus = title_rus
        self.source_link = source_link
        self.next_source_link = next_source_link
        self.content = content
        self.volume = volume
        self.novel_id = novel_id

    def to_str(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}\n{6}\n".format(self.title_rus, self.source_link, self.next_source_link, self.content, self.volume, self.novel_id)
