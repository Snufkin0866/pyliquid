# pyliquid

## Description

This is the python api wrapper for liquid crypto currency exchange.
https://app.liquid.com/

Pyliquid is based on pyquoinex written by kapipara.(Twitter: @kapipara180)
The author editted the wrapper to make it available for HFT, so that it doesn't
cause errors when you send more than 1 request in every second. And the author
added some other functions.
Take care not to send too many requests, or you will be banned by the exchange.
Thank you kapipara!

https://note.mu/kapipara180/n/n020f6b2a4037

## Usage

It requires the library 'PyJWT'. Make sure that the library is different from 
'jwt'.

```
pip install PyJWT
```
You can initialize the api wrapper by next code.

```
import pyliquid
api = pyliquid.API(key, secret)
```

