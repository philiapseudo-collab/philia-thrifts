"""Simple HTML page with seed button for easy database seeding."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["seed"])

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Philia Thrifts - Database Seeding</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 50px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: bold;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        .status.loading {
            background: #fff3cd;
            color: #856404;
            display: block;
        }
        .inventory-count {
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ Philia Thrifts</h1>
        <p class="subtitle">Database Seeding Tool</p>
        
        <button class="btn" id="seedBtn" onclick="runSeed()">
            🌱 Seed Database (40 Items)
        </button>
        
        <button class="btn" id="clearBtn" onclick="clearInventory()" style="margin-top: 10px; background: #dc3545;">
            🗑️ Clear Inventory
        </button>
        
        <div id="status" class="status"></div>
        
        <div class="inventory-count" id="inventoryCount"></div>
    </div>

    <script>
        async function runSeed() {
            const btn = document.getElementById('seedBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            status.className = 'status loading';
            status.innerHTML = '<span class="spinner"></span> Seeding database... This may take 10-20 seconds';
            
            try {
                const response = await fetch('/admin/seed-now', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    status.className = 'status success';
                    status.innerHTML = '✅ ' + data.message + '<br>Budget: ' + data.budget + ', Mid-Range: ' + data.mid_range + ', Premium: ' + data.premium;
                } else {
                    status.className = 'status error';
                    status.innerHTML = '❌ Error: ' + data.message;
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = '❌ Network error: ' + error.message;
            } finally {
                btn.disabled = false;
            }
        }
        
        async function clearInventory() {
            if (!confirm('Are you sure you want to clear all inventory?')) return;
            
            const btn = document.getElementById('clearBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            status.className = 'status loading';
            status.innerHTML = '<span class="spinner"></span> Clearing inventory...';
            
            try {
                const response = await fetch('/admin/clear-now', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    status.className = 'status success';
                    status.innerHTML = '✅ ' + data.message;
                } else {
                    status.className = 'status error';
                    status.innerHTML = '❌ Error: ' + data.message;
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = '❌ Network error: ' + error.message;
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""


@router.get("/seed", response_class=HTMLResponse)
async def seed_page():
    """Simple HTML page with seed button."""
    return HTML_PAGE
