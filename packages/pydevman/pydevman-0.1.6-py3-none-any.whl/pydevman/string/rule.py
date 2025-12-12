from pydantic import BaseModel

from pydevman.common.sorted_key_dict import SortedKeyDict
from pydevman.string.match import MatchStrategy, match_by_strategy


class Rule(BaseModel):
    name: str
    strategy: MatchStrategy
    patterns: list[str]
    priority: int = 0

    def match(self, text: str) -> bool:
        try:
            for pattern in self.patterns:
                if match_by_strategy(pattern, text, self.strategy):
                    return True
            return False
        except TypeError:
            return False
        except Exception as e:
            raise e


class RuleEngine:
    def __init__(self):
        self.rules = SortedKeyDict()

    def register(self, rule: Rule):
        priority = rule.priority
        li: list = self.rules.get(priority)
        if li is None:
            self.rules[priority] = [rule]
        else:
            self.rules[priority].append(rule)

    def match(self, text: str) -> list[Rule]:
        """返回匹配的规则列表"""
        for _, li in self.rules:
            li: list[Rule]
            matched = False
            matched_list = []
            for rule in li:
                if rule.match(text):
                    matched = True
                    matched_list.append(rule)
            if matched:
                return matched_list
        return matched_list
