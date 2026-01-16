# Playwright
`playwright install`
`sudo playwright install-deps` if it fails, try
`playwright install-deps`

# LibreOffice for DOCX to PDF conversions:
```   # Ubuntu/Debian
   sudo apt-get install libreoffice
   
   # macOS
   brew install libreoffice```
   
# To autogenerate migrations using alembic:
`alembic revision --autogenerate -m "<WRITE MIGRATION DESCRIPTION HERE>"`

# To apply the migrations:
`alembic upgrade head`