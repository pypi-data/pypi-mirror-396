import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

true = True
false = False
none = None

def rjson(file_or_CRU):
    try:
        with open(file_or_CRU, "r") as f:
            try:
                logging.info("Sucessfully read")
                return json.load(f)
            except json.JSONDecodeError:
                logging.error("Decodification error: Corrupted, incomplete or invalid JSON. Following...")
                return none
    except FileNotFoundError:
        try:
            logging.info("Sucessfully read")
            return json.loads(file_or_CRU)
        except json.JSONDecodeError:
            logging.error("Decodification error: Corrupted, incomplete or invalid JSON")
            return none
    except TypeError:
        logging.error("Invalid argument")
        return none
    except Exception as e:
        logging.error(f"Error: {e}")
        return none

def wjson(object, file=none):
    if file:
        try:
            with open(file, "w") as f:
                json.dump(object, f, indent=4)
            logging.info("Sucessfully written")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            return none
    else:
        try:
            return json.dumps(object)
        except TypeError as e:
            logging.error(f"Error: object is not JSON serializable: {e}")
            return none
        except Exception as e:
            logging.error(f"Error: {e}")
