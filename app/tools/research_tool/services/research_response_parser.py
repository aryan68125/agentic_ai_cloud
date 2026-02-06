import re

class ResearchTagParser:
    @staticmethod
    def parse(text: str) -> list[dict]:
        items = []

        # hard-strip any reasoning noise
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        research_block = re.search(
            r"<<RESEARCH_RESULTS>>(.*?)<<END_RESEARCH_RESULTS>>",
            text,
            re.DOTALL
        )

        if not research_block:
            return []

        for item in re.finditer(
            r"<<ITEM>>(.*?)<<END_ITEM>>",
            research_block.group(1),
            re.DOTALL
        ):
            answer = re.search(r"<<ANSWER>>(.*?)<<END_ANSWER>>", item.group(1), re.DOTALL)
            source = re.search(r"<<SOURCE>>(.*?)<<END_SOURCE>>", item.group(1), re.DOTALL)

            if not answer or not source:
                continue

            items.append({
                "answer": answer.group(1).strip(),
                "source": source.group(1).strip()
            })

        return items
