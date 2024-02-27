from fuzzywuzzy import process


def fuzz(raw: str,keyboard: str):
    return process.fuzz.token_set_ratio(raw,keyboard)

def fuzzsort(rawlist,keyboard: str):
    return process.extract(keyboard,rawlist,limit=len(rawlist))

if __name__ == "__main__":
    print(fuzz("hello world","world"))
    strfuzz = ["hel","llo","worl","world"]
    for value in fuzzsort(strfuzz,"o"):
        print(value)
