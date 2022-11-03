from dataclasses import dataclass
import json

from pserialize import deserialize

@dataclass
class Etherscan:
    apikey: str

@dataclass
class Infura:
    projectId: str
    projectSecret: str
    providerUrl: str

@dataclass
class Credentials:
    etherscan: Etherscan
    infura: Infura

def fromFile(credentialsPath: str) -> Credentials:
    with open(credentialsPath, "rb") as credentialsFile:
        credentialsJson = json.loads(credentialsFile.read())
        return deserialize(credentialsJson, Credentials)

def get_credentials() -> Credentials:
    try:
        return fromFile("credentials.json")
    except:
        return fromFile("../../credentials.json")