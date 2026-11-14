"""
Secret Format
SHA Key: Random Number (8) + Key
Context for Encryption: Key + Context
Encryption Mode:
 - SHA-256 the Key as the Vigenère Cipher
 - Huffman Code Compression

Decryption Mode:
 - Huffman Code Decompression
 - Decode the Key and find the Context that starts with Key, and remove Key
"""

import hashlib
import random
from typing import List, Dict

def getHashedstring(key: str) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(key.encode('utf-8'))  # Ensure to encode to bytes

    # Get the hexadecimal digest (the final hash)
    hashedString: str = sha256_hash.hexdigest()
    return hashedString

def vigenereCipher(inputString: str, key: str, mode: bool=True) -> str:
    """
    Encrypts or decrypts a string using the Vigenère cipher.
    If used for decryption, the key will shift characters in the opposite direction.
    """
    keyLength = len(key)
    keyInts = [int(char, 16) for char in key]
    specialSymbols = [
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', 
    '-', '_', '=', '+', '[', ']', '{', '}', '\\', '|', 
    ';', ':', "\'", '\"', ',', '.', '/', '<', '>', '?', 
    '~', '`', ' ',]
    
    resultString = []
    for i, char in enumerate(inputString):
        shift = keyInts[i % keyLength]
        
        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            if mode == False:  # If we are decrypting, we reverse the shift
                newChar = chr(start + (ord(char) - start - shift) % 26)  # Reverse shift
            else:  # Otherwise, we encrypt normally
                newChar = chr(start + (ord(char) - start + shift) % 26)
            
            resultString.append(newChar)

        elif char in specialSymbols:
            length: int = len(specialSymbols)
            if mode == False:
                newChar = specialSymbols[((specialSymbols.index(char) - shift) % length + length) % length]
            else:
                newChar = specialSymbols[(specialSymbols.index(char) + shift) % length]
        
            resultString.append(newChar)

        else:
            resultString.append(char)

    return ''.join(resultString)

def encryptSecret(inputString: str, hashedString: str) -> str:
    encodedText: str = vigenereCipher(inputString, hashedString, True)

    return encodedText

def decryptSecret(secret: str, hashedString: str) -> str:
    decodedText: str = vigenereCipher(secret, hashedString, False)
    return decodedText
    

while True:
    print("Please enter your comand:")
    print("(1) Create Encoded Text")
    print("(2) Decode Encoded Text")
    print("(3) Modify Encoded Text")
    print("(4) Exit")
    command: int = int(input())
    if command == 1:
        secrets: str = input()
        with open(f"{secrets}.txt", 'w') as f:
            print("Please choose a way to encode your Secrets:")
            print("(1) Through Console")
            print("(2) Through Text File")
            print("(3) Through Markdown File")
            command: int = int(input())
            if command == 1:
                print("Please enter your Key:")
                key: str = input()
                while True:
                    print("Please enter your Secret:")
                    secret: str = input()
                    # Generate a random 8-digit number
                    randomNumber = str(random.randint(10000000, 99999999))
                    hashedString: str = getHashedstring(randomNumber + key)
                    encrypted: str = encryptSecret(key + secret, hashedString)
                    f.write(randomNumber + encrypted + "\n")
                    print("Do you want to continue with the same Key?")
                    print("(1) Yes")
                    print("(2) No")
                    command: int = int(input())
                    if command == 2:
                        break

    elif command == 2:
        # encodedText: str = input("Please enter your Secrets:\n")
        encodedText: str = "Secrets.txt"
        with open(encodedText, 'r') as f:
            resultedString = {}
            while True:
                f.seek(0)
                print("Please enter the key of the Secrets:")
                key: str = input()
                
                resultedList = list()
                for line in f:
                    hashedString: str = getHashedstring(line[:8] + key)
                    decrypted: str = decryptSecret(line[8:], hashedString)
                    if decrypted.startswith(key):
                        decrypted = decrypted[len(key):]
                        decrypted = decrypted.rstrip('\n')
                        resultedList.append(decrypted)

                resultedList.sort(key=lambda x: x.lower())
                resultedString[key] = resultedList
                print("Do you want to continue decoding Keys?")
                print("(1) Yes")
                print("(2) No")
                command: int = int(input())
                if command == 2:
                    break

            print("Please choose a way to show your decoded Secrets:")
            print("(1) Through Console")
            print("(2) Through Text File")
            print("(3) Through Markdown File")
            command: int = int(input())
            if command == 1:
                print("====================================================")
                print("Below are the Secrets encoded with the entered Key:\n")
                print("====================================================")
                for key, results in resultedString.items():
                    if len(results) == 0:
                        continue

                    print(f"# {key}")
                    for num, result in enumerate(results):
                        print(f"{num + 1}. {result}")

                    print()
                
                print(("\n====================================================\n"))

            elif command == 2:
                with open("decodedSecrets.txt", 'w') as f:
                    for key, results in resultedString.items():
                        if len(results) == 0:
                            continue

                        f.write(f"{key}\n")
                        for num, result in enumerate(results):
                            f.write(f"{num + 1}. {result}\n")

                        f.write(f"\n")
                        

            elif command == 3:
                with open("decodedSecrets.md", 'w') as f:
                    for key, results in resultedString.items():
                        if len(results) == 0:
                            continue

                        f.write(f"# {key}\n")
                        for num, result in enumerate(results):
                            f.write(f"{num + 1}. {result}\n")

                        f.write(f"\n")
                        

    elif command == 3:
        # encodedText: str = input("Please enter your Secrets:\n")
        encodedText: str = "Secrets.txt"
        while True:
            print("How do you want to modify your Secrets:")
            print("(1) Add Secrets")
            print("(2) Remove Secrets")
            print()
            print("(0) Back")
            command: int = int(input())
            if command == 1:
                with open(encodedText, 'a') as f:
                    print("Please enter your Key:")
                    key: str = input()
                    while True:
                        print("Please enter your Secret:")
                        secret: str = input()
                        # Generate a random 8-digit number
                        randomNumber = str(random.randint(10000000, 99999999))
                        hashedString: str = getHashedstring(randomNumber + key)
                        encrypted: str = encryptSecret(key + secret, hashedString)
                        f.write(randomNumber + encrypted + "\n")
                        print("Do you want to continue with the same Key?")
                        print("(1) Yes")
                        print("(2) No")
                        command: int = int(input())
                        while command not in [1, 2]:
                            print("Please enter valid command.\n")
                            print("Do you want to continue removing Secret with the same key?")
                            print("(1) Yes")
                            print("(2) No")
                            command: int = int(input())

                        if command == 2:
                            break
                    
            
            elif command == 2:
                with open(encodedText, 'r') as f:
                    print("Please enter the key of the Secrets:")
                    key: str = input()
                    secretsList: List[str] = list()
                    resultedList: Dict[str, str] = dict()
                    for line in f:
                        hashedString: str = getHashedstring(line[:8] + key)
                        decrypted: str = decryptSecret(line[8:], hashedString)
                        if decrypted.startswith(key):
                            decrypted = decrypted.lstrip(key)
                            decrypted = decrypted.rstrip('\n')
                            resultedList[decrypted] = line

                        else:
                            secretsList.append(line)

                    for num, result in enumerate(resultedList.keys()):
                        print(f"{num + 1}. {result}")

                    removeList: List[int] = list()
                    print("\nPlease choose the Secret you want to remove.")
                    while True:
                        secretRemoved: int = int(input())
                        removeList.append(list(resultedList.keys())[secretRemoved - 1])
                        print("Do you want to continue removing Secret with the same key?")
                        print("(1) Yes")
                        print("(2) No")
                        command: int = int(input())
                        while command not in [1, 2]:
                            print("Please enter valid command.\n")
                            print("Do you want to continue removing Secret with the same key?")
                            print("(1) Yes")
                            print("(2) No")
                            command: int = int(input())

                        if command == 2:
                            break
                
                    for decoded, secret in resultedList.items():
                        if decoded in removeList:
                            continue

                        else:
                            secretsList.append(secret)

                with open(encodedText, 'w') as f:
                    for secret in secretsList:
                        f.write(secret)

            elif command == 0:
                break

            else:
                print("Please enter valid command.")
                

    elif command == 4:
        print("Exiting...")
        break


