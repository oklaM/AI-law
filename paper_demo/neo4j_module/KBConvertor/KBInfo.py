class KBInfo:
    def __init__(self, subject, predicate, obj, predicate_id, rule_str):
        self.subject = subject
        self.predicate = predicate
        self.object = obj
        self.predicate_id = predicate_id
        self.rule = rule_str

    def to_dict(self):
        result = dict()
        result["subject"] = self.subject
        result["predicate"] = self.predicate
        result["object"] = self.object
        result["predicateID"] = self.predicate_id
        result["rule"] = self.rule
        return result
