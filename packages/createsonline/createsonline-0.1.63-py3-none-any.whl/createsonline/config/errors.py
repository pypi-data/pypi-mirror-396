"""
CREATESONLINE Error Handling

Error handling and error page generation.
"""
from typing import Tuple


class HTTPException(Exception):
    """HTTP exception with status code and detail message"""
    
    def __init__(self, status_code: int, detail: str = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ErrorPageGenerator:
    """Generate error pages for HTTP errors"""
    
    @staticmethod
    def generate_error_page(
        status_code: int,
        error_message: str,
        path: str = "",
        method: str = "GET",
        details: str = ""
    ) -> str:
        """Generate error page HTML"""
        status_text = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }.get(status_code, "Error")
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{status_code} {status_text} - CREATESONLINE</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .error-container {{
            text-align: center;
            max-width: 600px;
        }}
        
        .error-code {{
            font-size: 8rem;
            font-weight: 900;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #ef4444, #f59e0b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .error-title {{
            font-size: 2rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }}
        
        .error-message {{
            font-size: 1.125rem;
            color: #d1d5db;
            margin-bottom: 2rem;
        }}
        
        .error-details {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            text-align: left;
            font-family: 'Monaco', monospace;
            font-size: 0.875rem;
        }}
        
        .detail-row {{
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .detail-label {{
            color: #6366f1;
            font-weight: 600;
        }}
        
        .detail-value {{
            color: #d1d5db;
            word-break: break-all;
        }}
        
        .back-link {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #6366f1;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{
            background: #4f46e5;
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">{status_code}</div>
        <h1 class="error-title">{status_text}</h1>
        <p class="error-message">{error_message}</p>
        
        <div class="error-details">
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value">{status_code} {status_text}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Method:</span>
                <span class="detail-value">{method}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Path:</span>
                <span class="detail-value">{path}</span>
            </div>
            {f'<div class="detail-row"><span class="detail-label">Details:</span><span class="detail-value">{details}</span></div>' if details else ''}
        </div>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
"""
        return html
