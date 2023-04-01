import base64

BUFFER = """{
    "UID": {},
    "CLIENTID": "bc861f85ca7341aba632503a2adb1d8c",
    "CLIENTSECRET": "d2e0d307afb8446ea057abfaaceea252",
    "REFRESHTOKEN": "AQC17gNf8hUbDSRy4OJsmVNkpXAJWNE59Bf7mRx0fvNhCr_HHtrCWihZpqwuNJSDG00fNPuaEKda4lcsdyhADBXFnvG9sQQPpJ4WvqwAJDtNgbaW2DoNno3SLSNdYrI7Qss",
    "ACCESSTOKEN": "BQD6h4yNWXF9AkmXyr_PQhYRNKdP24ba1zl_n1kjTRt76vLwF6g3kM9YwRdimWRhnVQa531yhtEOvA0Qr4gbeIDtuW2SIXEohB6ri9_Xgr7s3NrgE26v0k6wT6Nw7vrHzHLuHJpL9NNmUr-Dv9TS8_RBsy5JsmC9EFzjzUPXB9uv7W83SjtB-NP_hrZQm5DSe35KoNR0xzmlOI3YiUniRZizW8c6_jSGlI2TLyh2S_uZr9lQYF8OmlDulPGjjq2HewBtLjGPwZ_MjFW_"
}"""


from scripts.static import SECRET_FILE

with open(SECRET_FILE, "w") as file:
    encodeded = base64.b64encode(BUFFER.encode("ascii")).decode("ascii")
    file.write(encodeded)
