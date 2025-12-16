import os
import json

true = True
false = False
none = None

def ljson(arquivo_ou_CRU):
    try:
        with open(arquivo_ou_CRU, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Erro de decodificação: arquivo corrompido, incompleto ou não JSON. Continuando...")
                return none
    except FileNotFoundError:
        try:
            return json.loads(arquivo_ou_CRU)
        except json.JSONDecodeError:
            print("Erro de decodificação: código incompleto ou não JSON")
            return none
    except TypeError:
        print("O argumento não é válido")
        return none
    except Exception as e:
        print(f"Erro: {e}")
        return none

def ejson(objeto, arquivo=none):
    if arquivo:
        try:
            with open(os.path.abspath(arquivo), "w") as f:
                json.dump(objeto, f, indent=4)
            print("Escrito com sucesso")
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            return none
    else:
        try:
            return json.dumps(objeto)
        except TypeError as e:
            print(f"Erro: objeto não serializável: {e}")
            return none
