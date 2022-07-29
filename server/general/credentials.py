from dataclasses import dataclass
import json

from pserialize.deserialize import default_deserializer

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
        return default_deserializer.deserialize(credentialsJson, Credentials)

def get_credentials() -> Credentials:
    try:
        return fromFile("credentials.json")
    except:
        return fromFile("../../credentials.json")