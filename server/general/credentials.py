import json

from db.dict_to_class import deserialize

class Etherscan(object):
    def __init__(self, apikey: str):
        self.apikey = apikey

class Infura(object):
    def __init__(self, projectId: str, projectSecret: str, providerUrl: str):
        self.projectId = projectId
        self.projectSecret = projectSecret
        self.providerUrl = providerUrl

class Credentials(object):
    def __init__(self, etherscan: Etherscan, infura: Infura):
            self.etherscan = etherscan
            self.infura = infura

def fromFile(credentialsPath: str) -> Credentials:
    with open(credentialsPath, "rb") as credentialsFile:
        credentialsJson = json.loads(credentialsFile.read())
        return deserialize(credentialsJson, Credentials)

def get_credentials() -> Credentials:
    try:
        return fromFile("credentials.json")
    except:
        return fromFile("../../credentials.json")