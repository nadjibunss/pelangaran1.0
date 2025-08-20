from app import app

# Vercel membutuhkan handler function
def handler(event, context):
    return app(event, context)
