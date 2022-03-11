import json

class DMMLogAnalysis:
    def check(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                split = line.split(' > DMM session cookie. :: ')
                if len(split) == 2:
                    self.session = json.loads(split[1][:-2])
                    return True
            else:
                return False
