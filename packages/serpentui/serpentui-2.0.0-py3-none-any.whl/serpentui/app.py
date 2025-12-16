import json
import threading
import webbrowser
from typing import Callable
from .base import Component

try:
    from flask import Flask
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask no instalado. Instala con: pip install flask")

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("⚠️  PyWebView no instalado. Instala con: pip install pywebview")


class SerpentApp:
    """Main SerpentUI Application Class with Flask + WebView"""
    
    def __init__(self, title: str = "SerpentUI App", theme: str = "dark", 
                 width: int = 1200, height: int = 800, resizable: bool = True):
        self.title = title
        self.theme = theme
        self.width = width
        self.height = height
        self.resizable = resizable
        self.root_component = None
        self.flask_app = None
        self.routes = {}
        
        if FLASK_AVAILABLE:
            self.flask_app = Flask(__name__)
            self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.flask_app.route('/')
        def index():
            return self._generate_html()
    
    def set_root(self, component: Component):
        """Set the root component of the application"""
        self.root_component = component
        return self
    
    def _generate_html(self) -> str:
        """Generate complete HTML"""
        if not self.root_component:
            raise ValueError("No root component set. Use app.set_root(component)")
        
        render_data = json.dumps({
            'title': self.title,
            'theme': self.theme,
            'component': self.root_component.to_dict()
        })
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@nextui-org/theme@latest/dist/styles.css">
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .terminal-container {{ background: #1e1e1e; border-radius: 8px; overflow: hidden; }}
        .terminal-header {{ background: #2d2d2d; padding: 10px 15px; display: flex; align-items: center; gap: 8px; }}
        .terminal-button {{ width: 12px; height: 12px; border-radius: 50%; }}
        .terminal-button.close {{ background: #ff5f56; }}
        .terminal-button.minimize {{ background: #ffbd2e; }}
        .terminal-button.maximize {{ background: #27c93f; }}
        .terminal-title {{ color: #fff; font-size: 12px; margin-left: 10px; }}
        .terminal-body {{ background: #1e1e1e; color: #00ff00; padding: 15px; font-family: 'Courier New', monospace; font-size: 14px; overflow-y: auto; }}
        .terminal-input {{ background: transparent; border: none; color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px; outline: none; width: 100%; }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const {{ useState }} = React;
        const appData = {render_data};
        
        const Terminal = ({{ title, height }}) => {{
            const [lines, setLines] = useState(['🐍 SerpentUI Terminal v2.0', 'Type "help" for available commands', '$ ']);
            const [input, setInput] = useState('');
            
            const handleCommand = (cmd) => {{
                const newLines = [...lines];
                newLines[newLines.length - 1] = '$ ' + cmd;
                
                if (cmd === 'help') {{
                    newLines.push('Available commands:', '  help   - Show this help', '  clear  - Clear terminal', '  date   - Show current date', '  echo   - Echo a message', '  about  - About SerpentUI');
                }} else if (cmd === 'clear') {{
                    setLines(['$ ']);
                    setInput('');
                    return;
                }} else if (cmd === 'date') {{
                    newLines.push(new Date().toString());
                }} else if (cmd === 'about') {{
                    newLines.push('🐍 SerpentUI v2.0', 'Modern Python UI Framework', 'Built with React + NextUI + Flask + WebView');
                }} else if (cmd.startsWith('echo ')) {{
                    newLines.push(cmd.substring(5));
                }} else if (cmd) {{
                    newLines.push(`Command not found: ${{cmd}}. Type "help" for available commands.`);
                }}
                
                newLines.push('$ ');
                setLines(newLines);
                setInput('');
            }};
            
            return (
                <div className="terminal-container" style={{{{ height }}}}>
                    <div className="terminal-header">
                        <div className="terminal-button close"></div>
                        <div className="terminal-button minimize"></div>
                        <div className="terminal-button maximize"></div>
                        <div className="terminal-title">{{title}}</div>
                    </div>
                    <div className="terminal-body" style={{{{ height: `calc(${{height}} - 40px)` }}}}>
                        {{lines.map((line, i) => (
                            <div key={{i}}>
                                {{i === lines.length - 1 ? (
                                    <div style={{{{ display: 'flex' }}}}>
                                        <span>{{line}}</span>
                                        <input
                                            className="terminal-input"
                                            value={{input}}
                                            onChange={{(e) => setInput(e.target.value)}}
                                            onKeyDown={{(e) => {{
                                                if (e.key === 'Enter') handleCommand(input);
                                            }}}}
                                            autoFocus
                                        />
                                    </div>
                                ) : line}}
                            </div>
                        ))}}
                    </div>
                </div>
            );
        }};
        
        const renderComponent = (comp) => {{
            if (typeof comp === 'string') return comp;
            const {{ type, props, children }} = comp;
            const renderedChildren = children?.map((child, i) => 
                React.createElement(React.Fragment, {{ key: i }}, 
                    typeof child === 'object' ? renderComponent(child) : child
                )
            );
            
            if (type === 'Terminal') return React.createElement(Terminal, props);
            return React.createElement(type, props, renderedChildren);
        }};
        
        const App = () => {{
            return <div className={{{{'dark': appData.theme === 'dark'}}}}> 
                {{renderComponent(appData.component)}}
            </div>;
        }};
        
        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>"""
    
    def run(self, mode: str = 'desktop', debug: bool = False, port: int = 5000):
        """
        Run the application
        
        Args:
            mode: 'desktop' (webview window), 'browser' (web browser), or 'server' (Flask only)
            debug: Enable Flask debug mode
            port: Flask server port
        """
        if not self.root_component:
            raise ValueError("No root component set. Use app.set_root(component)")
        
        if not FLASK_AVAILABLE:
            print("❌ Flask no está instalado. Instala con: pip install flask")
            return
        
        if mode == 'desktop':
            if not WEBVIEW_AVAILABLE:
                print("⚠️  PyWebView no disponible, abriendo en navegador...")
                mode = 'browser'
            else:
                # Correr Flask en thread separado
                threading.Thread(
                    target=lambda: self.flask_app.run(port=port, debug=False, use_reloader=False),
                    daemon=True
                ).start()
                
                # Dar tiempo a Flask para iniciar
                import time
                time.sleep(1)
                
                # Abrir ventana de webview
                print(f"\n🐍 SerpentUI v2.0 - Desktop App")
                print(f"📱 Título: {self.title}")
                print(f"🚀 Abriendo ventana...\n")
                
                webview.create_window(
                    self.title,
                    f'http://127.0.0.1:{port}',
                    width=self.width,
                    height=self.height,
                    resizable=self.resizable
                )
                webview.start()
                return
        
        if mode == 'browser':
            threading.Thread(
                target=lambda: self.flask_app.run(port=port, debug=debug, use_reloader=False),
                daemon=True
            ).start()
            
            import time
            time.sleep(1)
            
            print(f"\n🐍 SerpentUI v2.0 - Web App")
            print(f"🌐 Servidor: http://127.0.0.1:{port}")
            print(f"🚀 Abriendo navegador...\n")
            
            webbrowser.open(f'http://127.0.0.1:{port}')
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Aplicación cerrada")
        
        elif mode == 'server':
            print(f"\n🐍 SerpentUI v2.0 - Server Mode")
            print(f"🌐 Servidor: http://127.0.0.1:{port}\n")
            self.flask_app.run(port=port, debug=debug)
    
    def save_html(self, filename: str = "app.html"):
        """Save as standalone HTML file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self._generate_html())
        print(f"✓ Archivo guardado: {filename}")


def quick_app(ui_func: Callable, title: str = "SerpentUI App", theme: str = "dark", **kwargs):
    """
    Crear y ejecutar una app en una sola función
    """
    app = SerpentApp(title=title, theme=theme, **kwargs)
    app.set_root(ui_func())
    app.run()
